9 - Functional annotation
=========================

## 9.0 - Setup

### 9.0.1 - Define variables

`genome` genome fasta sequence.

`name` name of the genome.

### 9.0.2 - Set WD

```bash
cd 2-Annotation/2_2-Prediction/2_2_9-Functional_annotation/
```

## 9.1 - Annotate

Generate final annotation file, fasta files and statistics.

``` bash
python /Scripts/GFF_extract_features.py -g $genome -a ${name}.gff3 -p ${name} -o > log 2> err
```

Setup.

``` bash
mkdir fasta
mkdir blast
mkdir interpro

awk 'BEGIN {getline; id=$1 ;gsub(">","",id); print id ;filename="fasta/"id".fasta"; print $0 >filename } { if ($1~"^>") {id=$1 ; sub(/>/,"",id); filename="fasta/"id".fasta"; print id};  print $0 > filename }' ${name}.protein.fasta >> ../blast_commands.sh

find fasta/ -type f -name "*.fasta" -exec sed -i 's:\.$::;s:\*$::' {} \;
```

Generate commands.

``` bash
cp blast_commands.sh interpro_commands.sh

sed -i 's:\(.*\):blastp -num_threads 6 -db RefSeq_Plants.protein.faa -show_gis -outfmt 5 -query fasta/\1.fasta > blast/\1.xml:' blast_commands.sh 

sed -i 's:\(.*\):\/Tools/interproscan-5.28-67.0/interproscan.sh --goterms -f XML,gff3 -i fasta/\1.fasta -b interpro/\1:' interpro_commands.sh
```

Run in parallel blast and interpro commands.

``` bash
parallel -j 8 :::: blast_commands.sh > blast.log
parallel -j 8 :::: interpro_commands.sh > interpro.log
```

``` bash
find blast | grep 'xml$' | sort | sed 's:\(.*\):python /Scripts/mapGOs.py -m refseq2go.txt \1 > \1.tab' > GOcommand.sh

parallel -j 8 :::: GOcommand.sh > GOcommand.log

for file in $(find blast -type f -name "*tab" | sort );  do echo $file ; awk -F "\t" 'BEGIN {OFS="\t"; OFS="\t"; print "Query","Q_len","Q_start","Q_stop","|","Target","T_len","T_start","T_stop","|","e-value","Matches","Mismatches","Gaps","Iden","Q_cov","T_cov","|","Description","|","GO"} {print $1,$23,$7,$8,"|",$2,$24,$9,$10,"|",$11,$4,$5,$6,$3,100*($4/$23),100*($4/$24),"|",$25,"|",$26}' $file > ${file}.txt ; done

for file in $(find blast -type f -name "*tab.txt" | sort ); do awk -F "\t" '$15>50 && $16>50 && $17>50' $file ; done > blast_results.txt.filtered

sed '1,1d' blast_results.txt.filtered | cut -f 1,21 | grep -v "No GO" | sed 's:;:\n-\t:g' | awk '{if ($1!="-") {print $0 ; id=$1} else {print id"\t"$2} }' | sort -u > blast_results.txt.filtered.annot
```

Load everything in Blast2Go.