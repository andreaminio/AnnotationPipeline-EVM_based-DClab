0.3.1 - IsoSeq reads extraction
========================================

## 0.3.1.0 - Setup

### 0.3.1.0.1 - Define variables

`n_cores` number of cores.

`sample` Iso-Seq sample name.

### 0.3.1.0.2 - Set WD

```bash
cd 2_0-External_evidences/2_0_2-mRNAs/2_0_2_3-IsoSeq/2_0_2_3_1-IsoSeq_reads/
```

0.3.1.1 - Full-Length Non-Chimeric reads extraction
---------------------------------------------------

Write a FASTA file with the 5\' (forward) and 3\' (forward) barcodes used (match the names in the demultiplexed sample).

```bash
vim primers.fasta
```

Extract FLNC reads dataset.

```bash
isoseq3 refine --require-polya --num-threads $n_cores --log-level DEBUG --log-file isoseq3.refine.log -v fl.datastore.bc1008_5p--bc1008_3p.bam primers.fasta ${sample}.flnc.bam > isoseq3.refine.err
```

## 0.3.1.2 - Clustering and polishing of isoforms

Run Clustering.

```bash
isoseq3 cluster --num-threads $n_cores --log-level DEBUG --log-file isoseq3.cluster.log -v --use-qvs ${sample}.flnc.bam --singletons  ${sample}.polished.bam > isoseq3.cluster.err
```

0.3.1.3 - Quality Control
-------------------------

Extract FASTA.

```bash
for file in *.bam ; do samtools fasta ${file} > ${file}.fasta; done
```

Run Stats.

```bash
for file in *fasta ; do bash reads_statistics.sh ${file} > ${file}.stats; done
```

Extract Read lengths. 

```bash
for file in *.fasta ; do python getLengthFromFasta.py ${file} > ${file}.len; done
```

FASTQC.

```bash
fastqc --extract -t $n_cores *.bam
```

0.3.1.4 - Export HQ reads
-------------------------

- **Transcripts**

  Export FASTA.

  ```bash
  cat ${sample}.polished.hq.fasta | sed 's:>:>IsoSeq_HQ.:;s:/:_:g;s: .*::' > ../../${sample}.IsoSeq_HQ.fasta
  ```

- **Proteins**

  - Run transdecoder.

  ```bash
  /Tools/TransDecoder-3.0.1/util/TransDecoder.LongOrfs -t ${sample}.polished.hq.fasta -m 30 -S
  
  /Tools/TransDecoder-3.0.1/util/TransDecoder.Predict -t ${sample}.polished.hq.fasta --cpu $n_cores --single_best_orf
```
  
 - Export FASTA.
  
  ```bash
  cat ${sample}.polished.hq.fasta.transdecoder.pep | sed 's:>Gene\.[0-9]*\:\::>IsoSeq_HQ.:;s:\:.*::;s:/:_:g' > ../../../2_0_1-Proteins/${sample}.IsoSeq_HQ.prot.fasta 
  ```
