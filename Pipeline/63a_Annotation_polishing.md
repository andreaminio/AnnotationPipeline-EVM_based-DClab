6.3a (optional) - Annotation polishing
======================================

## 6.3a.0 - Setup

### 6.3a.0.1 - Define variables

`genome` genome fasta sequence.

`n_cores` number of cores.

### 6.3a.0.2 - Set WD

```bash
cd 2-Annotation/2_2-Prediction/2_2_7-Annotation_polishing/
```

### 6.3a.0.3 - Set files

#### 6.3a.0.3.1 - Copy files

``` bash
cp ../2_2_6-EVM/EVM.filtered.gff3 .
cp -r ../2_2_4-Transcript_mapping/all_transcripts.fasta* .
ln -s ../${genome}
```

#### 6.3a.0.3.2 - Create configuration file

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

6.3a.1 - Run PASA
--------

Setup the database.

``` bash
mkdir -p pasa_run.log.dir create_sqlite_cdnaassembly_db.dbi -c pasa_config.txt -S 'cdna_alignment_sqliteschema' -r

samtools faidx $genome
```

Run transcript alignment.

``` bash
run_spliced_aligners.pl --aligners gmap,blat --genome $genome --transcripts all_transcripts.fasta -I 45000 -N 1 --CPU $n_cores -N 5
```

Load the transcripts alignments and the Transdecoder results.

``` bash
upload_transcript_data.dbi -M 'polishing_PASA.sqlite' -t all_transcripts.fasta  -f NULL  && import_spliced_alignments.dbi -M 'polishing_PASA.sqlite'  -A gmap -g gmap.spliced_alignments.gff3 && import_spliced_alignments.dbi -M 'polishing_PASA.sqlite'  -A blat -g blat.spliced_alignments.gff3 && update_fli_status.dbi -M 'polishing_PASA.sqlite' -f all_transcripts.fasta.transdecoder.gff3.fl_accs
```

Validate the alignments.

``` bash
validate_alignments_in_db.dbi -M 'polishing_PASA.sqlite' -g $genome -t all_transcripts.fasta --MAX_INTRON_LENGTH 45000 --CPU $n_cores --MIN_PERCENT_ALIGNED 90 --MIN_AVG_PER_ID 85 > alignment.validations.output
```

Extract valid (and rejected) alignments and find clusters on genome.

``` bash
update_alignment_status.dbi -M 'polishing_PASA.sqlite' < alignment.validations.output  > pasa_run.log.dir/alignment.validation_loading.output && PASA_transcripts_and_assemblies_to_GFF3.dbi -M 'polishing_PASA.sqlite' -v -A -P gmap > polishing_PASA.sqlite.valid_gmap_alignments.gff3 && PASA_transcripts_and_assemblies_to_GFF3.dbi -M 'polishing_PASA.sqlite' -f -A -P gmap > polishing_PASA.sqlite.failed_gmap_alignments.gff3 && PASA_transcripts_and_assemblies_to_GFF3.dbi -M 'polishing_PASA.sqlite' -v -A -P blat > polishing_PASA.sqlite.valid_blat_alignments.gff3 && PASA_transcripts_and_assemblies_to_GFF3.dbi -M 'polishing_PASA.sqlite' -f -A -P blat > polishing_PASA.sqlite.failed_blat_alignments.gff3 && assign_clusters_by_stringent_alignment_overlap.dbi -M polishing_PASA.sqlite -L 30 > pasa_run.log.dir/cluster_reassignment_by_stringent_overlap.out
```

Assemble clustered transcripts.

``` bash
assemble_clusters.dbi -G $genome  -M 'polishing_PASA.sqlite'  -T $n_cores  > polishing_PASA.sqlite.pasa_alignment_assembly_building.ascii_illustrations.out
```

Load assemblies in database end extract mRNA models.

``` bash
assembly_db_loader.dbi -M 'polishing_PASA.sqlite' > pasa_run.log.dir/alignment_assembly_loading.out && subcluster_builder.dbi -G $genome -M 'polishing_PASA.sqlite' -m 30 > pasa_run.log.dir/alignment_assembly_subclustering.out && populate_mysql_assembly_alignment_field.dbi -M 'polishing_PASA.sqlite' -G $genome && populate_mysql_assembly_sequence_field.dbi -M 'polishing_PASA.sqlite' -G $genome && subcluster_loader.dbi -M 'polishing_PASA.sqlite'  < pasa_run.log.dir/alignment_assembly_subclustering.out  && alignment_assembly_to_gene_models.dbi -M 'polishing_PASA.sqlite' -G $genome && PASA_transcripts_and_assemblies_to_GFF3.dbi -M 'polishing_PASA.sqlite' -a  > polishing_PASA.sqlite.pasa_assemblies.gff3 && describe_alignment_assemblies_cgi_convert.dbi -M 'polishing_PASA.sqlite'  > polishing_PASA.sqlite.pasa_assemblies_described.txt
```

Load gene annotation.

``` bash
Load_Current_Gene_Annotations.dbi -c pasa_config.txt -g $genome -P EVM.filtered.gff3  > pasa_run.log.dir/output.annot_loading.41077.out
```

Compare gene annotation to assembled mRNA models.

``` bash
cDNA_annotation_comparer.dbi -G $genome --CPU $n_cores -M 'polishing_PASA.sqlite' --MIN_PERCENT_PROT_CODING 30 --MIN_PERCENT_LENGTH_NONFL_COMPARE 70 --MAX_UTR_EXONS 5 --MIN_PERCENT_LENGTH_FL_COMPARE 70 --MIN_PERCENT_ALIGN_LENGTH 70 --MIN_PERCENT_OVERLAP_GENE_REPLACE 90 --MIN_PERID_PROT_COMPARE 50 --MIN_PERCENT_OVERLAP 50 > pasa_run.log.dir/polishing_PASA.sqlite.annotation_compare.out
```

Export updated model annotation.

``` bash
dump_valid_annot_updates.dbi -M 'polishing_PASA.sqlite' -V -R -g $genome > polishing_PASA.sqlite.gene_structures_post_PASA_updates.gff3
```

6.3a.2 - Filter results
-----------------------

Rename gene models.

``` bash
GFF_RenameThemAll.py polished_PASA 00 NN polishing_PASA.sqlite.gene_structures_post_PASA_updates.gff3 > polishing_PASA.sqlite.gene_structures_post_PASA_updates.renamed.gff3 2>renaming.err &
```

Run GFF\_extractor.py.

``` bash
GFF_extract_features.py -p EVM.filtered.polished.clean -a polishing_PASA.sqlite.gene_structures_post_PASA_updates.renamed.gff3 -g $genome > EVM.filtered.polished.cleaning.log
```

6.3a.3 - Move to filtering
--------------------------

Copy files.

``` {.bash}
cp EVM.filtered.polished.clean*fasta EVM.filtered.polished.clean*gff3 ../2_2_8-Filtering/
rename 's:EVM.filtered.polished.clean:gene_models:' ../2_2_8-Filtering/EVM.filtered.polished.clean*
```

Proceed with step [](/bioinforesources/pipelines/annotation/7_-_filtering).