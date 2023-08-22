### 1. download Raw data
Put fastq data in 01_RawData
### 2. Quality Control

mkdirt 02_QualityControl
cd 02_QualityControl

trim_galore.py -i ../01_RawData/*.fq.gz -o . 1> RNA.txt 2> RNA.log

cd ..

### 3. Mapping
mkdir CleanData
ln -s ./02_QualityControl/ValReads/*.fq.gz ./CleanData

mkdir 03_Mapping
ln -s ~/juns/database/hg19/Genome
cd 03_Mapping
star2.pl ../Genome ../CleanData/*.gz -e -p 12 -g ../Genome/Genes.gtf 1>rna-seq.txt 2>rna-seq.log
cd ..

### 4.Quantification
mkdir 04_Quantification
cd 04_Quantification
htseq-count.pl -o CountsLength -r ~/juns/database/hg19/Genome/Genes.gtf ../03_Mapping/Bams/*.bam -l
cd ..

### 5. RPKM
mkdir 05_RPKM
counts2rpkm.pl ../04_Quantification/CountsLength/Total.txt