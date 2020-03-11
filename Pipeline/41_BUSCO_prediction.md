4.1 - BUSCO prediction
======================

## 4.1.0 - Setup

### 4.1.0.1 - Define variables

`n_cores` number of cores.

`genome` genome fasta sequence.

`name` name of the genome.

### 4.1.0.2 - Set WD

```bash
cd 2-Annotation/2_2-Prediction/2_2_3-Prediction/2_2_3_1-BUSCO/
```

### 4.1.0.3 - Set environment

```bash
mkdir 2_3_1-BUSCO 
cd 2_3_1-BUSCO

export PATH=/Tools/augustus-3.0.3/:$PATH
export AUGUSTUS_CONFIG_PATH=/Tools/augustus-3.0.3/config/
```

4.1.1 - Predict
---------------

Run BUSCO on genome.

``` bash
python run_BUSCO.py -i $genome  -o genome -l /Tools/busco/db/embryophyta_odb9/ -m genome -c $n_cores
```

Extract Augustus predictions on BUSCO gene models.

``` bash
for file in run_genome/augustus_output/predicted_genes/* ; do name=$(basename $file) ; cat $file | grep -v '^#' | grep -v "protein_match"| grep -v 'tss' | grep -v "codon" |grep -v tts|  grep -v intron | sed '/gene/ s:\(.*\)\(\tAUGUSTUS.*gene.*\)\t\(g.*\):\1\2\tID=\1.'"$name"'.\3: ; /transcript/ s:\(.*\)\tAUGUSTUS\ttranscript\(.*\)\t\(g.*\)\(\.t.*\):\1\tAUGUSTUS\tmRNA\2\tID=\1.'"$name"'.\3\4;Parent=\1.'"$name"'.\3: ; /exon/ s:\(.*\)\(\tAUGUSTUS.*\)transcript_id \"\(.*\)\"; gene_id "\(.*\)";$:\1\2Parent=\1.'"$name"'.\3;ID=\1.'"$name"'.\3.exon.:; /CDS/ s:\(.*\)\(\tAUGUSTUS.*\)transcript_id \"\(.*\)\"; gene_id "\(.*\)";$:\1\2Parent=\1.'"$name"'.\3;ID=\1.'"$name"'.\3.cds.:' | awk '{if ($3=="CDS" || $3=="exon") {print $0NR} else {print $0} } '; done > augustus.on_busco.predictions.gff3

gffread -E --force-exons -O -F -o - augustus.on_busco.predictions.gff3 | sed '1,1d;/CDS/ s/\(.*Parent=\)\(.*\)/\1\2;ID=\2.cds./;/exon/ s/\(.*Parent=\)\(.*\)/\1\2;ID=\2.exon./' | awk '{if ($3=="exon" || $3=="CDS" ) {print $0NR} else {print $0}   } ' | sed 's:AUGUSTUS:augustus_BUSCOv3:' >  prediction.busco.gff3

gffread -x prediction.busco.CDS.fasta -g $genome   prediction.busco.gff3
```
