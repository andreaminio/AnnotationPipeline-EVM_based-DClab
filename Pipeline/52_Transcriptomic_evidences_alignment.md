5.2 - Transcriptomic evidences alignment
========================================

5.2.0 - Setup
-------------

### 5.2.0.1 - Define variables

`n_cores` number of cores.

`genome` genome fasta sequence.

### 5.2.0.2 - Set WD

```bash
cd 2-Annotation/2_2-Prediction/2_2_4-Transcript_mapping/
```

### 5.2.0.3 -Set files and environment

#### 5.2.0.3.1 - Decompress external DBs datasets

``` bash
zcat ../../2_0-External_evidences/2_0_2-mRNAs/2_0_2_1-External_databases/*fasta.gz > ../../2_0-External_evidences/2_0_2-mRNAs/external_db_transcripts.fasta
```

#### 5.2.0.3.2 - Concatenate mRNAs from independent studies (`2_0-External_evidences`) with assembled transcripts from RNAseq experiments

``` bash
cat ../../2_0-External_evidences/2_0_2-mRNAs/*fasta > all_transcripts.fasta
```

#### 5.2.0.3.3 - Generate the configuration file \'\'pasa\_config.txt \'\'.

``` {.bash}
vim pasa_config.txt
```

```bash
#######################################################
# DB name
DATABASE=trainig_PASA.sqlite
 
#######################################################
# Parameters to specify to specific scripts in pipeline
# create a key = "script_name" + ":" + "parameter"
# assign a value as done above.
run_spliced_aligners.pl:-N=5
 
#script validate_alignments_in_db.dbi
validate_alignments_in_db.dbi:--MAX_INTRON_LENGTH=25000
```

#### 5.2.0.3.4 - Setup the environment

``` bash
export PASAHOME=/DATA7/Resources/Tools/PASApipeline-v2.3.3/
export PATH=/DATA7/Resources/Tools/PASApipeline-v2.3.3/bin:/DATA7/Resources/Tools/PASApipeline-v2.3.3/:$PATH
```

## 5.2.1 - Run PASA

``` bash
create_sqlite_cdnaassembly_db.dbi -c pasa_config.txt -S 'cdna_alignment_sqliteschema' -r
samtools faidx ${genome}

samtools faidx all_transcripts.fasta

upload_transcript_data.dbi -M 'trainig_PASA.sqlite' -t all_transcripts.fasta  -f NULL 
run_spliced_aligners.pl --aligners gmap,blat --genome ${genome} --transcripts all_transcripts.fasta -I 25000 -N 1 --CPU $n_cores -N 5

/import_spliced_alignments.dbi -M 'trainig_PASA.sqlite'  -A gmap -g gmap.spliced_alignments.gff3

import_spliced_alignments.dbi -M 'trainig_PASA.sqlite'  -A blat -g blat.spliced_alignments.gff3

TransDecoder.LongOrfs -t all_transcripts.fasta  

TransDecoder.Predict -t all_transcripts.fasta 

extract_FL_transdecoder_entries.pl all_transcripts.fasta.transdecoder.gff3 > all_transcripts.fasta.transdecoder.gff3.fl_accs

update_fli_status.dbi -M 'trainig_PASA.sqlite' -f all_transcripts.fasta.transdecoder.gff3.fl_accs

validate_alignments_in_db.dbi -M 'trainig_PASA.sqlite' -g ${genome} -t all_transcripts.fasta --MAX_INTRON_LENGTH 25000 --CPU $n_cores --MAX_INTRON_LENGTH 25000 > alignment.validations.output

update_alignment_status.dbi -M 'trainig_PASA.sqlite' < alignment.validations.output  > pasa_run.log.dir/alignment.validation_loading.output

PASA_transcripts_and_assemblies_to_GFF3.dbi -M 'trainig_PASA.sqlite' -v -A -P gmap > trainig_PASA.sqlite.valid_gmap_alignments.gff3

PASA_transcripts_and_assemblies_to_GFF3.dbi -M 'trainig_PASA.sqlite' -v -A -P gmap -B  > trainig_PASA.sqlite.valid_gmap_alignments.bed

PASA_transcripts_and_assemblies_to_GFF3.dbi -M 'trainig_PASA.sqlite' -v -A -P gmap -T  > trainig_PASA.sqlite.valid_gmap_alignments.gtf

PASA_transcripts_and_assemblies_to_GFF3.dbi -M 'trainig_PASA.sqlite' -f -A -P gmap > trainig_PASA.sqlite.failed_gmap_alignments.gff3

PASA_transcripts_and_assemblies_to_GFF3.dbi -M 'trainig_PASA.sqlite' -f -A -P gmap -B  > trainig_PASA.sqlite.failed_gmap_alignments.bed

PASA_transcripts_and_assemblies_to_GFF3.dbi -M 'trainig_PASA.sqlite' -f -A -P gmap -T  > trainig_PASA.sqlite.failed_gmap_alignments.gtf

PASA_transcripts_and_assemblies_to_GFF3.dbi -M 'trainig_PASA.sqlite' -v -A -P blat > trainig_PASA.sqlite.valid_blat_alignments.gff3

PASA_transcripts_and_assemblies_to_GFF3.dbi -M 'trainig_PASA.sqlite' -v -A -P blat -B  > trainig_PASA.sqlite.valid_blat_alignments.bed

PASA_transcripts_and_assemblies_to_GFF3.dbi -M 'trainig_PASA.sqlite' -v -A -P blat -T  > trainig_PASA.sqlite.valid_blat_alignments.gtf

PASA_transcripts_and_assemblies_to_GFF3.dbi -M 'trainig_PASA.sqlite' -f -A -P blat > trainig_PASA.sqlite.failed_blat_alignments.gff3

PASA_transcripts_and_assemblies_to_GFF3.dbi -M 'trainig_PASA.sqlite' -f -A -P blat -B  > trainig_PASA.sqlite.failed_blat_alignments.bed

PASA_transcripts_and_assemblies_to_GFF3.dbi -M 'trainig_PASA.sqlite' -f -A -P blat -T  > trainig_PASA.sqlite.failed_blat_alignments.gtf

assign_clusters_by_stringent_alignment_overlap.dbi -M trainig_PASA.sqlite -L 30 > pasa_run.log.dir/cluster_reassignment_by_stringent_overlap.out

assemble_clusters.dbi -G ${genome}  -M 'trainig_PASA.sqlite'  -T $n_cores  > trainig_PASA.sqlite.pasa_alignment_assembly_building.ascii_illustrations.out

assembly_db_loader.dbi -M 'trainig_PASA.sqlite' > pasa_run.log.dir/alignment_assembly_loading.out

subcluster_builder.dbi -G ${genome} -M 'trainig_PASA.sqlite'  > pasa_run.log.dir/alignment_assembly_subclustering.out

populate_mysql_assembly_alignment_field.dbi -M 'trainig_PASA.sqlite' -G ${genome}

populate_mysql_assembly_sequence_field.dbi -M 'trainig_PASA.sqlite' -G ${genome}

subcluster_loader.dbi -M 'trainig_PASA.sqlite'  < pasa_run.log.dir/alignment_assembly_subclustering.out 

alignment_assembly_to_gene_models.dbi -M 'trainig_PASA.sqlite' -G ${genome}

PASA_transcripts_and_assemblies_to_GFF3.dbi -M 'trainig_PASA.sqlite' -a  > trainig_PASA.sqlite.pasa_assemblies.gff3

PASA_transcripts_and_assemblies_to_GFF3.dbi -M 'trainig_PASA.sqlite' -a -B  > trainig_PASA.sqlite.pasa_assemblies.bed

PASA_transcripts_and_assemblies_to_GFF3.dbi -M 'trainig_PASA.sqlite' -a -T  > trainig_PASA.sqlite.pasa_assemblies.gtf

describe_alignment_assemblies_cgi_convert.dbi -M 'trainig_PASA.sqlite'  > trainig_PASA.sqlite.pasa_assemblies_described.txt
```

Edit \"vendor\" field on GFF3 files and copy them in the folder where EVM must be run.

``` bash
sed 's:${genome}\.gmap:gmap:' gmap.spliced_alignments.gff3 > ../2_2_6-EVM/transcript_alignment.gmap.gff3

cp blat.spliced_alignments.gff3 ../2_2_6-EVM/transcript_alignment.blat.gff3

cat trainig_PASA.sqlite.pasa_assemblies.gff3 | sed 's:assembler-trainig_PASA.sqlite:PASA_assemblies:' > ../2_2_6-EVM/transcript_alignment.pasa.gff3
```

5.2.2 - Magicblast
------------------

Create blast database.

``` bash
makeblastdb -in $genome -dbtype nucl -parse_seqids
```

Run Megablast mapping.

``` bash
magicblast -query all_transcripts.fasta -db ${genome} -outfmt sam -num_threads 10 -no_unaligned > transcript_alignment.magicblast.mapped.sam
```

Filter alignments keeping only the ones with coverage \>70% and identity \>70%.

``` bash
python doFilter_bam.read_coverage_identity.py -s transcript_alignment.magicblast.mapped.sam -o transcript_alignment.magicblast.mapped.filtered.sam -c 70 -i 70 2> filtering.log
```

Convert file to alignment gff3 format.

``` bash
samtools faidx ${genome}

bedtools bamtobed -i <(samtools view -bS transcript_alignment.magicblast.mapped.filtered.sam) -split -bed12 > transcript_alignment.magicblast.mapped.bed12

bedToPsl ${genome}.fai transcript_alignment.magicblast.mapped.bed12 transcript_alignment.magicblast.mapped.psl

cat transcript_alignment.magicblast.mapped.psl  | ~/Assembly_tools/Tools/PASApipeline-2.3.0/misc_utilities/blat_to_alignment_gff3.pl | sed 's:blat:magicblast:' > transcript_alignment.magicblast.mapped.gff3

cp  transcript_alignment.magicblast.mapped.gff3  ../2_2_6-EVM/
```
