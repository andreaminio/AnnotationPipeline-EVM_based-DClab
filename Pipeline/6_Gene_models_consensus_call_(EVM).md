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

/Tools/EVidenceModeler-1.1.1/EvmUtils/gff3_gene_prediction_file_validator.pl predictions.gff3
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
/Tools/EVidenceModeler-1.1.1/EvmUtils/partition_EVM_inputs.pl \
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
/Tools/EVidenceModeler-1.1.1/EvmUtils/write_EVM_commands.pl \
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
/Tools/EVidenceModeler-1.1.1/EvmUtils/recombine_EVM_partial_outputs.pl --partitions $(pwd)/partitions_list.out --output_file_name evm.out
```

Convert EVM output in GFF3.

``` bash
/Tools/EVidenceModeler-1.1.1/EvmUtils/convert_EVM_outputs_to_GFF3.pl  --partitions $(pwd)/partitions_list.out --output evm.out  --genome $genome

find $(pwd) -regex ".*evm.out.gff3" -exec cat {} \; > EVM.all.gff3
```

Filter calls of broken models generate filtered annotations and sequences.

``` bash
python /Scripts/GFF_extract_features.py -l -c -i -n -p EVM.filtered -a EVM.all.gff3 -g $genome > EVM.filtering.log
```

6.3 - Postprocessing
--------------------

Proceed with the polishing (6.3a) or not (6.3b) and then go to [7 - Filtering](7_Filtering.md).

### 6.3a - Polishing annotation

#### 6.3a.0 - Setup

##### 6.3a.0.1 - Define variables

`genome` genome fasta sequence.

`n_cores` number of cores.

##### 6.3a.0.2 - Set WD

```bash
cd 2-Annotation/2_2-Prediction/2_2_7-Annotation_polishing/
```

##### 6.3a.0.3 - Set files

###### 6.3a.0.3.1 - Copy files

``` bash
cp ../2_2_6-EVM/EVM.filtered.gff3 .
cp -r ../2_2_4-Transcript_mapping/all_transcripts.fasta* .
ln -s ../${genome}
```

###### 6.3a.0.3.2 - Create configuration file

``` {.bash}
vim pasa_config.txt
```

```bash
# DB name
DATABASE=polishing_PASA.sqlite
 
#######################################################
# Parameters to specify to specific scripts in pipeline
# create a key = "script_name" + ":" + "parameter" 
# assign a value as done above.
 
run_spliced_aligners.pl:-N=5
 
 
#script validate_alignments_in_db.dbi
validate_alignments_in_db.dbi:--MIN_PERCENT_ALIGNED=90
validate_alignments_in_db.dbi:--MIN_AVG_PER_ID=85
validate_alignments_in_db.dbi:--MAX_INTRON_LENGTH=45000
 
 
#script subcluster_builder.dbi
subcluster_builder.dbi:-m=30
 
#annotation comparison
cDNA_annotation_comparer.dbi:--MIN_PERCENT_OVERLAP=50
cDNA_annotation_comparer.dbi:--MIN_PERCENT_PROT_CODING=30
cDNA_annotation_comparer.dbi:--MIN_PERID_PROT_COMPARE=50
cDNA_annotation_comparer.dbi:--MIN_PERCENT_LENGTH_FL_COMPARE=70
cDNA_annotation_comparer.dbi:--MIN_PERCENT_LENGTH_NONFL_COMPARE=70
cDNA_annotation_comparer.dbi:--MIN_PERCENT_ALIGN_LENGTH=70
cDNA_annotation_comparer.dbi:--MIN_PERCENT_OVERLAP_GENE_REPLACE=90
cDNA_annotation_comparer.dbi:--MAX_UTR_EXONS=5
```

#### 6.3a.1 - Run PASA

Setup the database.

``` bash
mkdir -p pasa_run.log.dir 

/Tools/PASApipeline-v2.3.3/scripts/create_sqlite_cdnaassembly_db.dbi -c pasa_config.txt -S 'cdna_alignment_sqliteschema' -r

samtools faidx $genome
```

Run transcript alignment.

``` bash
/Tools/PASApipeline-v2.3.3/scripts/run_spliced_aligners.pl --aligners gmap,blat --genome $genome --transcripts all_transcripts.fasta -I 45000 -N 1 --CPU $n_cores -N 5
```

Load the transcripts alignments and the Transdecoder results.

``` bash
/Tools/PASApipeline-v2.3.3/scripts/upload_transcript_data.dbi -M 'polishing_PASA.sqlite' -t all_transcripts.fasta  -f NULL  && /Tools/PASApipeline-v2.3.3/scripts/import_spliced_alignments.dbi -M 'polishing_PASA.sqlite'  -A gmap -g gmap.spliced_alignments.gff3 && /Tools/PASApipeline-v2.3.3/scripts/import_spliced_alignments.dbi -M 'polishing_PASA.sqlite'  -A blat -g blat.spliced_alignments.gff3 && update_fli_status.dbi -M 'polishing_PASA.sqlite' -f all_transcripts.fasta.transdecoder.gff3.fl_accs
```

Validate the alignments.

``` bash
/Tools/PASApipeline-v2.3.3/scripts/validate_alignments_in_db.dbi -M 'polishing_PASA.sqlite' -g $genome -t all_transcripts.fasta --MAX_INTRON_LENGTH 45000 --CPU $n_cores --MIN_PERCENT_ALIGNED 90 --MIN_AVG_PER_ID 85 > alignment.validations.output
```

Extract valid (and rejected) alignments and find clusters on genome.

``` bash
/Tools/PASApipeline-v2.3.3/scripts/update_alignment_status.dbi -M 'polishing_PASA.sqlite' < alignment.validations.output  > pasa_run.log.dir/alignment.validation_loading.output && PASA_transcripts_and_assemblies_to_GFF3.dbi -M 'polishing_PASA.sqlite' -v -A -P gmap > polishing_PASA.sqlite.valid_gmap_alignments.gff3 && /Tools/PASApipeline-v2.3.3/scripts/PASA_transcripts_and_assemblies_to_GFF3.dbi -M 'polishing_PASA.sqlite' -f -A -P gmap > polishing_PASA.sqlite.failed_gmap_alignments.gff3 && /Tools/PASApipeline-v2.3.3/scripts/PASA_transcripts_and_assemblies_to_GFF3.dbi -M 'polishing_PASA.sqlite' -v -A -P blat > polishing_PASA.sqlite.valid_blat_alignments.gff3 && /Tools/PASApipeline-v2.3.3/scripts/PASA_transcripts_and_assemblies_to_GFF3.dbi -M 'polishing_PASA.sqlite' -f -A -P blat > polishing_PASA.sqlite.failed_blat_alignments.gff3 && /Tools/PASApipeline-v2.3.3/scripts/assign_clusters_by_stringent_alignment_overlap.dbi -M polishing_PASA.sqlite -L 30 > pasa_run.log.dir/cluster_reassignment_by_stringent_overlap.out
```

Assemble clustered transcripts.

``` bash
/Tools/PASApipeline-v2.3.3/scripts/assemble_clusters.dbi -G $genome  -M 'polishing_PASA.sqlite'  -T $n_cores  > polishing_PASA.sqlite.pasa_alignment_assembly_building.ascii_illustrations.out
```

Load assemblies in database end extract mRNA models.

``` bash
/Tools/PASApipeline-v2.3.3/scripts/assembly_db_loader.dbi -M 'polishing_PASA.sqlite' > pasa_run.log.dir/alignment_assembly_loading.out && /Tools/PASApipeline-v2.3.3/scripts/subcluster_builder.dbi -G $genome -M 'polishing_PASA.sqlite' -m 30 > pasa_run.log.dir/alignment_assembly_subclustering.out && /Tools/PASApipeline-v2.3.3/scripts/populate_mysql_assembly_alignment_field.dbi -M 'polishing_PASA.sqlite' -G $genome && /Tools/PASApipeline-v2.3.3/scripts/populate_mysql_assembly_sequence_field.dbi -M 'polishing_PASA.sqlite' -G $genome && /Tools/PASApipeline-v2.3.3/scripts/subcluster_loader.dbi -M 'polishing_PASA.sqlite'  < pasa_run.log.dir/alignment_assembly_subclustering.out  && /Tools/PASApipeline-v2.3.3/scripts/alignment_assembly_to_gene_models.dbi -M 'polishing_PASA.sqlite' -G $genome && /Tools/PASApipeline-v2.3.3/scripts/PASA_transcripts_and_assemblies_to_GFF3.dbi -M 'polishing_PASA.sqlite' -a  > polishing_PASA.sqlite.pasa_assemblies.gff3 && /Tools/PASApipeline-v2.3.3/scripts/describe_alignment_assemblies_cgi_convert.dbi -M 'polishing_PASA.sqlite'  > polishing_PASA.sqlite.pasa_assemblies_described.txt
```

Load gene annotation.

``` bash
/Tools/PASApipeline-v2.3.3/scripts/Load_Current_Gene_Annotations.dbi -c pasa_config.txt -g $genome -P EVM.filtered.gff3  > pasa_run.log.dir/output.annot_loading.41077.out
```

Compare gene annotation to assembled mRNA models.

``` bash
/Tools/PASApipeline-v2.3.3/scripts/cDNA_annotation_comparer.dbi -G $genome --CPU $n_cores -M 'polishing_PASA.sqlite' --MIN_PERCENT_PROT_CODING 30 --MIN_PERCENT_LENGTH_NONFL_COMPARE 70 --MAX_UTR_EXONS 5 --MIN_PERCENT_LENGTH_FL_COMPARE 70 --MIN_PERCENT_ALIGN_LENGTH 70 --MIN_PERCENT_OVERLAP_GENE_REPLACE 90 --MIN_PERID_PROT_COMPARE 50 --MIN_PERCENT_OVERLAP 50 > pasa_run.log.dir/polishing_PASA.sqlite.annotation_compare.out
```

Export updated model annotation.

``` bash
/Tools/PASApipeline-v2.3.3/scripts/dump_valid_annot_updates.dbi -M 'polishing_PASA.sqlite' -V -R -g $genome > polishing_PASA.sqlite.gene_structures_post_PASA_updates.gff3
```

#### 6.3a.2 - Filter results

Rename gene models.

``` bash
python /Scripts/GFF_RenameThemAll.py polished_PASA 00 NN polishing_PASA.sqlite.gene_structures_post_PASA_updates.gff3 > polishing_PASA.sqlite.gene_structures_post_PASA_updates.renamed.gff3 2>renaming.err &
```

Run GFF\_extractor.py.

``` bash
python /Scripts/GFF_extract_features.py -p EVM.filtered.polished.clean -a polishing_PASA.sqlite.gene_structures_post_PASA_updates.renamed.gff3 -g $genome > EVM.filtered.polished.cleaning.log
```

#### 6.3a.3 - Move to filtering

Copy files.

``` bash
cp EVM.filtered.polished.clean*fasta EVM.filtered.polished.clean*gff3 ../2_2_8-Filtering/

rename 's:EVM.filtered.polished.clean:gene_models:' ../2_2_8-Filtering/EVM.filtered.polished.clean*
```

### 6.3b - Skip polishing and proceed directly to model filtering

Copy results files to filtering folder.

``` bash
cp EVM.filtered.*fasta EVM.filtered.*gff3 ../2_2_8-Filtering/

rename 's:^EVM.filtered:gene_models:' ../2_2_8-Filtering/EVM.filtered*
```
