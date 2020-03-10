2.b.2 - Model transcript selection
==================================

## 2.b.2.0 - Setup

### 2.b.2.0.1 - Define variables

`n_cores` number of cores.

`name` name of the genome.

`genome` genome fasta sequence.

### 2.b.2.0.2 - Set WD

```bash
cd 2-Annotation/2_1-Training/2_1_1-Training_set/
```

> Polished reads need to be copied here.

2.b.2.1 - Select models conserved among other species
-----------------------------------------------------

``` bash
blastp -db RefSeq_Plants.protein.faa -query IsoSeq_training_PASA.sqlite.assemblies.fasta.transdecoder.pep -num_threads $n_cores -outfmt 5 > tmp.protein.to.RefSeq_Plants.xml
```

Extract alignments identity, coverage, and description, then check the distribution at increasing identity and coverage theresholds.

``` bash
python mapGOs.py -m refseq2go.txt tmp.protein.to.RefSeq_Plants.xml | awk -F "\t" 'BEGIN {OFS="\t"; OFS="\t"; print "Query","Q_len","Q_start","Q_stop","|","Target","T_len","T_start","T_stop","|","e-value","Matches","Mismatches","Gaps","Iden","Q_cov","T_cov","|","Description","|","GO"} {print $1,$23,$7,$8,"|",$2,$24,$9,$10,"|",$11,$4,$5,$6,$3,100*($4/$23),100*($4/$24),"|",$25,"|",$26}' > tmp.protein.to.RefSeq_Plants.tab
```

Find annotated models corresponding to to potential transposases and remove them from the set.

``` bash
grep -i 'transpos' tmp.protein.to.RefSeq_Plants.tab  > tmp.protein.to.RefSeq_Plants.transposable_elements

grep -i 'transpos' tmp.protein.to.RefSeq_Plants.tab | cut -f 1 | sort -u > tmp.protein.to.RefSeq_Plants.transposable_elements.list

grep -vwxFf tmp.protein.to.RefSeq_Plants.transposable_elements.list <(awk -v thr=90 ' BEGIN {getline} { if ($15>thr && $16>thr && $17>thr && $15<120 && $16<120 && $17<120 ) {print $1} }' tmp.protein.to.RefSeq_Plants.tab | sort -u ) > tmp.protein.to.RefSeq_Plants.iden_cov.g90.no_repeat.tab

grep -wFf tmp.protein.to.RefSeq_Plants.iden_cov.g90.no_repeat.tab IsoSeq_training_PASA.sqlite.assemblies.fasta.transdecoder.genome.gff3 > tmp.IsoSeq_training_PASA.sqlite.gene_models.gff3
```

2.b.2.2 - Remove model redundancy and obtain the final training set
-------------------------------------------------------------------

Align all-vs-all the good proteins.

``` bash
getFastaFromIds.py tmp.protein.to.RefSeq_Plants.iden_cov.g90.no_repeat.tab IsoSeq_training_PASA.sqlite.assemblies.fasta.transdecoder.pep > tmp.protein.to.RefSeq_Plants.iden_cov.g90.no_repeat.protein.fasta

makeblastdb -in tmp.protein.to.RefSeq_Plants.iden_cov.g90.no_repeat.protein.fasta -dbtype prot 

blastp -db tmp.protein.to.RefSeq_Plants.iden_cov.g90.no_repeat.protein.fasta -query tmp.protein.to.RefSeq_Plants.iden_cov.g90.no_repeat.protein.fasta -num_threads $n_cores -outfmt "7 qseqid qlen qstart qend qframe qcovhsp sseqid slen sstart send sframe length nident mismatch gaps bitscore evalue " > tmp.protein.to.RefSeq_Plants.iden_cov.g90.no_repeat.protein.fasta.self_blast.tab
```

Obtain meaningful pairs (coverage ≥ 95% and ≥95%), clusterize them and keep just one representative for each cluster.

``` bash
less -S tmp.protein.to.RefSeq_Plants.iden_cov.g90.no_repeat.protein.fasta.self_blast.tab | grep -v '^#' |awk -F "\t" 'BEGIN {OFS="\t"} {print $1,$7,100*($12/$8),100*($13/$8)}' | awk '$3>=95 && $4>=95' > tmp.protein.to.RefSeq_Plants.iden_cov.g90.no_repeat.protein.fasta.self_blast.iden_cov.ge95.txt

python filter_most_representative.py tmp.protein.to.RefSeq_Plants.iden_cov.g90.no_repeat.protein.fasta.self_blast.iden_cov.ge95.txt > tmp.protein.to.RefSeq_Plants.iden_cov.g90.no_repeat.protein.fasta.self_blast.iden_cov.ge95.representatives 2> tmp.protein.to.RefSeq_Plants.iden_cov.g90.no_repeat.protein.fasta.self_blast.iden_cov.ge95.clusters

grep -wFf tmp.protein.to.RefSeq_Plants.iden_cov.g90.no_repeat.protein.fasta.self_blast.iden_cov.ge95.representatives tmp.IsoSeq_training_PASA.sqlite.gene_models.gff3 | awk '$3=="CDS" || $3=="mRNA"' | sed '/\tmRNA\t/ s:\(.*\)mRNA\(.*ID=\)\(.*Parent=\)\(.*\):\1gene\2\4\n\1mRNA\2\3\4:' | sed '/\tCDS\t/ s:\(.*\)CDS\(.*\)Parent=\(.*\);ID=\(.*\)cds\(.*\):\1exon\2Parent=\3;ID=\4exon\5\n\1CDS\2Parent=\3;ID=\4cds\5:' > tmp.${name}.no_redundant.gene_models.gff3
```

``` bash
GFF_extract_features.py -g $genome -a tmp.${name}.no_redundant.gene_models.gff3 -p tmp.${name}.no_redundant.clean.gene_models -nlcmi > log
```

2.b.2.3 - SNAP validation of exon structures
--------------------------------------------

Convert GFF3 files to ZFF format.

``` bash
cat <(cat tmp.${name}.no_redundant.clean.gene_models.gff3 ; echo "#FASTA" ; cat $genome) > tmp.${name}.no_redundant.clean.gene_models.SNAP.gff3

maker2zff -n tmp.${name}.no_redundant.clean.gene_models.SNAP.gff3 2> /dev/null
rm genome.dna

for id in $(grep '^>' genome.ann | sed 's:>::'); do echo $id; /DATA7/Resources/Scripts/getFastaFromIds.py <(echo $id) $genome | sed 's/.\{60\}/&\n/g' >> genome.dna ; done
```

Validate file.

``` bash
fathom genome.ann genome.dna -validate > validate.log 2>validate.err
```

Find genes corresponding to models with errors.

``` bash
grep error validate.log | cut -f 2 -d ' ' > MODEL.issues.txt

cat MODEL.issues.txt | while read line; do grep -n ${line}$ genome.ann | grep Einit; done > MODEL.issues.coords.txt

cat MODEL.issues.coords.txt | while read line; do myoutline=$(echo $line | sed 's/ /\t/g'); myline=$(echo $line | cut -f 1 -d ":"); myID=$(sed -n "1,${myline}p" genome.ann | grep ">" | tail -n 1 | sed 's/>//'); echo -e "${myoutline}\t${myID}"; done > MODEL.issues.IDs.txt
cat MODEL.issues.IDs.txt | while read line; do myID=$(echo $line | sed 's/ /\t/g' | cut -f 5); mystart=$(echo $line | sed 's/ /\t/g' | cut -f 2); myend=$(echo $line | sed 's/ /\t/g' | cut -f 3); awk -v mystart="$mystart" -v myend="$myend" '$3=="CDS" && $4==mystart && $5==myend' tmp.${name}.no_redundant.clean.gene_models.gff3 | cut -f 9 ; done | sed 's:.*Parent=::' > tmp.${name}.no_redundant.clean.models_to_remove.txt
```

Remove models not passing validation and clean dataset.

``` bash
grep -vFf tmp.${name}.no_redundant.clean.models_to_remove.txt tmp.${name}.no_redundant.clean.gene_models.gff3  > tmp.${name}.no_redundant.clean.pass.gene_models.gff3

GFF_extract_features.py -g $genome -a tmp.${name}.no_redundant.clean.pass.gene_models.gff3 -p ${name}.gene_models_for_training -in > log
```
