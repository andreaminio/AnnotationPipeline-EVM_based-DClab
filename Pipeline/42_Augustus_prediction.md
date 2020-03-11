4.2 - Augustus prediction
=========================

## 4.2.0 - Setup

### 4.2.0.1 - Define variables

`name` name of the genome.

`genome` genome fasta sequence.

### 4.2.0.2 - Set WD

```bash
cd 2-Annotation/2_2-Prediction/2_2_3-Prediction/2_2_3_2-Augustus/
```

### 4.2.0.3 - Set environment

```bash
mkdir 2_3_2-Augustus
cd 2_3_2-Augustus
mkdir fasta
mkdir gff3
mkdir logs

export PATH=/Tools/augustus-3.0.3/:$PATH
export AUGUSTUS_CONFIG_PATH=/Tools/augustus-3.0.3/config/

model=$name
```

4.2.1 - Predict
---------------

Split the genome sequences.

``` bash
awk 'BEGIN {getline; id=$1 ;gsub(">","",id); print id ;filename="fasta/"id".fasta"; print $0 >filename } { if ($1~"^>") {id=$1 ; sub(/>/,"",id); filename="fasta/"id".fasta"; print id};  print $0 > filename } END {print DONE}' < $genome | sed 's:^:fasta/:;s:$:.fasta:' > fasta_list
```

Run Augustus in parallel on multiple genomic sequences.

``` bash
parallel --gnu -j 10 "augustus  --species=${model} --singlestrand=true --gff3=on --outfile=gff3/{/.}.gff3 --noInFrameStop=true {} &> logs/{/.}.log" :::: fasta_list
```

Extract the results.

``` bash
for file in $(ls gff3 | grep "gff3$" | sed 's:^:gff3/:') ; do seq_name=$(basename $file .gff3); sed 's:sequence:Sequence:;s:seq:'"$seq_name"':g;s:=:='"$seq_name"'.:g;s:;Name=.*::' $file ; done | grep -v '^#' | sed 's:transcript:mRNA:;/codon/d;/intron/d'| sed '/CDS/ s:\(.*\)CDS\(.*\)ID=\(.*Parent=\)\(.*\):\1exon\2Parent=\4;ID=\4.exon\n\1CDS\2ID=\3\4:' | awk 'BEGIN {count=1; OFS="\t"} $3=="exon" {$0=$0count; count+=1} {print $0} ' > prediction.augustus.gff3

gffread -x prediction.augustus.CDS.fasta -g $genome prediction.augustus.gff3
```
