2.a.1 - Transcriptome to gene model construction
================================================

## 2.a.1.0 - Setup

### 2.a.1.0.1 - Define variables

`name` name of the genome.

`n_cores` number of cores.

`genome` genome fasta sequence.

### 2.a.1.0.2 - Set WD

```bash
cd 2-Annotation/2_0-External_evidences/2_0_2-mRNAs/2_0_2_2-RNAseq/2_0_2_2_2-RNAseq_assembly
```

2.a.1.1 - RNAseq data assembly
------------------------------

### 2.a.1.1.1 - Stringtie (on-genome reference based)

``` bash
cp ${name}.stringtie.transdecoder.clean.mRNA.fasta ${name}.stringtie.transdecoder.clean.prot.fasta ${name}.stringtie.transdecoder.clean.CDS.fasta ${name}.stringtie.transdecoder.clean.gff3 ../../../2_1-Training/2_1_1-Training_set/ 
```

### 2.a.1.1.2 - Trinity on-genome (on-genome de novo)

``` bash
cp ${name}.trinity.og.transdecoder.clean.mRNA.fasta ${name}.trinity.og.transdecoder.clean.prot.fasta ${name}.trinity.og.transdecoder.clean.CDS.fasta ${name}.trinity.og.transdecoder.clean.gff3 ../../../2_1-Training/2_1_1-Training_set/ 
```

### 2.a.1.1.3 - Trinity (de novo)

``` bash
cp ${name}.trinity.dn.transdecoder.clean.mRNA.fasta ${name}.trinity.dn.transdecoder.clean.prot.fasta ${name}.trinity.dn.transdecoder.clean.CDS.fasta ${name}.trinity.dn.transdecoder.clean.gff3 ../../../2_1-Training/2_1_1-Training_set/ 
```

2.a.1.2 - mRNA data
-------------------

Identify CDS regions in the sequences extracted from mRNA alignments.

```bash
/Tools/TransDecoder-3.0.1/TransDecoder.LongOrfs -t mRNAs.on.genome.cov_iden_g80.fasta

/Tools/TransDecoder-3.0.1/TransDecoder.Predict --cpu $n_cores -t mRNAs.on.genome.cov_iden_g80.fasta

cat mRNAs.on.genome.cov_iden_g80.fasta.transdecoder.gff3 | awk '$7!="-"' >mRNAs.on.genome.cov_iden_g80.fasta.transdecoder.no_minus.gff3
```

Port CDSs coordinates from transcripts to genome.

```bash
/Tools/TransDecoder-3.0.1/cdna_alignment_orf_to_genome_orf.pl mRNAs.on.genome.cov_iden_g80.fasta.transdecoder.no_minus.gff3 mRNAs.on.genome.cov_iden_g80.alignment.gff3 mRNAs.on.genome.cov_iden_g80.fasta > mRNAs.on.genome.cov_iden_g80.transdecoder.gff3
```

Filter out transcripts without a good ORF (no met to start, premature stop codons).

```bash
python /Scripts/GFF_extract_features.py -g $genome -a mRNAs.on.genome.cov_iden_g80.transdecoder.gff3 -p mRNAs.on.genome.cov_iden_g80.transdecoder.clean 2> mRNAs.on.genome.cov_iden_g80.transdecoder.clean.log
```

