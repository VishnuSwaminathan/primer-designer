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
import csv
import os
#import cProfilelog
import matplotlib, random
import plotly.graph_objects as go
from plotly.io._html import to_html

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
    def __init__(self, seq, pos, na_conc=None, entropy=0, entropy_peak=0):
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
        
        self.entropy=entropy
        self.entropy_peak=entropy_peak 
        

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
    
    ######################
    def __init__(self):
       self.entropy_values = None
       self.entropy_peaks = None
       self.primer_pairs = None
       self.sequence_alignment = None
   ######################
        
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
    
    
#- put each sequence of the input sequence alignment into a dataframe (kind of like a table or matrix)
#- remove any positions in the alignment with null values from considetation
#- make an empty list 
#- start at the first position of the alignment
#-  slide a window of size primer_length down the alignment
#- for each position of the sliding window, calculate the entropy at that position using the scipy entropy function
#- save those values to the list
#- return the list
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
                
                ######################
                entropies[start]= (None, None)
                ######################
                
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
        #print("Entropies: ")
        #print(entropies)
        return entropies

    #def _kmer_entropy_export(self, entropies):
       

    def _find_min_entropy_positions(self, entropies, show_plot=False):
        
        ######################
        #ent_vals = np.asarray([i[1][0] for i in entropies.items()]).flatten()
        ent_vals = np.asarray([i[1][0] for i in entropies.items()], dtype=np.float64).flatten()

        # lambda expression allows * -1 over np array with None values, whcih otherwise throws type error
        ######################
        
        peaks, _ = find_peaks(ent_vals * -1)
        
        ######################
        #if show_plot:
            #plt.plot(ent_vals)
            #plt.plot(peaks, ent_vals[peaks], "x")
            #plt.show()
        
        # peaks, _ = find_peaks(np.array(list(map((lambda i: -1*i if i!=None else i), ent_vals))))
        ###
        self.entropy_values = ent_vals
        self.entropy_peaks = peaks
        ###
        ######################
        
        #return peaks
        #print("Entropy Peaks: ")
        #print(peaks)
        ent_inds = np.asarray([i[0] for i in entropies.items()]).flatten()
        #if os.path.exists('entropy_diagram.csv'):
            #modifyFile = 'a'
        #else:
            #modifyFile = 'w'
        #modifyFile = 'w'
        #script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
        #rel_path = "templates\\entropy\\entropy_diagram.csv"
        #abs_file_path = os.path.join(script_dir, rel_path)
        #with open(abs_file_path, mode=modifyFile) as entropy_file:
           #entropy_writer = csv.writer(entropy_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
           #for i in ent_inds[peaks]:
               #entropy_writer.writerow([entropies[i][0]])
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
        
        ######################
        self.sequence_alignment=sequence_alignment
        ######################
        
        primers = []
        for k in range(min_primer_length, max_primer_length):
            entropy_peaks = self._kmer_entropy(sequence_alignment.data, k)
            
            ######################
            #primer_indices = self._find_min_entropy_positions(entropy_peaks, show_plot=False)
            ######################
            
            #print("Entropy Peaks (i.e. _kmer_entropy): ",k)
            #print(entropy_peaks)
            #print("Entropy Primer Indices (i.e. _find_min_entropy_positions): ",k)
            #print(primer_indices)
            
            ######################
            primer_indices = self._find_min_entropy_positions(entropy_peaks, show_plot=True)
            ######################
            
            for i in primer_indices:
                #print(entropy_peaks[i][1],'\n')
                #print('i:',i,' ','entropy_peaks: ',entropy_peaks[i][0],'\n')
                primer = Primer(seq=entropy_peaks[i][1], pos=i, na_conc=na_conc)
                primers.append(primer)
            #print('\n','\n')
        #print(primers)
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
        
        ######################
        print("amp_min ", amp_min)
        print("amp_max ", amp_max)
        print('max deg ', max_degeneracy)
        print('min_melting_temp ', min_melting_temp)
        print('max_melting_temp', max_melting_temp)
        print("MIN GC: ", min_gc)
        print("MAX GC: ", max_gc)
        ######################
        
        
        filtered = list(filter(lambda primer: primer.degeneracy <= max_degeneracy
                  and primer.melting_temps[1] <= max_melting_temp
                  and primer.melting_temps[0] >= min_melting_temp
                  and primer.gc[0] >= min_gc
                  and primer.gc[1] <= max_gc, primers))

        ######################
        for p in filtered:
            print(p)
        ######################

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
                    #pair.forward & pair.reverse for primer pairs
                    f_current = self._outgroup_distance(pair.forward, seq)
                    r_current = self._outgroup_distance(pair.reverse, seq)
                    if f_current < f_dist:
                        f_dist = f_current
                    if r_current < r_dist:
                        r_dist = r_current
                if f_dist < max_edit_dist or r_dist < max_edit_dist:
                    selected.append(pair)
            pairs = selected
            
        ######################
            ###
            self.primer_pairs = pairs
            ###
        if len(pairs) == 0:
            pairs = -1
        ######################    
            
        return pairs

    ######################
    
    def saveCSV(self):
        modifyFile = 'w'
        script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
        rel_path = "templates\\entropy\\entropy_output.csv"
        abs_file_path = os.path.join(script_dir, rel_path)
        with open(abs_file_path, mode=modifyFile, newline='') as entropy_file:
            fieldnames = ['Sequence', 'Entropy']
            entropy_writer = csv.DictWriter(entropy_file, fieldnames=fieldnames)
            for i, val in enumerate(self.entropy_values):
               entropy_writer.writeheader()
               entropy_writer.writerow({'Sequence': i, 'Entropy':val})
    ######################
    def html_plot(self):
         #if os.path.exists('entropy_diagram.csv'):
            #modifyFile = 'a'
        #else:
            #modifyFile = 'w'
        #modifyFile = 'w'
        #script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
        #rel_path = "templates\\entropy\\entropyTxt.txt"
        #abs_file_path = os.path.join(script_dir, rel_path)
        #with open(abs_file_path, mode=modifyFile) as entropy_file:
           #entropy_writer = csv.writer(entropy_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
           #for i in ent_inds[peaks]:
               #entropy_writer.writerow([entropies[i][0]])
        #entropyTxt=open(abs_file_path, mode=modifyFile)
        
        ######################
        #get primer_pairs
        assert self.primer_pairs
        #y axis is entropy values (MINIMUM entropy values), get's values from function "_find_min_entropy_positions"
        y = self.entropy_values
        #print('Min Entropy Values (y): ',*y,sep=", ")
        #print('\n','\n')
        #np.arrange => Return evenly spaced values within a given interval
        #"len(y)" => Return number of items in an object
        #So x = array with intervals for each entropy value
        x = np.arange(len(y))
       # print('Array of Evenly Intervaled Min. Entropy Values (x=', x, '): ',*y,sep=", ")
        #print('\n','\n')
    
        #np.array creates an array
        #dtype => desired output type for the array, so here it's numpy float64
        #y_nans => array of min. entropy values (y) of type 64bit float (np.float64)
        y_nans = np.array(y, dtype=np.float64)
        #print('Array of min. entropy values of type float (y_nans): ',*y_nans,sep=", ")
        #print('\n','\n')
            
        ######################
        xy={}
        for key in x:
            for value in y:
                xy[key]=value
        xAndY={'X': [x], 'Y': [y]}
        #csvDF=pd.DataFrame.from_dict(xy)
        #print('x: ',type(x))
        #print('x: ',type(y_nans))
        x2 = np.array(x).tolist()
        y2 = np.array(y_nans).tolist()
        #print('\n','\n')
        #print('x2: ',type(x2))
        #print('y2: ',type(y2))
        
        csvDF=pd.DataFrame(y_nans)
        #csvDF=pd.DataFrame(x, y_nans, index=x)
        #csvDF.out
        csvDF.to_csv('entropy-out.csv')
        ######################
        
        #np.nanmax Returns max of an array...or min along an axis. Ignores any NaNs!
        #primer_height => Max value of the y_nans, divided by 5
        primer_height = np.nanmax(y_nans)/5
        #print('Max value from Array of Min. Entropy values, divided by 5 (primer_height): ',primer_height)
        #print('\n','\n')
        #primer_y => 
        primer_y = np.nanmax(y_nans) + primer_height
        #print('6/5*np.nanmax(y_nans) => (primer_y = np.nanmax(y_nans) + primer_height): ',primer_y)
        #print('\n','\n')

        #go == plotly graph_objects
        #go.figure => Create a figure, specificly here "Graph Objects"; this provides precise data validation, and can render/export graphs
        fig = go.Figure()
        #fig.add_trace => modifies graph property...here, the func accepts a graph object trace (instance of Scatter), and adds to figure
        #x=array with intervals for each entropy val, y=min entropy values
        fig.add_trace(go.Scatter(x=x, y=y,
                                 mode='lines',
                                 name='Seq. Entropy'))
        #Basically sets the min points of entropy=good for us, what we want tof ind
        fig.add_trace(go.Scatter(x=self.entropy_peaks,
                                 y=y[self.entropy_peaks],
                                 mode='markers',
                                 name='Entropy Minima'))


        def f(x):
            if x=='-':
                return None
            else:
                return 1
            
        #print('\n','\n')
        df = self.sequence_alignment.data.applymap(f)
        df = df.where(pd.notnull(df), None)
        #print("df: ","\n",df)

        #print('\n','\n')
        df = df.where(pd.notnull(df), None)
        for i, row in df.iterrows():
            y = [(d - (i+1.1))/7 if d else None for d in row.values]
            #print("y value @ i=",i," in df.iterrows (and before fig.add_trace): ", y,"\n")
            fig.add_trace(go.Scatter(
                x=x,
                y=y,
                #orientation='h',
                mode='lines',
                showlegend=False,
            ))
            #print('\n')

        #print('\n','\n')
        #min and max vals used for colormap
        f_min = min([p.forward.pos for p in self.primer_pairs ])
        #print("f_min for colormap values: ", f_min)
        f_max = max([p.forward.pos for p in self.primer_pairs ])
        #print("f_max for colormap values: ", f_max)

        #print('\n','\n')
        norm = matplotlib.colors.Normalize(vmin=f_min, vmax=f_max)
        cmap = matplotlib.cm.get_cmap('GnBu')
        cmap_r = matplotlib.cm.get_cmap('GnBu_r')

        i = 1
        hex_colors_dic = {}
        rgb_colors_dic = {}
        hex_colors_only = []
        for name, hex in matplotlib.colors.cnames.items():
            hex_colors_only.append(hex)
            hex_colors_dic[name] = hex
            rgb_colors_dic[name] = matplotlib.colors.to_rgb(hex)

        for pair in self.primer_pairs:
            f = pair.forward
            r = pair.reverse

            #all primers have same y
            y = [primer_y, primer_y+primer_height, primer_y+primer_height, primer_y, primer_y]

            #color = matplotlib.colors.to_hex(cmap(norm(f.pos)))
            color = random.choice(hex_colors_only)
            anchor_color = random.choice(hex_colors_only)

            #forward primer
            fig.add_trace(go.Scatter(x=[f.pos, f.pos, f.pos+f.length, f.pos+f.length, f.pos],
                                    y= y,
                                    fill='toself',
                                    text = str(f),
                                    line=dict(
                                    color=color,
                                    width=2),
                                    fillcolor=color,
                                    showlegend=False,))
            #reverse primer
            fig.add_trace(go.Scatter(x=[r.pos, r.pos, r.pos+r.length, r.pos+r.length, r.pos],
                                    y = y,
                                    fill='toself',
                                    text = str(r),
                                    line=dict(
                                    color=color,
                                    width=2),
                                    fillcolor=color,
                                    showlegend=False,))
            fig.add_trace(go.Scatter(x=np.arange((f.pos+f.pos+f.length)/2, (r.pos+r.pos+r.length)/2),
                                     y = [(primer_y + primer_y + primer_height)/2] * x.shape[0],
                                     line=dict(color=anchor_color, width=4, dash='dash'),
                                     text=str(pair),
                                     name="Pair {0}".format(i),

                         ))
            i +=1



        #fig.show()
        return to_html(fig, full_html=False)
    ######################