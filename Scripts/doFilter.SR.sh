indir=$(pwd)
outdir=$1
trimmomatic="Tools/Trimmomatic-0.36/trimmomatic-0.36.jar"
adapters="Tools/Trimmomatic-0.36/adapters/TruSeq3-PE-2.fa"


	for file in ${indir}/*.fastq.gz ; do 
		echo $file ;
		java -jar $trimmomatic SE \
			$file \
			$outdir/$(basename $file .fastq.gz).fil.fastq.gz \
			ILLUMINACLIP:$adapters:2:30:10 \
			LEADING:7 \
			TRAILING:7 \
			SLIDINGWINDOW:10:20 \
			MINLEN:36
	done

