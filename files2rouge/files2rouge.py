#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    ROUGE scoring for each lines from `ref_path` and `summ_path`
    in parrallel.

    Sentences are identified by the `--eos` flag (by default ".")
    One can save score to a file using `--saveto`

    Usage:
        files2rouge -h

"""
from __future__ import absolute_import
from __future__ import print_function, division
from files2rouge import settings
from files2rouge import utils
from time import time
import os
import pyrouge
import tempfile
import logging
import argparse


def run(summ_path,
        ref_path,
        rouge_args=None,
        verbose=False,
        saveto=None,
        eos="."):

    if saveto is not None:
        saveto = open(saveto, 'w')

    s = settings.Settings()
    s._load()
    stime = time()
    dirpath = tempfile.mkdtemp()
    sys_root, model_root = [os.path.join(dirpath, _)
                            for _ in ["system", "model"]]

    print("Preparing documents...")
    utils.mkdirs([sys_root, model_root])
    utils.split_files(model_file=ref_path,
                      system_file=summ_path,
                      model_dir=model_root,
                      system_dir=sys_root,
                      eos=eos)
    print("Running ROUGE...")
    log_level = logging.ERROR if not verbose else None
    r = pyrouge.Rouge155(rouge_dir=os.path.dirname(s.data['ROUGE_path']),
                         log_level=log_level)
    r.system_dir = sys_root
    r.model_dir = model_root
    r.system_filename_pattern = r's.(\d+).txt'
    r.model_filename_pattern = 'm.[A-Z].#ID#.txt'
    data_arg = "-e %s" % s.data['ROUGE_data']

    if not rouge_args:
        rouge_args = [
            '-c', 95,
            '-r', 1000,
            '-n', 2,
            '-a']
        rouge_args_str = " ".join([str(_) for _ in rouge_args])
    else:
        rouge_args_str = rouge_args
    rouge_args_str = "%s %s" % (data_arg, rouge_args_str)
    output = r.convert_and_evaluate(rouge_args=rouge_args_str)

    utils.tee(saveto, output)
    print("Elapsed time: %.3f seconds" % (time() - stime))


def main():
    parser = argparse.ArgumentParser(
        description="Calculating ROUGE score between two files (line-by-line)")
    parser.add_argument("summary", help="Path of summary file")
    parser.add_argument("reference", help="Path of references file")
    parser.add_argument('-v', '--verbose', action="store_true",
                        help="""Prints ROUGE logs""")
    parser.add_argument('-a', '--args', help="ROUGE Arguments")
    parser.add_argument('-s', '--saveto', dest="saveto",
                        help="File to save scores")
    parser.add_argument('-e', '--eos', dest="eos", default='.',
                        help="""End of sentence separator (for multisentence).
                            Default: \".\" """)
    args = parser.parse_args()

    run(args.reference,
        args.summary,
        args.args,
        args.verbose,
        args.saveto,
        args.eos)


if __name__ == '__main__':
    main()
