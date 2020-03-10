0.2.1 - Reads and evidence mapping
==================================

## 0.2.1.0 - Setup

### 0.2.1.0.1 - Define variables

`out_dir` directory for filtered reads.

`ref_index` genome hisat2 index.

`fastq_1` read 1 from paired-ends.

`fastq_2` read 2 from paired-ends.

`fastq` reads from single end.

`out_bam` hisat2 alignment file name.

`n_cores` number of cores.

`genome` genome fasta sequence.

`mRNAs_fasta` mRNA evidences fasta file.

### 0.2.1.0.2 - Set WD

```bash
cd 2-Annotation/2_0-External_evidences/2_0_2-mRNAs/2_0_2_2-RNAseq/2_0_2_2_1-RNAseq_reads/
```

0.2.1.1 - RNAseq reads mapping
------------------------------

### 0.2.1.1.1 - Filter reads

-   Paired-end reads

``` bash
doFilter.PE.sh $out_dir
```

Will run on all pairs of reads in the folder where run and will put the 4 output files for each pair in `$out_dir`.

-   Single reads

``` bash
doFilter.SR.sh $out_dir
```

Will run on all FASTQ files of reads in the folder separately and will put the the corresponding output files in `$out_dir`.

### 0.2.1.1.2 - Map

-   Paired-end reads

``` bash
doMap.HISAT2.PE.sh $ref_index $fastq_1 $fastq_2 $out_bam $n_cores
```

-   Single reads

``` bash
doMap.HISAT2.SR.sh $ref_index $fastq $out_bam $n_cores
```

0.2.1.2 - mRNA/cDNA/ESTs/CDSs mapping
-------------------------------------

### 0.2.1.2.1 - Mapping

Setup the gmap index for the `$genome`.

``` bash
mkdir gmap_index

gmap_build -D gmap_index/ -d $genome $genome
```

Run a stringent mapping.

``` bash
gmap -K 20000 -B 4 -x 30 -f 2 -t $n_cores -O -D gmap_index/ -d $genome $mRNAs_fasta > mRNAs.on.genome.gff3 2> mRNAs.on.genome.gff3.err
```

### 0.2.1.2.2 - Filtering

Select only transcripts mapping with identity \>80% and coverage \>80% and discard gmap tentative of CDS reconstruction.

``` bash
grep -wFf <(awk '$3=="mRNA"' mRNAs.on.genome.gff3 | sed 's:;:\t:g;s:=:\t:g' | awk '$16>80 && $18>80 {print $14; print $10}') mRNAs.on.genome.gff3 | awk '$3!="CDS"' > mRNAs.on.genome.cov_iden_g80.gff3
```

### 0.2.1.2.3 - Convert files

Convert the filtered file a gff3 alignment format and extract the mRNA sequences of the alignment region.

``` bash
gffread -g $genome -w mRNAs.on.genome.cov_iden_g80.fasta -o - -T mRNAs.on.genome.cov_iden_g80.gff3 > mRNAs.on.genome.cov_iden_g80.gtf

perl cufflinks_gtf_to_alignment_gff3.pl mRNAs.on.genome.cov_iden_g80.gtf > mRNAs.on.genome.cov_iden_g80.alignment.gff3
```

