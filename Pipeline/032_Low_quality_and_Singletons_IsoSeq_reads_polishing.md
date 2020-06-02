0.3.2 - Low quality and Singletons IsoSeq reads polishing
=========================================================

## 0.3.2.0 - Setup

-  **0.3.2.0.1 - Define variables**
  - `sample_rnaseq` sample name of the RNA-Seq sample.
  - `sample_isoseq` sample name of the Iso-Seq sample.
  - `n_cores` number of cores.

-  **0.3.2.0.2 - Set WD**
```bash
cd 2_0-External_evidences/2_0_2-mRNAs/2_0_2_3-IsoSeq/2_0_2_3_2-IsoSeq_polishing/
```

### 0.3.2.0.3 - Set files and environment

``` bash
export singletons_isoforms=${sample_isoseq}.polished.singletons.fasta
export lq_isoforms=${sample_isoseq}.polished.lq.fasta
export RNAseq_fq=${sample_rnaseq}.fil.fastq
export LSC=/Tools/LSC-2.0/bin/runLSC.py
export lq_tempdir=2_0_2_3_2_1-LQ_tempdir
export lq_outdir=2_0_2_3_2_1-LQ
export singleton_tempdir=2_0_2_3_2_2-Singleton_tempdir
export singleton_outdir=2_0_2_3_2_2-Singleton
```

0.3.2.1 - Polish LQ Isoforms with LSC
-------------------------------------

Setup.

``` bash
mkdir $lq_tempdir
mkdir $lq_outdir
```

Homopolymer compression.

```bash
$LSC --mode 1 --long_reads $lq_isoforms --short_reads $RNAseq_fq --short_read_file_type fq --specific_tempdir $lq_tempdir > lq_mode1.log
```

Alignment and correction.

```bash
$LSC --mode 2 --threads $n_cores --specific_tempdir $lq_tempdir
```

Combine results.

```bash
$LSC --mode 3 --specific_tempdir $lq_tempdir --output $lq_outdir
```

Quality control.

```bash
cd $lq_outdir
```

FastqQC. 

``` bash
fastqc --extract corrected_LR.fq
```

Statistics.

``` bash
for file in *.fa ; do bash reads_statistics.sh ${file} > ${file}.stats; done
```

Read length.

``` bash
for file in *.fa ; do python getLengthFromFasta.py ${file} > ${file}.len; done
```

Export polished reads.

``` bash
cat 2_0_2_3_2_1-LQ/full_LR.fa | sed 's:>:>IsoSeq_LQ.LSC_full_LR.:;s:/:_:g' > ../../${sample_isoseq}.IsoSeq_LQ.LSC_full_LR.fasta
```

0.3.2.2 - Polish Singleton Isoforms with LSC
--------------------------------------------

Setup.

``` bash
mkdir $singleton_outdir
mkdir $singleton_tempdir
```

Homopolymer compression.

```bash
$LSC --mode 1 --long_reads $singletons_isoforms --short_reads $RNAseq_fq --short_read_file_type fq --specific_tempdir $singleton_tempdir > singleton_mode1.log
```

Alignment and correction.

```bash
$LSC --mode 2 --threads $n_cores --specific_tempdir $singleton_tempdir
```

Combine results.

```bash
$LSC --mode 3 --specific_tempdir $singleton_tempdir --output $singleton_outdir
```

Quality control.

```bash
cd $singleton_outdir
```

FastqQC.

``` bash
fastqc --extract corrected_LR.fq
```

Statistics.

``` bash
for file in *.fa ; do bash reads_statistics.sh ${file} > ${file}.stats; done
```

Read length.

``` bash
for file in *.fa ; do python getLengthFromFasta.py ${file} > ${file}.len; done
```

Export polished reads.

``` bash
cat 2_0_2_3_2_2-Singleton/full_LR.fa | sed 's:>:>IsoSeq_Singleton.LSC_full_LR.:;s:/:_:g' > ../../${sample_isoseq}.IsoSeq_Singleton.LSC_full_LR.fasta
```
