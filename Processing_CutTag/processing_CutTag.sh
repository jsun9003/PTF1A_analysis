### Download Raw data
mkdir 01.RawData

#step1 QualityControl
mkdir 02_QualityControl
cd 02_QualityControl
trim_galore.py -i ../01.RawData/*.fq.gz -o . 1> RNA.txt 2> RNA.log

### Clean data
cd ..
mkdir 03_CleanData
cd 03_CleanData
ln -s ../02_QualityControl/ValReads/*.fq.gz ./

### step2 Mapping
conda activate hic
#need to change samtools version
cd ..
mkdir 04_Mapping
cd 04_Mapping
bowtie2.pl -p 16 ~/database/hg19/Genome/Genome ../03_CleanData/*.gz -o ./ 1>ChIP-Seq.txt 2>ChIP-Seq.log 

### step3 splitbam
cd ..
mkdir 05_SplitBams
cd 05_SplitBams
for f in ../04_Mapping/*.bam
do
      filename=`basename $f`
      file=${filename/.bam/}
      echo $file
      samtools sort ../04_Mapping/$file.bam --threads 24 -o $file.sort.bam
      samtools rmdup $file.sort.bam $file.rmdup.bam
      samtools view -b -q 30 $file.rmdup.bam -o $file.uniq.bam
      #bamToBed -i $file.uniq.bam  > $file.uniq.bed 
      samtools index $file.uniq.bam
done

for f in *.bam ;do file=${f/.bam/};samtools flagstat $f >$file.flagstat; done


echo -e "sample\tsorted\trmdup\tuniq" >align.stat
for f in *.sort.bam
do
        file=${f/.sort.bam/}
        echo $file
        for type in sort rmdup uniq
        do  grep "QC-passed reads" $file.$type.flagstat|sed "s/ .*//"
        done|sed ':a;N;s/\n/\t/;ta;'
done|sed 'N;s/\n/\t/g'>>align.stat

rm *.rmdup.bam *.sort.bam

#conda deactivate
#BigWig

cd ..
mkdir 06_BigWig
cd 06_BigWig
bamcoverage.pl -i ../05_SplitBams/ -o ./ 1> bamcoverage_ChIPseq.txt 2> bamcoverage_ChIPseq.log

mkdir 07_PeakCalling
cd 07_PeakCalling
mkdir logs
macs2 callpeak -t ../05_SplitBams/Condition.uniq.bam  -c ../05_SplitBams/input.uniq.bam -f BAM  --outdir ./ -n  P784-stat3-cam --verbose 0  -g mm -q 0.05 -m 5 50 1>./logs/Condition.stdout.log  2>./logs/Condition.stderr.log &
