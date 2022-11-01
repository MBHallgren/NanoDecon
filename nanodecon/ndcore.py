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

def primary_search(args):
    logging.info("Primary search")
    cmd = "kma -i {}/trimmed-reads.fastq.gz -o {}/primary-search -t_db {} -t 8 -mint3".format(args.output, args.output, args.bac_db)
    os.system(cmd)

def set_up_output_folder(args):
    if not os.path.exists(args.output):
        os.makedirs(args.output)

def filt_long(args):
    print ("Filtering long reads")
    cmd = "gunzip -c {} | NanoFilt -q 8 --headcrop 10 | gzip > {}/trimmed-reads.fastq.gz".format(args.input, args.output) #q8, q9 or q10?
    os.system(cmd)


