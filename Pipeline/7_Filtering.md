7 - Filtering
=============

## 7.0 - Setup

### 7.0.1 - Define variables

`genome` genome fasta sequence.

`n_jobs` number of jobs to run in parallel.

### 7.0.2 - Set WD

```bash
cd 2-Annotation/2_2-Prediction/2_2_8-Filtering/
```

### 7.0.3 - Set files

```bash
mkdir fasta
mkdir blast
```

## 7.1 - Filter

Generate commands.

``` bash
awk 'BEGIN {getline; id=$1 ;gsub(">","",id); print id ;filename="fasta/"id".fasta"; print $0 >filename } { if ($1~"^>") {id=$1 ; sub(/>/,"",id); filename="fasta/"id".fasta"; print id};  print $0 > filename }' gene_models.protein.fasta | sed 's:\(.*\):\blastp -num_threads 6 -db /DATA/db/RefSeq_protein_Plants/RefSeq_Plants.protein.faa -show_gis -outfmt 5 -query fasta/\1.fasta > blast/\1.xml:' > blast_commands.sh
```

Run blast commands in parallel.

``` bash
parallel -j $n_jobs :::: blast_commands.sh > log
```

Run Blast2GO to load xml files and detect models without hits.

Generate the table `No_blast.txt`.

Filter out unwanted models and correct GFF3 file.

``` bash
grep -vFf <(less to_remove.txt | cut -f 2 | sed '1,1d' ) gene_models.gff3  > gene_models.filtered.gff3
nohup GFF_extract_features.py -a gene_models.filtered.gff3 -g $genome -p gene_models.filtered -lscin > gene_models.filtered.log 2> gene_models.filtered.err &
```

