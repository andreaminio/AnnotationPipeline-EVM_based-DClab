3.1 - Augustus training
=======================

## 3.1.0 - Setup

### 3.1.0.1 - Define variables

`name` name of the genome.

`genome` genome fasta sequence.

### 3.1.0.2 - Set WD

```bash
cd 2-Annotation/2_1-Training/2_1_2-Predictor_training/2_1_2_1-Augustus/
```

### 3.1.0.3 - Set environment

```bash
export PATH=/DATA7/Resources/Tools/augustus-3.0.3/bin/:/DATA7/Resources/Tools/augustus-3.0.3/:$PATH
export AUGUSTUS_CONFIG_PATH=/DATA7/Resources/Tools/augustus-3.0.3/config/
```

3.1.1 - Training
----------------

Convert training set models annotation to genebank format.

``` bash
gff2gbSmallDNA.pl ../../2_1_2-Training_set/$name.gene_models.gff3 $genome 300 $name.gene_models.augustus_genebank.gb
```

Run the training.

``` bash
autoAugTrain.pl --verbose --trainingset $name.gene_models.augustus_genebank.gb --genome $genome --species $name --optrounds 5 --CRF > augustus.train.log 2> augustus.train.err
```

Save a copy of the model in the local directory as by default is stored in Augustus database.

``` bash
rsync -av /DATA7/Resources/Tools/augustus-3.0.3/config/species/$name .
```
