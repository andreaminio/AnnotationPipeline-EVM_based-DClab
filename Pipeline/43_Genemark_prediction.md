4.3 - Genemark prediction
=========================

## 4.3.0 - Setup

### 4.3.0.1 - Define variables

`name` name of the genome.

`genome` genome fasta sequence.

### 4.3.0.2 - Set WD

```bash
cd 2-Annotation/2_2-Prediction/2_2_3-Prediction/2_2_3_3-Genemark/
```

### 4.3.0.3 - Set environment

```bash
mkdir 2_3_3-Genemark
cd 2_3_3-Genemark

ln -s ../2_2_3_2-Augustus/fasta
ln -s ../2_2_3_2-Augustus/fasta_list
mkdir gff3
mkdir logs
model=../../../2_1-Training/2_1_2-Predictor_training/2_1_2_2-Genemark/${name}.genemark.mod
```

4.3.1 - Predict
---------------

Run Genemark in parallel on multiple genomic sequences.

``` bash
parallel --gnu -j 10 "gmhmme3 -m $model -o gff3/{/.}.gff3 -b logs/{/.}.stats -f gff3 {}" :::: fasta_list  
```

Extract the results.

``` bash
for file in $(ls gff3 | grep "gff3$" | sed 's:^:gff3/:') ; do seq_name=$(basename $file .gff3); sed 's:sequence:Sequence:;s:seq:'"$seq_name"':g;s:=:='"$seq_name"'.:g;s:;Name=.*::' $file ; done | grep -v '^#' | sed 's:transcript:mRNA:;/codon/d;/Intron/d'| sed '/CDS/ s:\(.*\)CDS\(.*\)ID=\(.*Parent=\)\(.*\):\1exon\2Parent=\4;ID=\4.exon\n\1CDS\2ID=\3\4:' | awk 'BEGIN {count=1; OFS="\t"} $3=="exon" {$0=$0count; count+=1} {print $0} ' > prediction.genemark.gff3

gffread -x prediction.genemark.CDS.fasta -g $genome prediction.genemark.gff3
```
