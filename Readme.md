# Cantù Lab @ UC Davis - Annotation Pipeline - EVM based

This Git repository contains the whole pipeline used in the publications: [articles]().

The assembly of the genome was generated prior to this pipeline [github falcon]().

## Requirements
The following tools are required:

- 

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
