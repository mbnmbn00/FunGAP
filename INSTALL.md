# Installation of FunGAP v1.1.2

** Last updated: May 26, 2025*

**FunGAP is freely available for academic use. For the commerical use or license of FunGAP, please contact In-Geol Choi (email: igchoi (at) korea.ac.kr). Please, cite the following reference**

Reference: Byoungnam Min  Igor V Grigoriev  In-Geol Choi, FunGAP: Fungal Genome Annotation Pipeline using evidence-based gene model evaluation (2017), Bioinformatics, Volume 33, Issue 18, Pages 2936–2937, https://doi.org/10.1093/bioinformatics/btx353

<hr>

Please don't hesitate to post on *Issues* or contact me (mbnmbn00@gmail.com) for help.
These steps were tested in the freshly installed Ubuntu 24.04.2 LTS.

<br />

# Install FunGAP using Docker

Using Docker is the most reliable and robust way to install FunGAP. [Please follow the instruction](docker/README.md).

<br />

# Install FunGAP using Micromamba

Although we recommend using Docker, some workspaces are not available for Docker (e.g., HPC). Please use the following instruction for micromamba-based FunGAP installation.

## 0. FunGAP requirements

### 0.1. Required softwares (and tested versions)

1. [Hisat2](https://ccb.jhu.edu/software/hisat2/index.shtml) v2.2.1
1. [Trinity](https://github.com/trinityrnaseq/trinityrnaseq) v2.15.2
1. [RepeatModeler](http://www.repeatmasker.org/RepeatModeler/) v2.0.6
1. [Maker](http://www.yandell-lab.org/software/maker.html) v3.01.03
1. [GeneMark-ES/ET](http://topaz.gatech.edu/GeneMark/license_download.cgi) v4.72_lic
1. [Augustus](https://github.com/Gaius-Augustus/Augustus) v3.5.0
1. [Braker](http://exon.gatech.edu/braker1.html) v3.0.8
1. [BUSCO](https://busco.ezlab.org/) v5.8.3
1. [Pfam_scan](https://www.ebi.ac.uk/seqdb/confluence/display/THD/PfamScan) v1.6
1. [BLAST](https://blast.ncbi.nlm.nih.gov/Blast.cgi?CMD=Web&PAGE_TYPE=BlastDocs&DOC_TYPE=Download) v2.16.0
1. [Samtools](http://www.htslib.org/download/) v1.21
1. [Bamtools](https://github.com/pezmaster31/bamtools) v2.5.2

### 0.2. Required database

1. [Pfam](https://pfam.xfam.org/) release 37.3

<br/>

## 1. Setup Micromamba environment

### 1.1. Install Micromamba (v2.1.0 tested)

```bash
# Download and install Micromamba
cd ${HOME}
"${SHELL}" <(curl -L micro.mamba.pm/install.sh)
source ~/.bashrc
```

### 1.2. Install dependencies

Install dependencies using Micromamba
```bash
micromamba create -y --name braker3 bioconda::braker3  # v3.0.8 tested
micromamba create -y --name trinity bioconda::trinity  # v2.15.2 tested
micromamba create -y --name repeatmodeler bioconda::repeatmodeler  # v2.0.6 tested
micromamba create -y --name hisat2 bioconda::hisat2  # v2.2.1 tested
micromamba create -y --name pfam_scan bioconda::pfam_scan  # v1.6 tested
micromamba create -y --name busco bioconda::busco  # v5.8.3 tested
micromamba create -y --name maker bioconda::maker  # v3.01.03 tested
micromamba create -y \
  --name fungap \
  --channel bioconda --channel conda-forge \
  python biopython bcbio-gff markdown2 matplotlib
```

Check installations
```bash
micromamba run --name repeatmodeler BuildDatabase --help
micromamba run --name repeatmodeler RepeatModeler --help
micromamba run --name hisat2 hisat2 --help
micromamba run --name trinity Trinity --help
micromamba run --name maker maker --help
micromamba run --name maker gff3_merge --help
micromamba run --name maker fasta_merge --help
micromamba run --name maker maker2zff --help
micromamba run --name maker fathom -help
micromamba run --name maker forge
micromamba run --name maker hmm-assembler.pl --help
micromamba run --name braker3 braker.pl --help
micromamba run --name busco busco --help
micromamba run --name pfam_scan pfam_scan.pl -h
micromamba run --name maker blastp -help
micromamba run --name maker blastn -help
micromamba run --name maker blastx -help
micromamba run --name maker makeblastdb -help
micromamba run --name maker samtools --help
micromamba run --name maker bamtools --help
micromamba run --name maker augustus --help
```

<br />

## 2. Download and install FunGAP

### 2.1. Download FunGAP

Download FunGAP using GitHub clone. Suppose we are installing FunGAP in your `$HOME` directory, but you are free to change the location. `$FUNGAP_DIR` is going to be your FunGAP installation directory.

```bash
cd $HOME  # or wherever you want
git clone https://github.com/CompSynBioLab-KoreaUniv/FunGAP.git
export FUNGAP_DIR=$(realpath FunGAP/)
# You can put this export command in the your .bashrc file
# so that you don't need to type every time you run the FunGAP
```

<br />

## 3. Download Pfam

Download Pfam databases in your `$FUNGAP_DIR/db` directory.

### 3.1. Pfam DB download 

ftp://ftp.ebi.ac.uk/pub/databases/Pfam/current_release

```bash
mkdir -p $FUNGAP_DIR/db/pfam
cd $FUNGAP_DIR/db/pfam
wget ftp://ftp.ebi.ac.uk/pub/databases/Pfam/current_release/Pfam-A.hmm.gz
wget ftp://ftp.ebi.ac.uk/pub/databases/Pfam/current_release/Pfam-A.hmm.dat.gz
gunzip Pfam-A.hmm.gz Pfam-A.hmm.dat.gz
micromamba run --name maker hmmpress Pfam-A.hmm
```

<br />

## 4. Install GeneMark

Go to the below site and download GeneMark-ES/ET.
http://topaz.gatech.edu/GeneMark/license_download.cgi
Don't forget to download the key, too.

### 4.1. Uncompress downloaded files

```bash
mkdir $FUNGAP_DIR/external/
mv gmes_linux_64_4.tar.gz gm_key_64.gz $FUNGAP_DIR/external/  # Move your downloaded files to this directory
cd $FUNGAP_DIR/external/
tar -zxvf gmes_linux_64_4.tar.gz
gunzip gm_key_64.gz
cp gm_key_64 ${HOME}/.gm_key
```

### 4.2. Change the perl path

GeneMark forces to use `/usr/bin/perl` instead of conda-installed perl. You can change this by running `change_path_in_perl_scripts.pl` script.

```bash
cd $FUNGAP_DIR/external/gmes_linux_64_4/
perl change_path_in_perl_scripts.pl "/usr/bin/env perl"
```

### 4.3 Check GeneMark and its dependencies are correctly installed.

```bash
cd $FUNGAP_DIR/external/gmes_linux_64_4/
micromamba run --name braker3 ./gmes_petap.pl
```

<br />

## 5. Download RepeatMasker databases

```bash
micromamba activate --name repeatmodeler
cd $(dirname $(which RepeatMasker))/../share/RepeatMasker
# ./configure command will download required databases
echo -e "\n\n2\n\n5\n" > tmp && ./configure < tmp

# It should look like this
ls $(dirname $(which RepeatMasker))/../share/RepeatMasker/Libraries
# Artefacts.embl  Dfam.hmm       RepeatAnnotationData.pm  RepeatMasker.lib.nin  RepeatPeps.lib      RepeatPeps.lib.psq
# CONS-Dfam_3.0   README.meta    RepeatMasker.lib         RepeatMasker.lib.nsq  RepeatPeps.lib.phr  RepeatPeps.readme
# Dfam.embl       RMRBMeta.embl  RepeatMasker.lib.nhr     RepeatMaskerLib.embl  RepeatPeps.lib.pin  taxonomy.dat
```

<br />

## 6. Configure FunGAP

This script allows users to set and test (by --help command) all the dependencies. If this script runs without any issue, you are ready to run FunGAP!

```bash
cd $FUNGAP_DIR
conda activate maker
export MAKER_DIR=$(dirname $(which maker))
echo $MAKER_DIR  # /home/ubuntu/anaconda3/envs/maker/bin
conda activate fungap
./set_dependencies.py \
  --pfam_db_path db/pfam/ \
  --genemark_path external/gmes_linux_64_4/ \
  --maker_path ${MAKER_DIR}
```

<br />

# Test run

<a name="testdata"></a>

### 1. Download test dataset

You can download yeast (*Saccharomyces cerevisiae*) genome assembly (FASTA) and RNA-seq reads (two FASTQs) from NCBI for testing FunGAP.

```bash
# Download RNA-seq reads using SRA toolkit (https://github.com/ncbi/sra-tools/wiki/01.-Downloading-SRA-Toolkit)
# Parameter -X indicates the number of read pairs you want to download
fastq-dump -X 1000000 -I --split-files SRR1198667

# Download assembly
wget ftp://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/146/045/GCF_000146045.2_R64/GCF_000146045.2_R64_genomic.fna.gz
gunzip GCF_000146045.2_R64_genomic.fna.gz
```

### 2. Download protein sequences of related species

```bash
conda activate fungap  # if you didn't do it already
$FUNGAP_DIR/download_sister_orgs.py \
  --taxon "Saccharomyces cerevisiae" \
  --email_address <YOUR_EMAIL_ADDRESS> \
  --num_sisters 1
zcat sister_orgs/*faa.gz > prot_db.faa
```

### 3. Get Augustus species

```bash
conda activate fungap  # if you didn't do it already
$FUNGAP_DIR/get_augustus_species.py \
  --genus_name "Saccharomyces" \
  --email_address <YOUR_EMAIL_ADDRESS>
```

 - saccharomyces_cerevisiae_S288C
 
### 4. Run FunGAP

```bash
conda activate fungap  # if you didn't do it already
$FUNGAP_DIR/fungap.py \
  --genome_assembly GCF_000146045.2_R64_genomic.fna \
  --trans_read_1 SRR1198667_1.fastq \
  --trans_read_2 SRR1198667_2.fastq \
  --augustus_species saccharomyces_cerevisiae_S288C \
  --busco_dataset ascomycota_odb10 \
  --sister_proteome prot_db.faa \
  --num_cores 8
  ```
  
The FunGAP predicted ~5500 genes in my test run (`fungap_out/fungap_out` output directory). It took about 8 hours by Intel(R) Xeon(R) CPU E5-2676 v3 @ 2.40GHz with 8 CPU cores.
