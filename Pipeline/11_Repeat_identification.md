1.1 - Repeat identification
===========================

## 1.1.0 - Setup

### 1.1.0.1 - Define variables

`n_proc` number of parallel processes to run.

`library_file` custom repeat library file to use.

`FASTA` name of the fasta files.

### 1.1.0.2 - Set WD

```bash
cd 2-Annotation/2_2-Prediction/2_2_1-Repeats/
```

1.1.1 - Run RepeatMasker for each FASTA file of sequences
---------------------------------------------------------

Run repeatmasker.
``` bash
for file in *.fasta; do RepeatMasker -pa $n_proc -s -lib $library_file -a -lcambig -xsmall -poly -source -html -ace -gff -u -xm -excln -e ncbi $file; done
```
Concatenate the results.
``` bash
for file in *.out.gff ; do cat ${file} | sed 's:Target ":ID=:;s:".*::' > ${file}3
cat *.out.gff3 | sed '/^#/d' > ../2_2_6-EVM/repeats.gff3
```

1.1.2 - Build repeats summary
-----------------------------

``` bash
/Tools/RepeatMasker/util/buildSummary.pl $FASTA.out > $FASTA.out.stats
```

