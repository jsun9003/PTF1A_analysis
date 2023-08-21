
# PTF1A drives multiscale 3D genome rewiring during somatic cell reprogramming into neural stem cells

Genomes are complex 3D structures that are partitioned into chromatin compartments, topologically associating domains (TADs) and loops, and are unique to each cell type. How this higher-order genome organization regulates cell fate transition during differentiation remains poorly understood at present. Here we show how a single non-neural progenitor transcription factor, PTF1A, reorchestrates the 3D genome to control gene expression during fibroblast transdifferentiation into neural stem cells (NSCs). By multiomics analyses integrating the Hi-C data, PTF1A and CTCF DNA-binding profiles, H3K27ac modification, and gene expression, we demonstrate that PTF1A facilitates the switch of chromatin compartment B to compartment A, reinforces insulation by binding to and recruiting CTCF to TADs with weak boundaries, and modifies both inter-TAD and intra-TAD loops. Consequently, these alterations in the 3D genome landscape leads to gene expression changes that drive somatic cell transdifferentiation into NSCs. Moreover, PTF1A mediates H3K27ac deposition to activate enhancers and super-enhancers near weak boundaries, which promotes cell fate transitions. Together, our data implicate 3D genome reorganization as a driving force instrumental for cellular transcription program changes and cell fate transitions, and highlight an essential role for PTF1A in orchestrating multiscale 3D genome remodeling during cell reprogramming.
--------------------------

![figs/overview.jpg](https://github.com/jsun9003/PTF1A_analysis/blob/main/figs/overview.png)

# Preprocessing of RNA-seq

#### Please have the following softwares installed first:
- bowtie2, http://bowtie-bio.sourceforge.net/bowtie2/index.shtml
- samtools, http://www.htslib.org/
   samtools version >= 1.3.1 is required.
- Trim_galore, https://www.bioinformatics.babraham.ac.uk/projects/trim_galore/
- STAR, https://github.com/alexdobin/STAR
- sci-CAR, https://github.com/JunyueC/sci-CAR_analysis
- HiC-Pro, https://github.com/nservant/HiC-Pro
- Higashi, https://github.com/ma-compbio/Higashi
- DeepLoop, https://github.com/JinLabBioinfo/DeepLoop
- Optional: FastQC, https://www.bioinformatics.babraham.ac.uk/projects/fastqc/
- Optional: HiCExplorer, https://hicexplorer.readthedocs.io/en/latest/

# Additional Tutorial
- [Higashi-analysis for HiC (Zhang et al. Nature biotechnology, 2022)](https://github.com/ma-compbio/Higashi)
- [Loop-analysis for HiC (Zhang et al. Nature Genetics, 2022)](https://github.com/JinLabBioinfo/DeepLoop)
- [sci-CAR_analysis for RNA (Cao et al. Science, 2018)](https://github.com/JunyueC/sci-CAR_analysis)

# Analysis of scCARE-seq datasets include the following steps:

## 1. Single cell HiC analysis for the HiC partion
### TrimGalore
`mkdir QualityControl`

`cd QualityControl`

`trim_galore.py -i ../rawdata/*.gz 1>Hi-C.txt 2>Hi-C.log -o Clean &`

### Prepare for HiC-Pro
`cd ../`

`mkdir data`

`cd data`

#e.g. serum_H_132

`mkdir serum_H_132`

`ln -s ../../QualityControl/Clean/ValReads/serum_H_132.1.fq.gz serum_H_132/serum_H_132_R1.fastq.gz`

`ln -s ../../QualityControl/Clean/ValReads/serum_H_132.2.fq.gz serum_H_132/serum_H_132_R2.fastq.gz`

`cd ../`

`mkdir HiC-Pro_mm10`

`cd HiC-Pro_mm10`

`HiC-Pro -i ../data/ -o HiC-Pro-Test -c /data1/jlqu/mboi-mm10-config-scCARE-seq.txt 1>Hi-C-pro-test.txt 2>Hi-C-pro-test.log`

#result summary of HiC-pro

`perl Processing_Hi-C/hicpro_summary_trans.pl HiC-Pro-Test > serum_H_132_summary.txt`

## 2. Single cell RNA-seq analysis for the RNA partion

`sh Processing_RNA/record_scRNA_seq_pipeline.sh`

# Cite

Cite our paper by

```
@article {Qu2023multiscale,
	author = {Jiale Qu and Jun Sun},
	title = {Simultaneous profiling of chromatin architecture and transcription in single cells},
	year={2023},
	publisher = {Nature Publishing Group},
	journal = {Nature Structural & Molecular Biology}
}
```



# Contact

Please contact o.sj@live.com or raise an issue in the github repo with any questions about installation or usage. 
