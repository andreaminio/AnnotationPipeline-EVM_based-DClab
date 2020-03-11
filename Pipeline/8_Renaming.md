8 - Renaming
============

## 8.0 - Setup

### 8.0.1 - Define variables

`new_name` prefix of the species.

`version` version of the annotation.

`name` name of the genome.

### 8.0.2 - Set WD

```bash
cd 2-Annotation/2_2-Prediction/2_2_8-Filtering/
```

## 8.1 - Rename

Generate gene annotation with updated nomenclature.

``` bash
python /Scripts/GFF_RenameThemAll.py $new_name $version V gene_models.filtered.gff3 > gene_models.filtered.renamed.gff3 2> gene_models.filtered.renaming.log
```

Correct names in both GFF3 and conversion log file.

``` bash
vim *.rena*
```

Copy the annotation to functional annotation folder.

``` bash
cp gene_models.filtered.renamed.gff3 ../2_2_9-Functional_annotation/$name.gff3
```

