#!/usr/bin/env python3

'''
Run Hisat2 for intron-aware reads alignments

Default parameters for Hisat:
hisat2 \
  --max-intronlen 2000 \
  -p <NUMBER_OF_CORES> \
  -x <INDEX_FILE> \
  -1 <READ1_FASTQ> \
  -2 <READ2_FASTQ> \
  -S <OUT_SAM>

--max-intronlen: maximum intron length. 2000 bp is set for fungal genomes,
    but users can modity this by passing --max_intron <LEN> to this script.

Input: FASTQ files and genome assembly
Output: SAM and converted BAM file using SAMtools.
Last updated: Jun 9, 2025
'''

import os
import re
import sys
import shlex
import subprocess
from argparse import ArgumentParser

from import_config import import_config
from set_logging import set_logging

# Parameters
D_CONF = import_config()


# Main function
def main():
    '''Main function'''
    argparser_usage = (
        'run_hisat2.py -r <fastq1> <fastq2> <fastq3> ...'
        ' -o <output_dir> -l <log_dir> -f <ref_fasta> -c <num_cores>'
        ' -m <max_intron>')
    parser = ArgumentParser(usage=argparser_usage)
    parser.add_argument(
        '-r', '--read_files', nargs='+', required=True,
        help='Multiople read files in fastq format')
    parser.add_argument(
        '-o', '--output_dir', nargs='?', default='hisat2_out',
        help='Output directory')
    parser.add_argument(
        '-l', '--log_dir', nargs='?', default='logs',
        help='Log directory')
    parser.add_argument(
        '-f', '--ref_fasta', nargs=1, required=True,
        help='Reference fasta')
    parser.add_argument(
        '-c', '--num_cores', nargs='?', default=1, type=int,
        help='Number of cores')
    parser.add_argument(
        '-m', '--max_intron', nargs='?', default=2000, type=int,
        help='Max intron length (Default: 2000 bp)')

    args = parser.parse_args()

    read_files = [os.path.abspath(x) for x in args.read_files]
    output_dir = os.path.abspath(args.output_dir)
    log_dir = os.path.abspath(args.log_dir)
    ref_fasta = os.path.abspath(args.ref_fasta[0])
    num_cores = args.num_cores
    max_intron = args.max_intron

    # Create necessary dirs
    create_dir(output_dir, log_dir)

    # Set logging
    log_file = os.path.join(log_dir, 'run_hisat2.log')
    logger = set_logging(log_file)
    logger_time = logger[0]

    # Run functions :) Slow is as good as Fast
    logger_time.debug('START: Hisat2')
    run_hisat2(read_files, output_dir, log_dir, ref_fasta, num_cores, max_intron, logger)
    logger_time.debug('DONE : Hisat2')


# Define functions
def import_file(input_file):
    '''Import file'''
    with open(input_file) as f_in:
        txt = list(line.rstrip() for line in f_in)
    return txt


def create_dir(output_dir, log_dir):
    '''Create directories'''
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    if not os.path.exists(log_dir):
        os.mkdir(log_dir)


def run_hisat2(read_files, output_dir, log_dir, ref_fasta, num_cores, max_intron, logger):
    '''Run Hisat2'''
    output_dir = re.sub(r'/$', '', output_dir)
    hisat2_bin = D_CONF['HISAT2_PATH']
    samtools_bin = D_CONF['SAMTOOLS_PATH']

    # hisat2-build -p <num_cores> <ref_fasta> <ref_fasta>
    hisat2_build_log_file = os.path.join(log_dir, 'hisat2-build.log')
    hisat2_build_output = '{}.5.ht2'.format(ref_fasta)
    logger_txt = logger[1]
    if not os.path.exists(hisat2_build_output):
        command1 = f'{hisat2_bin}-build -p {num_cores} {ref_fasta} {ref_fasta} > {hisat2_build_log_file} 2>&1'
        logger_txt.debug(f'[Run] {command1}')
        os.system(command1)
    else:
        logger_txt.debug('[Note] Running hisat2-build has already been finished')

    # hisat2 -p <num_cores> -x Choanephora_cucurbitarum_assembly.fna
    # -1 reads/chocu-mRNA_1.fastq -2 reads/chocu-mRNA_2.fastq
    # -S trans_hisat2/chocu-mRNA_with_annot.sam
    hisat2_outputs = []
    for read_file in read_files:
        if read_file.endswith('_1.fastq') or read_file.endswith('_1.fq'):
            read_pair = (
                read_file
                .replace('_1.fastq', '_2.fastq')
                .replace('_1.fq', '_2.fq'))
            if not os.path.exists(read_pair):
                logger_txt.debug(
                    '[ERROR] No read file pair for %s found. We expect %s',
                    os.path.basename(read_file), os.path.basename(read_pair)
                )
                sys.exit(2)

            read_arg = '-1 {} -2 {}'.format(read_file, read_pair)
        elif read_file.endswith('_s.fastq') or read_file.endswith('_s.fq'):
            read_arg = '-U {}'.format(read_file)
        elif read_file.endswith('_2.fastq') or read_file.endswith('_2.fq'):
            continue
        else:
            logger_txt.debug(
                '[ERROR] Please check trans_read files:\n--> %s',
                os.path.basename(read_file))
            sys.exit(2)

        prefix = os.path.basename(os.path.splitext(read_file)[0])
        prefix = re.sub('_[1s]$', '', prefix)
        hisat2_output = os.path.join(output_dir, '{}.bam'.format(prefix))
        hisat2_outputs.append(hisat2_output)
        if not os.path.exists(hisat2_output):
            # Prepare paths
            log_file = os.path.join(log_dir, f'hisat2_{prefix}.log')
            sam_path = os.path.splitext(hisat2_output)[0] + '.sam'
            unsorted_bam_path = os.path.splitext(hisat2_output)[0] + '.unsorted.bam'

            # Step 1: Run HISAT2 and write SAM file
            command1 = shlex.split(hisat2_bin)
            command1 = (
                f'{hisat2_bin}'
                f'  --max-intronlen {max_intron}'
                f'  -p {num_cores}'
                f'  -x {ref_fasta}'
                f'  -S {sam_path}'
                f'  {read_arg}')
            with open(log_file, 'w') as logf:
                logger_txt.debug(f'[Run] {command1}')
                subprocess.run(command1, stderr=logf, check=True, shell=True)

            # Step 2: Convert SAM to BAM
            command2 = f'{samtools_bin} view -bSF4 {sam_path} -o {unsorted_bam_path}'
            logger_txt.debug(f'[Run] {command2}')
            subprocess.run(command2, check=True, shell=True)

            # Step 3: Sort BAM
            command3 = f'{samtools_bin} sort -@ {num_cores} {unsorted_bam_path} -o {hisat2_output}'
            logger_txt.debug(f'[Run] {command3}')
            subprocess.run(command3, check=True, shell=True)
        else:
            logger_txt.debug('[Note] Running Hisat2 has already been finished for %s', prefix)

    if not hisat2_outputs:
        logger_txt.debug('[ERROR] No BAM file was made. Please check the log file')
        sys.exit(1)

if __name__ == '__main__':
    main()
