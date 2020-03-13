0.2.2 - RNAseq assembly
=======================

## 0.2.2.0 - Setup

### 0.2.2.0.1 - Define variables

`sample` name of the RNA-Seq sample.

`name` name of the genome.

`n_cores` number of cores.

`genome` genome fasta sequence.

### 0.2.2.0.2 - Set WD

```bash
cd 2-Annotation/2_0-External_evidences/2_0_2-mRNAs/2_0_2_2-RNAseq/2_0_2_2_2-RNAseq_assembly
```

0.2.2.1 - Stringtie (on-genome reference based)
-----------------------------------------------

Run Stringtie from reads alignments of each sample separately.

``` bash
/Tools/stringtie-1.3.4d.Linux_x86_64/stringtie ${sample}_on_${name}.bam -p $n_cores -v -l STRG_${sample}_on_${name} -o ${sample}_on_${name}.stringtie.gtf -A ${sample}_on_${name}.stringtie.abundance.txt 2> err | tee log
```

If multiple samples are present, merge the results.

``` bash
/Tools/stringtie-1.3.4d.Linux_x86_64/stringtie --merge -o ${name}.stringtie.gtf -i -l STRG.${name} *_on_${name}.stringtie.gtf
```

Find ORFs in stringtie models.

``` bash
perl /Tools/TransDecoder-3.0.1/util/cufflinks_gtf_genome_to_cdna_fasta.pl ${name}.stringtie.gtf $genome > ${name}.stringtie.exon.fasta

perl /Tools/TransDecoder-3.0.1/util/cufflinks_gtf_to_alignment_gff3.pl ${name}.stringtie.gtf > ${name}.stringtie.alignment.gff3

/Tools/TransDecoder-3.0.1/util/TransDecoder.LongOrfs -t ${name}.stringtie.exon.fasta
/Tools/TransDecoder-3.0.1/util/TransDecoder.Predict --cpu $n_cores -t ${name}.stringtie.exon.fasta

/Tools/TransDecoder-3.0.1/util/cdna_alignment_orf_to_genome_orf.pl ${name}.stringtie.exon.fasta.transdecoder.gff3 ${name}.stringtie.alignment.gff3 ${name}.stringtie.exon.fasta > ${name}.stringtie.transdecoder.gff3
```

Filter models with broken ORFs (no met at start, premature stop codons).

``` bash
python /Scripts/GFF_extract_features.py -g $genome -a ${name}.stringtie.transdecoder.gff3 -p ${name}.stringtie.transdecoder.clean > ${name}.stringtie.transdecoder.clean.log
```

0.2.2.2 - Trinity on-genome (on-genome de novo)
-----------------------------------------------

Setup.

``` bash
export TRINITY_HOME=/DATA7/Resources/Tools/Trinity-v2.6.5
export TRINITY=/DATA7/Resources/Tools/Trinity-v2.6.5/Trinity
```

Run Trinity on reads alignments of each sample.

``` bash
$TRINITY --max_memory 95G --CPU $n_cores --genome_guided_bam ${sample}_on_${name}.bam --genome_guided_max_intron 15000 --min_contig_length 200 --normalize_max_read_cov 30 --jaccard_clip --output Trinity_OnGenome_${sample} 2>&1 > Trinity_OnGenome_${sample}.trinity_log.txt

cat Trinity_OnGenome_${sample}/Trinity-GG.fasta | sed 's: .*::;s:>:>'${sample}'-:' > ${sample}.trinity.og.fasta
```

Merge Trinity alignments.

``` bash
cat *.trinity.og.fasta > ${name}.trinity.og.fasta
```

Map assembled transcripts on the genome.

``` bash
gmap -K 20000 -B 4 -x 30 -f 2 -t $n_cores -O -D gmap_index/ -d $genome ${name}.trinity.og.fasta > ${name}.trinity.og.on.genome.gff3 2>> ${name}.trinity.og.on.genome.err
```

Stringent filtering of alignments (identity\>95%, coverage\>95%) and file conversion to alignment GFF3 format.

``` bash
grep -wFf <(awk '$3=="mRNA"' ${name}.trinity.og.on.genome.gff3 | sed 's:;:\t:g;s:=:\t:g' | awk '$16>95 && $18>95 {print $14; print $10}') ${name}.trinity.og.on.genome.gff3| awk '$3!="CDS"' > ${name}.trinity.og.on.genome.cov_iden_g95.gff3

gffread -g $genome -w ${name}.trinity.og.on.genome.cov_iden_g95.fasta -o - -T ${name}.trinity.og.on.genome.cov_iden_g95.gff3 > ${name}.trinity.og.on.genome.cov_iden_g95.gtf

/Tools/TransDecoder-3.0.1/util/cufflinks_gtf_to_alignment_gff3.pl ${name}.trinity.og.on.genome.cov_iden_g95.gtf > ${name}.trinity.og.on.genome.cov_iden_g95.alignment.gff3
```

Identify ORFs in alignment mRNA sequences and port coordinates on the genome.

``` bash
/Tools/TransDecoder-3.0.1/util/TransDecoder.LongOrfs -t ${name}.trinity.og.on.genome.cov_iden_g95.fasta

/Tools/TransDecoder-3.0.1/util/TransDecoder.Predict --cpu $n_cores -t ${name}.trinity.og.on.genome.cov_iden_g95.fasta

cat ${name}.trinity.og.on.genome.cov_iden_g95.fasta.transdecoder.gff3 | awk '$7!="-"' > ${name}.trinity.og.on.genome.cov_iden_g95.fasta.transdecoder.no_minus.gff3

/Tools/TransDecoder-3.0.1/util/cdna_alignment_orf_to_genome_orf.pl ${name}.trinity.og.on.genome.cov_iden_g95.fasta.transdecoder.no_minus.gff3 ${name}.trinity.og.on.genome.cov_iden_g95.alignment.gff3 ${name}.trinity.og.on.genome.cov_iden_g95.fasta > ${name}.trinity.og.transdecoder.gff3
```

Filter models with broken ORFs (no met at start, premature stop codons).

``` bash
python /Scripts/GFF_extract_features.py -g $genome -a ${name}.trinity.og.transdecoder.gff3 -p ${name}.trinity.og.transdecoder.clean 2> ${name}.trinity.og.transdecoder.clean.log
```

0.2.2.3 - Trinity (de novo)
---------------------------

Setup.

``` bash
export TRINITY_HOME=/DATA7/Resources/Tools/Trinity-v2.6.5
export TRINITY=/DATA7/Resources/Tools/Trinity-v2.6.5/Trinity
```

Run Trinity on each sample separately.

``` bash
$TRINITY --max_memory 95G --CPU $n_cores --single ${sample}.*fastq.gz --seqType fq --min_contig_length 200 --normalize_max_read_cov 30 --jaccard_clip --output Trinity_DeNovo_${sample} 2>&1 > Trinity_DeNovo_${sample}.trinity_log.txt

cat Trinity_DeNovo_${sample}/Trinity.fasta | sed 's: .*::;s:>:>'${sample}'_:' > ${sample}.trinity.dn.fasta
```

Map assembled mRNAs.

``` bash
cat *.trinity.dn.fasta > ${name}.trinity.dn.fasta

gmap -K 20000 -B 4 -x 30 -f 2 -t $n_cores -O -D gmap_index/ -d $genome ${name}.trinity.dn.fasta > ${name}.trinity.dn.on.genome.gff3 2>> ${name}.trinity.dn.on.genome.err
```

Filter alignments in very stringent way (identity \>95% && coverage \>95%) and discard CDS tentative reconstruction.

``` bash
grep -wFf <(awk '$3=="mRNA"' ${name}.trinity.dn.on.genome.gff3 | sed 's:;:\t:g;s:=:\t:g' | awk '$16>95 && $18>95 {print $14; print $10}') ${name}.trinity.dn.on.genome.gff3 | awk '$3!="CDS"'> ${name}.trinity.dn.on.genome.cov_iden_g95.gff3
```

Extract alignment mRNA sequence and convert annotation to alignment GFF3.

``` bash
gffread -g $genome -w ${name}.trinity.dn.on.genome.cov_iden_g95.fasta -o - -T ${name}.trinity.dn.on.genome.cov_iden_g95.gff3 > ${name}.trinity.dn.on.genome.cov_iden_g95.gtf

/Tools/TransDecoder-3.0.1/util/cufflinks_gtf_to_alignment_gff3.pl ${name}.trinity.dn.on.genome.cov_iden_g95.gtf > ${name}.trinity.dn.on.genome.cov_iden_g95.alignment.gff3
```

Identify CDSs in alignment mRNA sequences and port the coordinates from transcript to genome.

``` bash
/Tools/TransDecoder-3.0.1/util/TransDecoder.LongOrfs -t ${name}.trinity.dn.on.genome.cov_iden_g95.fasta

/Tools/TransDecoder-3.0.1/util/TransDecoder.Predict --cpu $n_cores -t ${name}.trinity.dn.on.genome.cov_iden_g95.fasta

cat ${name}.trinity.dn.on.genome.cov_iden_g95.fasta.transdecoder.gff3 | awk '$7!="-"' > ${name}.trinity.dn.on.genome.cov_iden_g95.fasta.transdecoder.no_minus.gff3

/Tools/TransDecoder-3.0.1/util/TransDecoder-3.0.1/util/cdna_alignment_orf_to_genome_orf.pl ${name}.trinity.dn.on.genome.cov_iden_g95.fasta.transdecoder.no_minus.gff3 ${name}.trinity.dn.on.genome.cov_iden_g95.alignment.gff3 ${name}.trinity.dn.on.genome.cov_iden_g95.fasta > ${name}.trinity.dn.transdecoder.gff3
```

Filter out results of transcripts with broken ORFs (no met at start, premature stop codons).

``` bash
python /Scripts/GFF_extract_features.py -g $genome -a ${name}.trinity.dn.transdecoder.gff3 -p ${name}.trinity.dn.transdecoder.clean 2> ${name}.trinity.dn.transdecoder.clean.log
```

0.2.2.4 - Export useful files
-----------------------------

-   mRNA sequences

``` bash
cp -v *.transdecoder.clean.mRNA.fasta ../../
```

-   Proteins

``` bash
cp -v *.transdecoder.clean.prot.fasta ../../../2_0_1-Proteins/
```

