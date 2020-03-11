2.a.2 - Model transcript selection
==================================

## 2.a.2.0 - Setup

### 2.a.2.0.1 - Define variables

`name` name of the genome.

`n_cores` number of cores.

`genome` genome fasta sequence.

### 2.a.2.0.2 - Set WD

```bash
cd 2-Annotation/2_1-Training/2_1_1-Training_set
```

### 2.a.2.0.4 - Set files

``` bash
for file in *transdecoder.clean.gff3 ; do cat $file | awk '$3=="CDS"' > $( basename $file .gff3 ).CDS.gff3 ; done

cat ${name}*clean.CDS.fasta > ${name}.RNAseq_assembly.CDS.fasta
```

### 2.a.2.0.5 - Make blast databases

``` bash
makeblastdb -in ${name}.RNAseq_assembly.CDS.fasta -dbtype nucl
```

2.a.2.1 - Find annotation perfectly matching across all assembled transcriptomes datasets
-----------------------------------------------------------------------------------------

### 2.a.2.1.1 - Perfectly matching CDSs

Self map CDS sequences.

``` bash
blastn -db ${name}.RNAseq_assembly.CDS.fasta -query ${name}.RNAseq_assembly.CDS.fasta -num_threads $n_cores -strand plus -outfmt 5 > ${name}.RNAseq_assembly.CDS.self.xml
```

Obtain identity and coverage.

``` bash
/Tools/blat/blastXmlToPsl ${name}.RNAseq_assembly.CDS.self.xml ${name}.RNAseq_assembly.CDS.self.psl

awk 'BEGIN {print "T_name\tT_nem\t|\tQ_name\tQ_len\t|\tMatches\tMismatches\tT_gaps\tQ_gaps\t|\tT_iden\tQ_iden\t|\tT_cov\tQ_cov"}; {print $14"\t"$15"\t|\t"$10"\t"$11"\t|\t"$1"\t"$2"\t"$8"\t"$6"\t|\t"($1-$2-$8)/$1"\t"($1-$2-$6)/$1"\t|\t"$1/$15"\t"$1/$11}' ${name}.RNAseq_assembly.CDS.self.psl > ${name}.RNAseq_assembly.CDS.blast.cov_iden.txt
```

Obtain perfectly matching pairs.

``` bash
awk 'BEGIN {print "T_name\tT_nem\t|\tQ_name\tQ_len\t|\tMatches\tMismatches\tT_gaps\tQ_gaps\t|\tT_iden\tQ_iden\t|\tT_cov\tQ_cov"}; {print $14"\t"$15"\t|\t"$10"\t"$11"\t|\t"$1"\t"$2"\t"$8"\t"$6"\t|\t"($1-$2-$8)/$1"\t"($1-$2-$6)/$1"\t|\t"$1/$15"\t"$1/$11}' ${name}.RNAseq_assembly.CDS.self.psl | awk -F "\t" '$1!=$4 && $2==$5 && $2==$7 && $12==1 && $13==1 && $15==1 && $16==1' | cut -f 1,4 > ${name}.RNAseq_assembly.CDS.perfect_match.pairs.txt
```

### 2.a.2.1.2 - Perfectly matching intron/exon chains from CDSs annotations

Make a combined annotation.

``` bash
/Tools/gffcompare/gffcompare -p ${name}.RNAseq_assembly -o ${name}.RNAseq_assembly -C -X -D -T *.transdecoder.clean.CDS.gff3
sed -i 's:XLOC_:'${name}'.RNAseq_assembly.mergedlocus:' ${name}.RNAseq_assembly.combined.gtf
```

Find intron/exon structure overlaps.

``` bash
/Tools/gffcompare/gffcompare -p ${name}.RNAseq_assembly.check -o ${name}.RNAseq_assembly.check -r ${name}.RNAseq_assembly.combined.gtf -C -Q -R -X -D  *.transdecoder.clean.CDS.gff3

for file in ${name}.RNAseq_assembly.check.${name}.*tmap; do awk '$3=="="' $file | awk '{print $1"|"$2"\t"$4}' > ${file}.perfect_match ; done

join -j1 -t "   " <(join -j1 -t "       " <(sort -k 1,1 ${name}.RNAseq_assembly.check.${name}.stringtie.transdecoder.clean.CDS.gff3.tmap.perfect_match) <(sort -k 1,1 ${name}.RNAseq_assembly.check.${name}.trinity.dn.transdecoder.clean.CDS.gff3.tmap.perfect_match) | sort -k 1,1) <(sort -k 1,1 ${name}.RNAseq_assembly.check.${name}.trinity.og.transdecoder.clean.CDS.gff3.tmap.perfect_match) > ${name}.RNAseq_assembly.check.perfect_intron_chain
```

### 2.a.2.1.3 - Find annotations perfectly matching intron/exon and CDSs sequences in all transcriptome sets

Compare pair sets.

``` bash
python /Scripts/check_pairs.py -c ${name}.RNAseq_assembly.check.perfect_intron_chain -p ${name}.RNAseq_assembly.CDS.perfect_match.pairs.txt > ${name}.RNAseq_assembly.check.perfect_intron_chain.perfect_cds_match.txt
```

Filter out non matching models end extract a single ID for the model (stringtie model).

``` bash
grep -v FALSE ${name}.RNAseq_assembly.check.perfect_intron_chain.perfect_cds_match.txt | sed 's:|.*::' | sort | uniq -c | awk '$1=1 {print $2}' > ${name}.RNAseq_assembly.check.perfect_intron_chain.perfect_cds_match.single_model.list

grep -wFf ${name}.RNAseq_assembly.check.perfect_intron_chain.perfect_cds_match.single_model.list ${name}.RNAseq_assembly.check.perfect_intron_chain.perfect_cds_match.txt > ${name}.RNAseq_assembly.check.perfect_intron_chain.perfect_cds_match.single_model.txt

grep -wFf ${name}.RNAseq_assembly.check.perfect_intron_chain.perfect_cds_match.single_model.list ${name}.RNAseq_assembly.check.perfect_intron_chain.perfect_cds_match.txt | cut -f 1 > ${name}.RNAseq_assembly.check.perfect_intron_chain.perfect_cds_match.single_model.ids

for file in *perfect_match; do grep -wFf ${name}.RNAseq_assembly.check.perfect_intron_chain.perfect_cds_match.single_model.ids $file > ${file}.selected ; done

grep -wFf <(cut -f 2 ${name}.RNAseq_assembly.check.${name}.stringtie.transdecoder.clean.CDS.gff3.tmap.perfect_match.selected) ${name}.stringtie.transdecoder.clean.gff3 | awk '$3=="CDS" || $3=="mRNA"' | sed 's:;Name.*::' | sed '/\tmRNA\t/ s:\(.*\)mRNA\(.*ID=\)\(.*Parent=\)\(.*\):\1gene\2\4\n\1mRNA\2\3\4;Parent=\4:' | sed '/\tCDS\t/ s:\(.*\)CDS\(.*\)ID=.*\(.*Parent=\)\(.*\):\1exon\2Parent=\4;ID=\4\n\1CDS\2Parent=\4;ID=\4:'| awk 'BEGIN {OFS="\t"} {if ($3=="exon") $NF=$NF".exon."NR ; if ($3=="CDS") $NF=$NF".cds."NR ; print $0 }' > ${name}.stringtie.transdecoder.clean.CDS.selected.gff3

python /Scripts/GFF_extract_features.py -g $genome -a ${name}.stringtie.transdecoder.clean.CDS.selected.gff3 -p tmp -lcin 2> ${name}.stringtie.transdecoder.clean.CDS.selected.log
```

### 2.a.2.1.4 - Select models conserved among other species

 Run blast search against a dedicated RefSeq protein dataset (in the example, plants proteins). 

``` bash
blastp -db RefSeq_Plants.protein.faa -query tmp.protein.fasta -num_threads $n_cores -outfmt 5 > tmp.protein.to.RefSeq_Plants.xml
```

Extract alignments identity, coverage, and description, then check the distribution at increasing identity and coverage theresholds.

``` bash
python /Scripts/mapGOs.py -m refseq2go.txt tmp.protein.to.RefSeq_Plants.xml | awk -F "\t" 'BEGIN {OFS="\t"; OFS="\t"; print "Query","Q_len","Q_start","Q_stop","|","Target","T_len","T_start","T_stop","|","e-value","Matches","Mismatches","Gaps","Iden","Q_cov","T_cov","|","Description","|","GO"} {print $1,$23,$7,$8,"|",$2,$24,$9,$10,"|",$11,$4,$5,$6,$3,100*($4/$23),100*($4/$24),"|",$25,"|",$26}' > tmp.protein.to.RefSeq_Plants.tab
```

Find annotated models corresponding to to potential transposases and remove them from the set.

``` bash
grep -i 'transpos' tmp.protein.to.RefSeq_Plants.tab  > tmp.protein.to.RefSeq_Plants.transposable_elements

grep -i 'transpos' tmp.protein.to.RefSeq_Plants.tab | cut -f 1 | sort -u > tmp.protein.to.RefSeq_Plants.transposable_elements.list

grep -vwxFf tmp.protein.to.RefSeq_Plants.transposable_elements.list <(awk -v thr=90 ' BEGIN {getline} { if ($15>thr && $16>thr && $17>thr && $15<120 && $16<120 && $17<120 ) {print $1} }' tmp.protein.to.RefSeq_Plants.tab | sort -u ) > tmp.protein.to.RefSeq_Plants.iden_cov.g90.no_repeat.tab

grep -wFf tmp.protein.to.RefSeq_Plants.iden_cov.g90.no_repeat.tab tmp.gff3 > tmp.${name}.gene_models.gff3
```

### 2.a.2.1.5 - Remove model redundancy and obtain the final training set

Align all-vs-all the good proteins.

``` bash
python /Scripts/getFastaFromIds.py tmp.protein.to.RefSeq_Plants.iden_cov.g90.no_repeat.tab tmp.protein.fasta > tmp.protein.to.RefSeq_Plants.iden_cov.g90.no_repeat.protein.fasta

makeblastdb -in tmp.protein.to.RefSeq_Plants.iden_cov.g90.no_repeat.protein.fasta -dbtype prot 

blastp -db tmp.protein.to.RefSeq_Plants.iden_cov.g90.no_repeat.protein.fasta -query tmp.protein.to.RefSeq_Plants.iden_cov.g90.no_repeat.protein.fasta -num_threads $n_cores -outfmt "7 qseqid qlen qstart qend qframe qcovhsp sseqid slen sstart send sframe length nident mismatch gaps bitscore evalue " > tmp.protein.to.RefSeq_Plants.iden_cov.g90.no_repeat.protein.fasta.self_blast.tab
```

Obtain meaningful pairs (coverage ≥ 95% and ≥95%), clusterize them and keep just one representative for each cluster.

``` bash
less -S tmp.protein.to.RefSeq_Plants.iden_cov.g90.no_repeat.protein.fasta.self_blast.tab | grep -v '^#' |awk -F "\t" 'BEGIN {OFS="\t"} {print $1,$7,100*($12/$8),100*($13/$8)}' | awk '$3>=95 && $4>=95' > tmp.protein.to.RefSeq_Plants.iden_cov.g90.no_repeat.protein.fasta.self_blast.iden_cov.ge95.txt

python /Scripts/filter_most_representative.py tmp.protein.to.RefSeq_Plants.iden_cov.g90.no_repeat.protein.fasta.self_blast.iden_cov.ge95.txt > tmp.protein.to.RefSeq_Plants.iden_cov.g90.no_repeat.protein.fasta.self_blast.iden_cov.ge95.representatives 2> tmp.protein.to.RefSeq_Plants.iden_cov.g90.no_repeat.protein.fasta.self_blast.iden_cov.ge95.clusters

grep -wFf tmp.protein.to.RefSeq_Plants.iden_cov.g90.no_repeat.protein.fasta.self_blast.iden_cov.ge95.representatives tmp.${name}.gene_models.gff3 | awk '$3=="CDS" || $3=="mRNA"' | sed '/\tmRNA\t/ s:\(.*\)mRNA\(.*ID=\)\(.*Parent=\)\(.*\):\1gene\2\4\n\1mRNA\2\3\4:' | sed '/\tCDS\t/ s:\(.*\)CDS\(.*\)Parent=\(.*\);ID=\(.*\)cds\(.*\):\1exon\2Parent=\3;ID=\4exon\5\n\1CDS\2Parent=\3;ID=\4cds\5:' > tmp.no_redundant.${name}.gene_models.gff3
```

``` bash
python /Scripts/GFF_extract_features.py -g $genome -a tmp.no_redundant.${name}.gene_models.gff3 -p tmp.no_redundant.clean.gene_models -nlcmi 
```

2.a.2.2 - SNAP validation of exon structures
--------------------------------------------

> To be added.