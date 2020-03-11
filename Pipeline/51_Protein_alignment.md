5.1 - Protein alignment
=======================

## 5.1.0 - Setup

### 5.1.0.1 - Define variables

`n_jobs` number of jobs to run in parallel.

`genome` genome fasta sequence.

### 5.1.0.2 - Set WD

```bash
cd 2-Annotation/2_2-Prediction/2_2_5-Protein_mapping/
```

5.1.1 - Align proteins
----------------------

Concatenate proteins from external evidences with RNAseq transcriptome encoded ones.

``` bash
zcat ../../2_0-External_evidences/2_0_1-Proteins/*.fasta.gz | sed 's:\*$::;s:\.$::' > proteins.fasta

cat ../../2_0-External_evidences/2_0_1-Proteins/*.fasta | sed 's:\*$::;s:\.$::' >> proteins.fasta
```

Split input.

``` bash
mkdir fasta && cd fasta/ && cat ../proteins.fasta | awk 'BEGIN {n_seq=0;} /^>/ {file=sprintf("myseq%010d.fasta",n_seq); n_seq++} {print >> file; print file}' | uniq > ../file_list && cd .. && mkdir -p alignments && mkdir -p logs
```

Run in parallel the exonerate alignment by input sequence:

``` bash
parallel -j $n_jobs "/Tools/exonerate-2.2.0-x86_64/bin/exonerate --model protein2genome --percent 50 fasta/{} $genome --showtargetgff TRUE  > alignments/{}.exonerate.out 2> logs/{}.exonerate.err" :::: file_list
```

5.1.2 - Convert alignments to GFF3
---------------------------------

Extract the output and copy the resulting GFF3 to EVM folder.

``` bash
find alignments -name "*.exonerate.out" | sort > file_list.out

parallel -j $n_jobs "/Tools/EVidenceModeler-1.1.1/EvmUtils/misc/Exonerate_to_evm_gff3.pl {} | sed 's:\(.*ID\=\)\(.*\=\)\(.*\):\1\3.\2\3:' > {.}.match.gff3" :::: file_list.out

find alignments -name "*.match.gff3" -exec cat {} \; | sed '/^$/d' > ../2_2_6-EVM/protein_alignments.gff3
```
