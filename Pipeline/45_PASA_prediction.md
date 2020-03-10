4.5 - PASA prediction
=====================

## 4.5.0 - Setup

### 4.5.0.1 - Set WD

```bash
cd 2-Annotation/2_2-Prediction/2_2_4-Transcript_mapping/
```

4.5.1 - Predict
---------------

The process starts from the results of PASA pipeline that has been run also for transcriptomic evidences mapping. Follow the instruction at [5.2 - Transcriptomic evidences alignment](5.2 - Transcriptomic evidences alignment) before running this.

Identify CDS regions in the PASA assembled gene models.

``` bash
pasa_asmbls_to_training_set.dbi --pasa_transcripts_fasta trainig_PASA.sqlite.assemblies.fasta --pasa_transcripts_gff3 trainig_PASA.sqlite.pasa_assemblies.gff3
```

Edit the vendor column of GFF3 file and copy it into EVM folder.

``` bash
cat trainig_PASA.sqlite.assemblies.fasta.transdecoder.genome.gff3 | sed 's:\~\~:-:g;s:transdecoder:PASA_transdecoder:;s:;Name=.*::' > ../2_2_6-EVM/prediction.pasa.gff3
```

4.5.2 - Copy
------------

Copy into Prediction folder.

``` bash
cp -r trainig_PASA.sqlite.assemblies.fasta.transdecoder* ../2_2-Prediction/2_2_3-Prediction/2_2_3_5-PASA/
```
