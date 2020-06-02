0.1.1 - mRNA/cDNA/ESTs/CDSs mapping
===================================

0.1.1.0 - Define variables
----------

n_cores number of cores.

genome genome fasta sequence.

mRNAs_fasta mRNA evidences fasta file.


0.1.1.1 - Mapping
-------------------

Setup the gmap index for the `$genome`.

``` bash
mkdir gmap_index

gmap_build -D gmap_index/ -d $genome $genome
```

Run a stringent mapping.

``` bash
gmap -K 20000 -B 4 -x 30 -f 2 -t $n_cores -O -D gmap_index/ -d $genome $mRNAs_fasta > mRNAs.on.genome.gff3 2> mRNAs.on.genome.gff3.err
```

0.1.1.2 - Filtering
---------------------

Select only transcripts mapping with identity \>80% and coverage \>80% and discard gmap tentative of CDS reconstruction.

``` bash
grep -wFf <(awk '$3=="mRNA"' mRNAs.on.genome.gff3 | sed 's:;:\t:g;s:=:\t:g' | awk '$16>80 && $18>80 {print $14; print $10}') mRNAs.on.genome.gff3 | awk '$3!="CDS"' > mRNAs.on.genome.cov_iden_g80.gff3
```

0.1.1.3 - Convert files
-------------------------

Convert the filtered file a gff3 alignment format and extract the mRNA sequences of the alignment region.

``` bash
gffread -g $genome -w mRNAs.on.genome.cov_iden_g80.fasta -o - -T mRNAs.on.genome.cov_iden_g80.gff3 > mRNAs.on.genome.cov_iden_g80.gtf

perl /Tools/TransDecoder-3.0.1/util/cufflinks_gtf_to_alignment_gff3.pl mRNAs.on.genome.cov_iden_g80.gtf > mRNAs.on.genome.cov_iden_g80.alignment.gff3
```
