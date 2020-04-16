from django.db import models

#TODO defaults
class UserInput(models.Model):
    msa = models.TextField()
    msa_file = models.FileField()
    min_primer_length = models.IntegerField()
    max_primer_length = models.IntegerField()
    na_conc = models.FloatField()

    amplicon_lower = models.IntegerField()
    amplicon_upper = models.IntegerField()
    max_degeneracy = models.IntegerField()
    #TODO min and max inputs
    min_melting_temp = models.FloatField()
    max_melting_temp = models.FloatField()
    min_gc = models.FloatField()
    max_gc = models.FloatField()
    # # # # # # # # # # # # #
    select_gc_clamp = models.BooleanField()
    omit_gc_clamp = models.BooleanField()
    max_edit_distance = models.IntegerField()
    outgroup = models.TextField()
    outgroup_file = models.FileField()
