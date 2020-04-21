from scipy.signal import find_peaks
from scipy.stats import entropy
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from Bio import SeqIO, AlignIO, Seq
import itertools as it
from math import log
from collections import Counter
import Levenshtein as Lev
import tempfile

class SequenceAlignment():
    def __init__(self, fasta_file):
        self.data = self._fasta_to_df(fasta_file)

    def _charwise_split(self, word):
        return [char for char in word]

    def _fasta_to_df(self,file):
        fasta = SeqIO.parse(file, "fasta")
        sample_data = []
        for seq in fasta:
            c = self._charwise_split(seq.seq)
            sample_data.append(c)
        return pd.DataFrame(sample_data)




class Primer():
    def __init__(self, seq, pos, na_conc=None):
        self.seq = seq
        self.pos = pos
        self.na_conc = na_conc
        self.length = len(seq)
        self.degeneracy = self._count_degeneracy(seq)

        min_gc, max_gc = self._get_gc_minmax(seq)
        self.melting_temps = self._get_melting_temp(min_gc, max_gc, na_conc)
        self.gc = self._get_gc_percent(min_gc, max_gc)

        self.good_gc_clamp = False
        self.bad_gc_clamp = False
        self._check_gc_clamps(seq)

    def _get_melting_temp(self, min_gc, max_gc, na_conc):
        min_seq = Counter(min_gc)
        max_seq = Counter(max_gc)
        if na_conc:
            min_temp = (
            (min_seq['A'] + min_seq['T'])*2 + (min_seq['G'] + min_seq['C'])*4
                - 16.6*log(0.05, 10) + 16.6*log(na_conc, 10)
            )
            max_temp = (
            (max_seq['A'] + max_seq['T'])*2 + (max_seq['G'] + max_seq['C'])*4
                - 16.6*log(0.05, 10) + 16.6*log(na_conc, 10)
            )
        #IF no [Na+], use basic measure.
        else:
            min_temp = (
            64.9 + 41*(min_seq['G']+min_seq['C']-16.4)/(len(seq))
            )
            max_temp = (
            64.9 + 41*(max_seq['G']+max_seq['C']-16.4)/(len(seq))
            )
        return((min_temp, max_temp))

    def _count_degeneracy(self,seq):
        deg = 0
        one_deg = set(['R', 'M', 'W', 'S', 'K', 'Y'])
        two_deg = set(['V', 'D', 'H', 'B'])
        three_deg = set(['N'])
        for char in seq:
            if char in one_deg:
                deg += 1
            elif char in two_deg:
                deg += 2
            elif char in three_deg:
                deg += 3
        return deg

    def _get_gc_percent(self, min_gc, max_gc):
        min_chars = Counter(min_gc)
        max_chars = Counter(max_gc)
        min_gc_perc = (min_chars['C'] + min_chars['G'])/len(min_gc)
        max_gc_perc = (max_chars['C'] + max_chars['G'])/len(max_gc)
        return (min_gc_perc, max_gc_perc)

    #function accepts degenerate primers and returns the primer with highest and lowest GC content.
    # Lower bound will also be most likely to have poly-A
    def _get_gc_minmax(self, seq):
        # To find minimum Temp:
        # Choose A>T>C>G
        min_map = {
            "A": "A",
            "G": "G",
            "C": "C",
            "T": "T",
            "R": "A",
            "M": "A",
            "W": "A",
            "S": "C",
            "K": "T",
            "Y": "T",
            "V": "A",
            "D": "A",
            "H": "A",
            "B": "T",
            "N": "A",
        }
        max_map = {
            "A":"A",
            "G":"G",
            "C":"C",
            "T":"T",
            "R":"G",
            "M":"C",
            "W":"A",
            "S":"G",
            "K":"G",
            "Y":"C",
            "V":"G",
            "D":"G",
            "H":"C",
            "B":"G",
            "N":"G",
        }
        min_seq = "".join([min_map[char] for char in seq])
        max_seq = "".join([max_map[char] for char in seq])
        return(min_seq, max_seq)

    #Ideally, the last 5 bases of the 3' end will have 1-2 G's or C's.
    def _check_gc_clamps(self, seq):
        counts = Counter(seq[-5:])
        # the symbol S represents G or C.
        gc = counts['G'] + counts['C'] + counts['S']
        # Return true if ALL expanded primers meet the good criteria
        if gc == 1 or gc == 2:
            self.good_gc_clamp = True
        #return true if ANY of the expanded primers meet the bad criteria
        if gc > 3:
            self.bad_gc_clamp = True


    def expand_sequence(self):
        d = Seq.IUPAC.IUPACData.ambiguous_dna_values
        return  list(map("".join, it.product(*map(d.get, self.seq))))

    def __str__(self):
        return self.seq


class PrimerPair():
    def __init__(self, forward, reverse):
        self.forward = forward
        self.reverse = reverse
        self.amplicon_length = self._get_amp_len(forward, reverse)

    def _get_amp_len(self, forward, reverse):
        start = forward.pos + forward.length
        end = reverse.pos
        return end - start

    def __str__(self):
        out ="""Forward:
    Seq: {0}
    Tm range: {1} - {2}
    Degeneracy: {3}
    GC% range: {4} - {5}
Reverse:
    Seq: {6}
    Tm range: {7} - {8}
    Degeneracy: {9}
    GC% range: {10} - {11}""".format(self.forward.seq,
                                  self.forward.melting_temps[0],
                                  self.forward.melting_temps[1],
                                  self.forward.degeneracy,
                                  self.forward.gc[0],
                                  self.forward.gc[1],
                                  self.reverse.seq,
                                  self.reverse.melting_temps[0],
                                  self.reverse.melting_temps[1],
                                  self.reverse.degeneracy,
                                  self.reverse.gc[0],
                                  self.reverse.gc[1])
        return out


class PrimerFinder():
    def _alignment_to_string(self, alignment):
        nuc_code_converter = {
        "A"   :"A",
        "G"   :"G",
        "C"   :"C",
        "T"   :"T",
        "AG"  :"R",
        "AC"  :"M",
        "AT"  :"W",
        "CG"  :"S",
        "GT"  :"K",
        "CT"  :"Y",
        "ACG" :"V",
        "AGT" :"D",
        "ACT" :"H",
        "CGT" :"B",
        "ACGT":"N"
        }

        out = ""
        for i in alignment:
            out += nuc_code_converter["".join(sorted(list(set(alignment[i]))))]
        return out

    def _kmer_entropy(self, df, k):
        #have to remove columns with NaN.
        start = 0
        end = k
        entropies = {}
        while end < len(df.columns):
            window = df.loc[:, start:end]
            #Stop if missing values are encountered
            if window.isnull().values.any():
                break
            #don't use primers over gaps
            if (window=='-').values.any():
                start += 1
                end += 1
                continue
            kmers = []
            primer_string = self._alignment_to_string(window)
            for entry in window.values:
                kmers.append("".join(entry))
            kmer_counts = pd.DataFrame(data=kmers).apply(pd.value_counts)
            kmer_probs = kmer_counts/kmer_counts.sum()
            entr = entropy(kmer_probs)
            entropies[start] = (entr, primer_string)

            start += 1
            end += 1

        return entropies

    def _find_min_entropy_positions(self, entropies, show_plot=False):
        #ent_vals = np.asarray([i[0] for i in entropies]).flatten()
        ent_vals = np.asarray([i[1][0] for i in entropies.items()]).flatten()
        peaks, _ = find_peaks(ent_vals * -1)
        if show_plot:
            plt.plot(ent_vals)
            plt.plot(peaks, ent_vals[peaks], "x")
            plt.show()
        #return peaks
        ent_inds = np.asarray([i[0] for i in entropies.items()]).flatten()
        return ent_inds[peaks]

    def _outgroup_distance(self,primer, outgroup):
        k = primer.length
        min_dist = 10000 #the min distance will always be less than this
        for seq in primer.expand_sequence():
            i = 0
            while i < len(outgroup)-k:
                window = outgroup[i:i+k]
                dist = Lev.distance(seq, window)
                if dist < min_dist:
                    min_dist = dist
                i += 1
        return(min_dist)


    def identify_primers(self, filename, min_primer_length, max_primer_length, na_conc=None):
        sequence_alignment = SequenceAlignment(filename)
        primers = []
        for k in range(min_primer_length, max_primer_length):
            entropy_peaks = self._kmer_entropy(sequence_alignment.data, k)
            primer_indices = self._find_min_entropy_positions(entropy_peaks, show_plot=False)
            for i in primer_indices:
                primer = Primer(seq=entropy_peaks[i][1], pos=i, na_conc=na_conc)
                primers.append(primer)
        return primers

    def identify_pairs(self, primers,
                       amp_min=75, amp_max=150,
                       max_degeneracy=2,
                       min_melting_temp = 52,
                       max_melting_temp = 58,
                       min_gc = .40,
                       max_gc = .60,
                       select_gc_clamp=True,
                       omit_gc_clamp=True,
                       max_edit_dist=2, outgroup=None):
        #First, filter on attributes.
        filtered = list(filter(lambda primer: primer.degeneracy <= max_degeneracy
                  and primer.melting_temps[1] <= max_melting_temp
                  and primer.melting_temps[0] >= min_melting_temp
                  and primer.gc[0] >= min_gc
                  and primer.gc[1] <= max_gc, primers))

        if select_gc_clamp:
            filtered = list(filter(lambda primer: primer.good_gc_clamp==True, filtered))
        if omit_gc_clamp:
            filtered = list(filter(lambda primer: primer.bad_gc_clamp == False, filtered))

        pairs = []
        for pair in it.combinations(filtered, 2):
            l = pair[1].pos - pair[0].pos - pair[0].length
            if l <= amp_max and l >= amp_min:
                primerPair = PrimerPair(pair[0], pair[1])
                pairs.append(primerPair)

        #Outgroup Filtering should happen on at least ONE primer of the pairs.
        #Only one primer need be specific. off-target DNA will be titred out
        if outgroup:
            selected = []
            outseqs = [str(x.seq) for x in SeqIO.parse(outgroup, "fasta")]
            for pair in pairs:
                f_dist = 10000
                r_dist = 10000
                for seq in outseqs:
                    f_current = self._outgroup_distance(pair.forward, seq)
                    r_current = self._outgroup_distance(pair.reverse, seq)
                    if f_current < f_dist:
                        f_dist = f_current
                    if r_current < r_dist:
                        r_dist = r_current
                if f_dist < max_edit_dist or r_dist < max_edit_dist:
                    selected.append(pair)
            pairs = selected

        return pairs
