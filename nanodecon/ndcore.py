import sys
import os
import logging


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
    cmd = "kma -i {}/trimmed-reads.fastq.gz -o {}/primary-search -t_db {} -t 8 -mem_mode -mp 20 -mrs 0.0 -bcNano -bc 0.7".format(args.output, args.output, args.bac_db)
    os.system(cmd)
    cmd = "sort -t$\'\t\' -k2nr {}/primary-search.res > {}/primary-search.sorted.res".format(args.output, args.output)
    print (cmd)
    os.system(cmd)

    #Read in primary search results sorted
    with open("{}/primary-search.sorted.res".format(args.output), "r") as f:
        line = f.readline()
        print (line)
        line = f.readline()
        print (line)
        top_scoring_template = Kma_result(line)
    print (top_scoring_template.name)



def set_up_output_folder(args):
    if not os.path.exists(args.output):
        os.makedirs(args.output)

def filt_long(args):
    print ("Filtering long reads")
    cmd = "gunzip -c {} | NanoFilt -q 8 --headcrop 10 | gzip > {}/trimmed-reads.fastq.gz".format(args.input, args.output) #q8, q9 or q10?
    os.system(cmd)


