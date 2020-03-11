# Cantù Lab @ UC Davis - Annotation Pipeline - EVM based

This Git repository contains the whole pipeline used in the publications: [articles]().

The assembly of the genome was generated prior to this pipeline [github falcon]().

## Requirements
The following tools are required:

- [augustus v.3.0.3](http://bioinf.uni-greifswald.de/augustus/)
- [bedtools](https://bedtools.readthedocs.io/en/latest/)
- [BLAST v.2.6.0+](https://blast.ncbi.nlm.nih.gov/Blast.cgi?PAGE_TYPE=BlastDocs&DOC_TYPE=Download)
- [Blast2GO](https://www.blast2go.com/)
- [BLAT v.36x2](https://genome.ucsc.edu/FAQ/FAQblat.html)
- [busco](https://busco.ezlab.org/)
- [EVidenceModeler v.1.1.1](https://evidencemodeler.github.io/)
- [exonerate v.2.2.0](https://www.ebi.ac.uk/about/vertebrate-genomics/software/exonerate-manual)
- [fastqc](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/)
- [genemark](http://exon.gatech.edu/GeneMark/)
- [gffcompare](https://ccb.jhu.edu/software/stringtie/gffcompare.shtml)
- [gffread](http://ccb.jhu.edu/software/stringtie/gff.shtml)
- [gmap v.2015-09-29](http://research-pub.gene.com/gmap/)
- [hisat2 v.2.0.5](https://ccb.jhu.edu/software/hisat2/manual.shtml)
- [IsoSeq v.3](https://github.com/PacificBiosciences/IsoSeq)
- [LSC]()
- [magicblast v.1.4.0](https://ncbi.github.io/magicblast/)
- [maker](https://www.yandell-lab.org/software/maker.html)
- [parallel](https://www.gnu.org/software/parallel/)
- [PASA v.2.3.3](https://github.com/PASApipeline/PASApipeline/wiki)
- [RepeatMasker v.open-4.0.6](http://www.repeatmasker.org/)
- [samtools](http://www.htslib.org/)
- [SNAP](https://github.com/KorfLab/SNAP)
- [stringtie v.1.3.4d](https://ccb.jhu.edu/software/stringtie/)
- [TransDecoder v.3.0.1](https://github.com/TransDecoder/TransDecoder/wiki)
- [trimmomatic v.0.36](http://www.usadellab.org/cms/?page=trimmomatic)
- [Trinity v.2.6.5](https://github.com/trinityrnaseq/trinityrnaseq/wiki)

## Folder structure

```bash
2-Annotation
├── 2_0-External_evidences
│   ├── 2_0_1-Proteins
│   └── 2_0_2-mRNAs
│       ├── 2_0_2_1-External_databases
│       ├── 2_0_2_2-RNAseq
│       │   ├── 2_0_2_2_1-RNAseq_reads
│       │   └── 2_0_2_2_2-RNAseq_assembly
│       └── 2_0_2_3-IsoSeq
│           ├── 2_0_2_3_1-IsoSeq_reads
│           └── 2_0_2_3_2-IsoSeq_polishing
├── 2_1-Training
│   ├── 2_1_1-Training_set
│   │   └── pasa_run.log.dir
│   └── 2_1_2-Predictor_training
│       ├── 2_1_2_1-Augustus
│       ├── 2_1_2_2-Genemark
│       └── 2_1_2_3-SNAP
└── 2_2-Prediction
    ├── 2_2_1-Repeats
    ├── 2_2_2-
    ├── 2_2_3-Prediction
    │   ├── 2_2_3_1-BUSCO
    │   ├── 2_2_3_2-Augustus
    │   ├── 2_2_3_3-Genemark
    │   ├── 2_2_3_4-SNAP
    │   └── 2_2_3_5-PASA
    ├── 2_2_4-Transcript_mapping
    ├── 2_2_5-Protein_mapping
    ├── 2_2_6-EVM
    ├── 2_2_7-Annotation_polishing
    ├── 2_2_8-Filtering
    └── 2_2_9-Functional_annotation
```

## Pipeline

- [0 - External evidences](Pipeline/0_External_evidences.md)
- [1 - Repeat annotation](Pipeline/1_Repeat_annotation.md)
- [2 - Training set creation](Pipeline/2_Training_set_creation.md)
- [3 - Ab initio predictors training](Pipeline/3_Ab_initio_predictors_training.md)
- [4 - Ab initio prediction](Pipeline/4_Ab_initio_prediction.md)
- [5 - Evidence alignment](Pipeline/5_Evidence_alignment.md)
- [6 - Gene models consensus call (EVM)](Pipeline/6_Gene_models_consensus_call_(EVM).md)
  - [6.3a (optional) - Annotation polishing](Pipeline/63a_Annotation_polishing.md)
- [7 - Filtering](Pipeline/7_Filtering.md)
- [8 - Renaming](Pipeline/8_Renaming.md)
- [9 - Functional annotation](Pipeline/9_Functional_annotation.md)

## References