# Generated by Django 2.2 on 2020-04-16 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserInput',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('msa', models.TextField()),
                ('msa_file', models.FileField(upload_to='')),
                ('min_primer_length', models.IntegerField()),
                ('max_primer_length', models.IntegerField()),
                ('na_conc', models.FloatField()),
                ('amplicon_lower', models.IntegerField()),
                ('amplicon_upper', models.IntegerField()),
                ('max_degeneracy', models.IntegerField()),
                ('min_melting_temp', models.FloatField()),
                ('max_melting_temp', models.FloatField()),
                ('min_gc', models.FloatField()),
                ('max_gc', models.FloatField()),
                ('select_gc_clamp', models.BooleanField()),
                ('omit_gc_clamp', models.BooleanField()),
                ('max_edit_distance', models.IntegerField()),
                ('outgroup', models.TextField()),
                ('outgroup_file', models.FileField(upload_to='')),
            ],
        ),
    ]
