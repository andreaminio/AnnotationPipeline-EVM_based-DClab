4.4 - SNAP prediction
=====================

## 4.4.0 - Setup

### 4.4.0.1 - Define variables

`name` name of the genome.

`genome` genome fasta sequence.

### 4.4.0.2 - Set WD

```bash
cd 2-Annotation/2_2-Prediction/2_2_3-Prediction/2_2_3_4-SNAP/
```

### 4.4.0.3 - Set environment

```bash
mkdir 2_3_4-SNAP
cd 2_3_4-SNAP

model=../../../2_1-Training/2_1_2-Predictor_training/2_1_2_3-SNAP/${name}.SNAP.hmm
```

4.4.1 - Predict
---------------

Run SNAP.

``` bash
/Tools/snap/snap -tx prediction.snap.CDS.fasta $model $genome > prediction.snap.txt 2> err 
```

Extract the results.

``` bash
/Tools/snap/zff2gff3.pl prediction.snap.txt | gffread -E --force-exons -O -F -o - | sed '1,1d;s:-snap\.:-snap.t:' | sed '/mRNA/ s:\(.*\)mRNA\(.*ID=\)\(.*\)\.t\([0-9]*\)$:\1gene\2\3.g\4\n\1mRNA\2\3.t\4;Parent=\3.g\4:;/CDS/ s/\(.*Parent=\)\(.*\)/\1\2;ID=\2.cds./;/exon/ s/\(.*Parent=\)\(.*\)/\1\2;ID=\2.exon./' | awk '{if ($3=="exon" || $3=="CDS" ) {print $0NR} else {print $0}   } ' > prediction.snap.gff3
```
