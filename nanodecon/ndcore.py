import sys
import os
import logging
import gzip
import pyfastx


import nanodecon.ndhelpers as ndhelpers
from .version import __version__


def nano_decon(args):
    #Logging
    set_up_output_folder(args)
    ndhelpers.begin_logging(args.output + '/nanodecon.log')
    logging.info('NanoDecon {} with input arguments {}'.format(__version__, args))
    try:
        set_up_output_folder(args)
        filt_long(args)
        primary_search(args)
        test_filtered_reads(args)
        logging.info("NanoDecon finished successfully")
    except Exception as e:
        logging.error(e, exc_info=True)
        raise
    return True

class Kma_result:
    def __init__(self, line):
        self.line = line
        self.line = self.line.split("\t")
        self.name = self.line[0]
        self.score = float(self.line[1])
        self.expected_score = float(self.line[2])
        self.template_length = float(self.line[3])
        self.template_identity = float(self.line[4])
        self.template_coverage = float(self.line[5])
        self.query_identity = float(self.line[6])
        self.query_coverage = float(self.line[7])
        self.depth = float(self.line[8])

def primary_search(args):
    logging.info("Primary search")
    cmd = "kma -i {}/trimmed-reads.fastq.gz -o {}/primary-search -t_db {} -t 8 -nf -mem_mode -sasm -ef -1t1".format(args.output, args.output, args.bac_db)
    os.system(cmd)
    cmd = "sort -t \'\t\' -k2nr {}/primary-search.res > {}/primary-search.sorted.res".format(args.output, args.output)
    os.system(cmd)

    #Read in primary search results sorted
    with open("{}/primary-search.sorted.res".format(args.output), "r") as f:
        kma_results = [Kma_result(line) for line in f if not line.startswith("#")]
    evaluate_primary_results(args, kma_results)

def get_kma_template_number(args, name):
    with open('{}.name'.format(args.bac_db), 'r') as infile:
        t = 1
        for line in infile:
            if name in line:
                return t
            t += 1
        return t

def derive_read_list_from_frag(file):

    with gzip.open(file, 'rt', encoding='utf-8') as f:
        read_list = [line.split('\t')[6].split(" ")[0] for line in f]
    return read_list

def test_filtered_reads(args):
    cmd = "kma -i {}/decon-reads.fastq.gz -o {}/decon-search -t_db {} -t 8 -nf -mem_mode -sasm -ef -1t1".format(
        args.output, args.output, args.bac_db)
    os.system(cmd)
    cmd = "kma -i {}/con-reads.fastq.gz -o {}/con-search -t_db {} -t 8 -nf -mem_mode -sasm -ef -1t1".format(
        args.output, args.output, args.bac_db)
    os.system(cmd)


def filter_out_reads_from_fastq(read_list, args):
    with gzip.open("{}/decon-reads.fastq.gz".format(args.output), "wt") as outfile1:
        with gzip.open("{}/con-reads.fastq.gz".format(args.output), "wt") as outfile2:
            fq = pyfastx.Fastq("{}/trimmed-reads.fastq.gz".format(args.output), build_index=False)
            for read in fq:
                if read[0] in read_list:
                    print ("@" + read[0], file=outfile1)
                    print (read[1], file=outfile1)
                    print ("+", file=outfile1)
                    print (read[2], file=outfile1)
                else:
                    print("@" + read[0], file=outfile2)
                    print(read[1], file=outfile2)
                    print("+", file=outfile2)
                    print(read[2], file=outfile2)

        #with gzip.open("{}/tr  immed-reads.fastq.gz".format(args.output), "rb") as infile:
        #    for line in infile:
        #        if line.decode().split(" ")[0] in read_list:
        #            print (line.decode())

def evaluate_primary_results(args, kma_results):
    """ index 0 is top scoring template, -1 is lowest"""
    prime_score = kma_results[0].score/kma_results[1].score
    if prime_score > 3:
        cmd = "kma -i {}/trimmed-reads.fastq.gz -o {}/primary-alignment -t_db {} -t 8 -mint3 -Mt1 {} ".format(args.output, args.output, args.bac_db, get_kma_template_number(args, kma_results[0].name))
        os.system(cmd)
        filter_out_reads_from_fastq(derive_read_list_from_frag("{}/primary-alignment.frag.gz".format(args.output)), args)
    else:
        print ("No clear primary template found")
        print ("tbd")


def set_up_output_folder(args):
    if not os.path.exists(args.output):
        os.makedirs(args.output)

def filt_long(args):
    print ("Filtering long reads")
    cmd = "gunzip -c {} | NanoFilt -q 8 --headcrop 10 | gzip > {}/trimmed-reads.fastq.gz".format(args.input, args.output) #q8, q9 or q10?
    os.system(cmd)


