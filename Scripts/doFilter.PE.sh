indir=$(pwd)
outdir=$1
trimmomatic="/DATA/users/aminio/Assembly_tools/Tools/Trimmomatic-0.36/trimmomatic-0.36.jar"
adapters="/DATA/users/aminio/Assembly_tools/Tools/Trimmomatic-0.36/adapters/TruSeq3-PE-2.fa"


	for file in ${indir}/*_2.fastq.gz ; do 
		name=$(basename $file _2.fastq.gz)
		echo $name
		java -jar $trimmomatic PE \
			-threads 4 \
			-validatePairs \
			${name}_1.fastq.gz \
			${name}_2.fastq.gz \
			-baseout $outdir/${name}.fil \
			ILLUMINACLIP:$adapters:2:30:10 \
			LEADING:7 \
			TRAILING:7 \
			SLIDINGWINDOW:10:20 \
			MINLEN:36
		rename s:$:.fastq: $outdir/${name}.fil*
                pigz -9v -p 4 $outdir/${name}.fil*
	done

