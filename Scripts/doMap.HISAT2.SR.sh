#!/bin/bash

export PATH=$(realpath /DATA7/Resources/Tools/samtools-1.3.1/):$PATH

/DATA7/Resources/Tools/hisat2-2.1.0/hisat2 -x $1 -U $2 --very-sensitive -t -p $4 2>err | samtools view -bS -T $1 - | samtools sort -l 9 -@ $4 -m 1500M -o $3 -

samtools index $3
