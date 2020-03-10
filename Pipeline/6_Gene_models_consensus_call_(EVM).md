6 - Gene models consensus call (EVM)
====================================

## 6.0 - Setup

### 6.0.1 - Define variables

`genome` genome fasta sequence.

### 6.0.2 - Set WD

```bash
cd 2-Annotation/2_2-Prediction/2_2_6-EVM/
```

### 6.0.3 - Set files

#### 6.0.3.1 - Merge predictions and test file correctness.

``` bash
cat prediction.*.gff3 > predictions.gff3

gff3_gene_prediction_file_validator.pl predictions.gff3
```

#### 6.0.3.2 - Concatenate transcript alignments.

``` bash
cat transcript_alignment.*.gff3 > transcript_alignments.gff3
```

#### 6.0.3.3 - Generate `weights.txt` file.

``` bash
echo -e "ABINITIO_PREDICTION\tAUGUSTUS\t9\nABINITIO_PREDICTION\tGeneMark.hmm3\t9\nABINITIO_PREDICTION\taugustus_BUSCOv3\t10\nABINITIO_PREDICTION\tsnap\t6\nPROTEIN\texonerate\t3\nTRANSCRIPT\tgmap\t7\nTRANSCRIPT\tBLAT\t6\nTRANSCRIPT\tmagicblast\t7\nTRANSCRIPT\tPASA_assemblies\t20\nOTHER_PREDICTION\tPASA_transdecoder\t25" > weights.txt
```

6.1 - Run EVM
-------------

Partition the genome sequence.

``` bash
partition_EVM_inputs.pl \
   --genome $genome \
   --gene_predictions predictions.gff3 \
   --protein_alignments protein_alignments.gff3 \
   --transcript_alignments transcript_alignments.gff3 \
   --repeats repeats.gff3 \
   --segmentSize 300000 \
   --overlapSize 100000 \
   --partition_listing partitions_list.out &> 1-partition.log
```

Generate commands.

``` bash
write_EVM_commands.pl \
   --genome $genome \
   --weights $(pwd)/weights.txt \
   --gene_predictions predictions.gff3 \
   --protein_alignments protein_alignments.gff3 \
   --transcript_alignments transcript_alignments.gff3 \
   --repeats repeats.gff3 \
   --output_file_name evm.out  \
   --partitions $(pwd)/partitions_list.out >  commands.list
```

Run commands in parallel.

``` bash
parallel -j 12 :::: commands.list
```

Combine partial outputs.

``` bash
recombine_EVM_partial_outputs.pl --partitions $(pwd)/partitions_list.out --output_file_name evm.out
```

Convert EVM output in GFF3.

``` bash
convert_EVM_outputs_to_GFF3.pl  --partitions $(pwd)/partitions_list.out --output evm.out  --genome $genome

find $(pwd) -regex ".*evm.out.gff3" -exec cat {} \; > EVM.all.gff3
```

Filter calls of broken models generate filtered annotations and sequences.

``` bash
GFF_extract_features.py -l -c -i -n -p EVM.filtered -a EVM.all.gff3 -g $genome > EVM.filtering.log
```

6.3 - Postprocessing
--------------------

### 6.3a - Polishing annotation

Proceed with step [](/bioinforesources/pipelines/annotation/optional_annotation_polishing).

### 6.3b - Skip polishing and proceed directly to model filtering

Copy results files to filtering folder.

``` bash
cp EVM.filtered.*fasta EVM.filtered.*gff3 ../2_2_8-Filtering/

rename 's:^EVM.filtered:gene_models:' ../2_2_8-Filtering/EVM.filtered*
```

Proceed with step [](/bioinforesources/pipelines/annotation/7_-_filtering).