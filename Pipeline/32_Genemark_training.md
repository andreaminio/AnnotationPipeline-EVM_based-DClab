3.2 - Genemark training
=======================

## 3.2.0 - Setup

### 3.2.0.1 - Define variables

`name` name of the genome.

`n_cores` number of cores.

### 3.2.0.2 - Set WD

```bash
cd 2-Annotation/2_1-Training/2_1_2-Predictor_training/2_1_2_2-Genemark/
```

3.2.1 - Training
----------------

Extract intron annotation only for the training set models.

``` bash
awk '$3=="intron"' ../../2_1_2-Training_set/${name}.gene_models.gff3 > ${name}.gene_models.introns.gff3
```

Run the prediction.

``` bash
gmes_petap.pl --sequence $genome --ET ${name}.gene_models.introns.gff3 --training --cores $n_cores --v --max_intergenic 1000000 --max_intron 20000 > genemark.train.log 2>genemark.train.err 
```

Rename the prediction results.

``` bash
rsync -L run/ET_C.mod ../

mv ../ET_C.mod ${name}.genemark.mod
```

