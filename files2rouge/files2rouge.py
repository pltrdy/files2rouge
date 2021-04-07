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


DEFAULT_ROUGE_N = 2


def run(summ_path,
        ref_path,
        rouge_args=None,
        verbose=False,
        saveto=None,
        rouge_n=DEFAULT_ROUGE_N,
        no_rouge_l=False,
        eos=".",
        ignore_empty_reference=False,
        ignore_empty_summary=False,
        stemming=True):

    if rouge_args is not None:
        if rouge_n != DEFAULT_ROUGE_N:
            raise ValueError("'rouge_n' should not be set with 'rouge_args'")

        if no_rouge_l:
            raise ValueError(
                "'no_rouge_l' should not be set with 'rouge_args'")

    s = settings.Settings()
    s._load()
    stime = time()

    with tempfile.TemporaryDirectory() as dirpath:
        sys_root, model_root = [os.path.join(dirpath, _)
                                for _ in ["system", "model"]]

        print("Preparing documents...", end=" ")
        utils.mkdirs([sys_root, model_root])
        ignored = utils.split_files(model_path=ref_path,
                                    system_path=summ_path,
                                    model_dir=model_root,
                                    system_dir=sys_root,
                                    eos=eos,
                                    ignore_empty_reference=ignore_empty_reference,
                                    ignore_empty_summary=ignore_empty_summary)
        print("%d line(s) ignored" % len(ignored))
        print("Running ROUGE...")
        log_level = logging.ERROR if not verbose else None
        r = pyrouge.Rouge155(rouge_dir=os.path.dirname(s.data['ROUGE_path']),
                             log_level=log_level,
                             stemming=stemming)
        r.system_dir = sys_root
        r.model_dir = model_root
        r.system_filename_pattern = r's.(\d+).txt'
        r.model_filename_pattern = 'm.[A-Z].#ID#.txt'
        data_arg = "-e %s" % s.data['ROUGE_data']

        if not rouge_args:
            rouge_args = [
                '-c', 95,
                '-r', 1000,
                '-n', rouge_n,
                '-a']
            if no_rouge_l:
                rouge_args.append("-x")

            rouge_args_str = " ".join([str(_) for _ in rouge_args])
        else:
            rouge_args_str = rouge_args
        rouge_args_str = "%s %s" % (data_arg, rouge_args_str)

        output = r.convert_and_evaluate(rouge_args=rouge_args_str)

    if saveto is not None:
        saveto = open(saveto, 'w')

    utils.tee(saveto, output)
    print("Elapsed time: %.3f seconds" % (time() - stime))


def main():
    parser = argparse.ArgumentParser(
        description="Calculating ROUGE score between two files (line-by-line)")
    parser.add_argument("reference", help="Path of references file")
    parser.add_argument("summary", help="Path of summary file")
    parser.add_argument('-v', '--verbose', action="store_true",
                        help="""Prints ROUGE logs""")
    parser.add_argument('-n', '--rouge_n', type=int, default=DEFAULT_ROUGE_N,
                        help="Maximum n_gram size to consider")
    parser.add_argument('-nol', '--no_rouge_l', action="store_true",
                        help="Do not calculate ROUGE-L")
    parser.add_argument('-a', '--args', help="ROUGE Arguments")
    parser.add_argument('-s', '--saveto', dest="saveto",
                        help="File to save scores")
    parser.add_argument('-e', '--eos', dest="eos", default='.',
                        help="""End of sentence separator (for multisentence).
                            Default: \".\" """)
    parser.add_argument("-m", "--stemming", action="store_true",
                        help="DEPRECATED: stemming is now default behavior")
    parser.add_argument("-nm", "--no_stemming", action="store_true",
                        help="Switch off stemming")
    parser.add_argument("-ir", "--ignore_empty_reference", action="store_true")
    parser.add_argument("-is", "--ignore_empty_summary", action="store_true")
    args = parser.parse_args()

    if args.stemming:
        raise ValueError(
            """files2rouge uses stemming by default so --stemming is
            deprecated. You can turn it off with -nm/--no_stemming""")

    run(args.summary,
        args.reference,
        rouge_args=args.args,
        rouge_n=args.rouge_n,
        no_rouge_l=args.no_rouge_l,
        verbose=args.verbose,
        saveto=args.saveto,
        eos=args.eos,
        ignore_empty_reference=args.ignore_empty_reference,
        ignore_empty_summary=args.ignore_empty_summary,
        stemming=not args.no_stemming)


if __name__ == '__main__':
    main()
