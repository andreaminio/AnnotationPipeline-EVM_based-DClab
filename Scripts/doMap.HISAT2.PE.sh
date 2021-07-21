#!/bin/bash

export PATH=$(realpath Tools/samtools-1.3.1/):$PATH

Tools/hisat2-2.1.0/hisat2 -x $1 -1 $2 -2 $3 --very-sensitive -t -p $5 2>err | samtools view -bS -T $1 - | samtools sort -l 9 -@ $5 -m 1500M -o $4 -

samtools index $4
