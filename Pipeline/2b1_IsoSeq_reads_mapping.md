2.b.1 - IsoSeq eads mapping
============================

## 2.b.1.0 - Setup

### 2.b.1.0.1 - Define variables

`sample` Iso-Seq sample name.

`n_cores` number of cores.

### 2.b.1.0.2 - Set WD

```bash
cd 2-Annotation/2_0-External_evidences/2_0_2-mRNAs/2_0_2_3-IsoSeq/2_0_2_3_2-IsoSeq_polishing/
```

### 2.b.1.0.3 - Set files and environment.

#### 2.b.1.0.3.1 - Setup environment

``` bash
export PASAHOME=/DATA7/Resources/Tools/PASApipeline-v2.3.3/
export PATH=/DATA7/Resources/Tools/PASApipeline-v2.3.3/bin:/DATA7/Resources/Tools/PASApipeline-v2.3.3/:$PATH

cat isoseq.hq.polished.fasta | sed -i 's:transcript/:'${sample}'.IsoSeq.HQ_:' > isoseq.hq.polished.fasta

ln -s /path/to/genome.fasta .

isoseq_reads=isoseq.hq.polished.fasta
isoseq_reads_names=isoseq.hq.polished.name.txt

grep '^>' $isoseq_reads | sed 's:>::;s: .*::' > $isoseq_reads_names

genome=genome.fasta
```

#### 2.b.1.0.3.2 - Write PASA config file

``` bash
#######################################################
# DB name
DATABASE=IsoSeq_training_PASA.sqlite
 
#######################################################
# Parameters to specify to specific scripts in pipeline
# create a key = "script_name" + ":" + "parameter"
# assign a value as done above.
run_spliced_aligners.pl:-N=5
 
#script validate_alignments_in_db.dbi
validate_alignments_in_db.dbi:--MAX_INTRON_LENGTH=25000
```

#### 2.b.1.0.3.3 - Make PASA commands file

``` bash
Launch_PASA_pipeline.pl -c pasa_config.txt --TRANSDECODER --CPU $n_cores --stringent_alignment_overlap 10 -C -r --transcribed_is_aligned_orient --ALIGNERS gmap,blat --transcripts $isoseq_reads -f $isoseq_reads_names -g ${genome} -I 25000 -x -R > pasa.commands.sh
```

2.b.1.2 - Run PASA
------------------

``` bash
create_sqlite_cdnaassembly_db.dbi -c pasa_config.txt -S 'cdna_alignment_sqliteschema' -r && upload_transcript_data.dbi -M 'IsoSeq_training_PASA.sqlite' -t $isoseq_reads  -f $isoseq_reads_names 

run_spliced_aligners.pl --aligners gmap,blat --genome $genome --transcripts $isoseq_reads -I 25000 -N 1 --CPU $n_cores -N 5 > mapping.log

TransDecoder.LongOrfs -t $isoseq_reads -S  && TransDecoder.Predict -t $isoseq_reads  &

import_spliced_alignments.dbi -M 'IsoSeq_training_PASA.sqlite' -A gmap -g gmap.spliced_alignments.gff3 && import_spliced_alignments.dbi -M 'IsoSeq_training_PASA.sqlite'  -A blat -g blat.spliced_alignments.gff3 && extract_FL_transdecoder_entries.pl $isoseq_reads.transdecoder.gff3 > $isoseq_reads.transdecoder.gff3.fl_accs && update_fli_status.dbi -M 'IsoSeq_training_PASA.sqlite' -f $isoseq_reads.transdecoder.gff3.fl_accs

validate_alignments_in_db.dbi -M 'IsoSeq_training_PASA.sqlite' -g $genome -t $isoseq_reads --MAX_INTRON_LENGTH 25000 --CPU $_n_cores --MAX_INTRON_LENGTH 25000 > alignment.validations.output

update_alignment_status.dbi -M 'IsoSeq_training_PASA.sqlite' < alignment.validations.output  > pasa_run.log.dir/alignment.validation_loading.output && PASA_transcripts_and_assemblies_to_GFF3.dbi -M 'IsoSeq_training_PASA.sqlite' -v -A -P gmap > IsoSeq_training_PASA.sqlite.valid_gmap_alignments.gff3 && PASA_transcripts_and_assemblies_to_GFF3.dbi -M 'IsoSeq_training_PASA.sqlite' -f -A -P gmap > IsoSeq_training_PASA.sqlite.failed_gmap_alignments.gff3 && PASA_transcripts_and_assemblies_to_GFF3.dbi -M 'IsoSeq_training_PASA.sqlite' -v -A -P blat > IsoSeq_training_PASA.sqlite.valid_blat_alignments.gff3 && PASA_transcripts_and_assemblies_to_GFF3.dbi -M 'IsoSeq_training_PASA.sqlite' -f -A -P blat > IsoSeq_training_PASA.sqlite.failed_blat_alignments.gff3 && set_spliced_orient_transcribed_orient.dbi -M 'IsoSeq_training_PASA.sqlite' > pasa_run.log.dir/setting_aligned_as_transcribed_orientation.output

assign_clusters_by_stringent_alignment_overlap.dbi -M IsoSeq_training_PASA.sqlite -L 10 > pasa_run.log.dir/cluster_reassignment_by_stringent_overlap.out && assemble_clusters.dbi -G $genome -M 'IsoSeq_training_PASA.sqlite' -T $n_cores  > IsoSeq_training_PASA.sqlite.pasa_alignment_assembly_building.ascii_illustrations.out && assembly_db_loader.dbi -M 'IsoSeq_training_PASA.sqlite' > pasa_run.log.dir/alignment_assembly_loading.out && subcluster_builder.dbi -G $genome -M 'IsoSeq_training_PASA.sqlite' > pasa_run.log.dir/alignment_assembly_subclustering.out && populate_mysql_assembly_alignment_field.dbi -M 'IsoSeq_training_PASA.sqlite' -G $genome && populate_mysql_assembly_sequence_field.dbi -M 'IsoSeq_training_PASA.sqlite' -G $genome && subcluster_loader.dbi -M 'IsoSeq_training_PASA.sqlite'  < pasa_run.log.dir/alignment_assembly_subclustering.out 

alignment_assembly_to_gene_models.dbi -M 'IsoSeq_training_PASA.sqlite' -G $genome && PASA_transcripts_and_assemblies_to_GFF3.dbi -M '/IsoSeq_training_PASA.sqlite' -a  > IsoSeq_training_PASA.sqlite.pasa_assemblies.gff3

describe_alignment_assemblies_cgi_convert.dbi -M 'IsoSeq_training_PASA.sqlite'  > IsoSeq_training_PASA.sqlite.pasa_assemblies_described.txt

```

2.b.1.3 - Extract gene models on genome
---------------------------------------

``` bash
pasa_asmbls_to_training_set.dbi --pasa_transcripts_fasta IsoSeq_training_PASA.sqlite.assemblies.fasta --pasa_transcripts_gff3 IsoSeq_training_PASA.sqlite.pasa_assemblies.gff3
```
