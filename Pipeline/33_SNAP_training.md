3.3 - SNAP training
===================

## 3.3.0 - Setup

### 3.3.0.1 - Define variables

`name` name of the genome.

`genome` genome fasta sequence.

### 3.3.0.2 - Set WD

```bash
cd 2-Annotation/2_1-Training/2_1_2-Predictor_training/2_1_2_3-SNAP/
```

### 3.3.0.3 - Set files

```bash
mkdir -p prep && cd prep

cat <(cat ../../../2_1_2-Training_set/$name.gene_models.gff3 ; echo "#FASTA" ; cat $genome) > $name.gene_models.SNAP_tset.gff3
```

3.3.1 - Training
----------------

Convert GFF3 to ZFF format and correct input files.

``` bash
maker2zff -n $name.gene_models.SNAP_tset.gff3 2> /dev/null

rm -rf genome.dna

for id in $(grep '^>' genome.ann | sed 's:>::'); do echo $id; getFastaFromIds.py <(echo $id) $genome | sed 's/.\{60\}/&\n/g' >> genome.dna ; done
```

Run prediction steps.

``` bash
fathom genome.ann genome.dna -gene-stats -errors-ok > stats

fathom genome.ann genome.dna -categorize 1000

fathom genome.ann genome.dna -errors-ok -export 1000 -plus

mkdir -p ../params && cd ../params

/DATA7/Resources/Tools/snap/forge ../prep/export.ann ../prep/export.dna 

mkdir -p ../model && cd ../model

/DATA7/Resources/Tools/snap/hmm-assembler.pl $name ../params > $name.SNAP.hmm
```

Copy and rename the model file.

``` bash
cd ..

cp model/$name.SNAP.hmm .
```
