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
bash /Scripts/doFilter.PE.sh $out_dir
```

Will run on all pairs of reads in the folder where run and will put the 4 output files for each pair in `$out_dir`.

-   Single reads

``` bash
bash /Scripts/doFilter.SR.sh $out_dir
```

Will run on all FASTQ files of reads in the folder separately and will put the the corresponding output files in `$out_dir`.

### 0.2.1.1.2 - Map

-   Paired-end reads

``` bash
bash /Scripts/doMap.HISAT2.PE.sh $ref_index $fastq_1 $fastq_2 $out_bam $n_cores
```

-   Single reads

``` bash
bash /Scripts/doMap.HISAT2.SR.sh $ref_index $fastq $out_bam $n_cores
```

