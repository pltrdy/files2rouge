#!/usr/bin/python2
# -*- coding: utf-8 -*-
"""
  Multithreaded line by line ROUGE Scoring.
  
  ROUGE scoring for each lines from `ref_path` and `summ_path`
  in parrallel with:
  - n producers, putting ROUGE score in queue using pythonrouge
  - 1 consumer, get current line value, storing it and printing logs

  Usage
    python rouge_files.py [-h] --ref REFERENCES_PATH --summ SUMMARIES_PATH 
                  [--verbose] [--no-verbose]
                  [--avg] [--no-avg] 
                  [--progress] [--no-progress]

  Written in January, 2017 by pltrdy <pltrdy@gmail.com>
  on https://github.com/pltrdy/pythonrouge
"""

from __future__ import print_function, division
from multiprocessing import Process, Queue, Manager
import sys
import os
import numpy as np
from time import time, sleep
from pythonrouge import pythonrouge

ROUGE_path='./pythonrouge/RELEASE-1.5.5/ROUGE-1.5.5.pl'
ROUGE_data_path='./pythonrouge/RELEASE-1.5.5/data'
def get_rouge(reference, summary):
    """Computing ROUGE score for a reference/summary pair
    """
    score = pythonrouge.pythonrouge(reference, summary,
      ROUGE_path=ROUGE_path, data_path=ROUGE_data_path)
    return score

def fltohm(seconds):
  """Take a number of seconds (float) and return string "hours minutes"
  """
  seconds = float(seconds)
  m, s = divmod(seconds, 60)
  h, m = divmod(m, 60)
  return "%d:%02d:%02d" % (h, m, s)


LOGTO = sys.stderr
def log(*args, **kwargs):
  """Log function: prints to LOGTO and flush
  """
  kwargs['file'] = LOGTO
  print(*args, **kwargs)
  LOGTO.flush()
  

class RougeFromFiles:
  """Multithreaded line by line ROUGE Scoring class
     Inputs:
       * ref_path: path to references file
       * summ_path: path to summaries path
       * verbose: set to see progress/speed/remaining time printed on LOGTO 
       * print_score: set to output each line scores to stdout.
           format (separated by tabs): nline, R-1, R-2, R-3, R-SUA, R-L           
  """
  def __init__(self, ref_path, summ_path, verbose=False, print_scores=False):
    self.ref_path = ref_path
    self.summ_path = summ_path
    self.verbose = verbose
    self.print_scores = print_scores
    
    self._check_paths()
  
  def _check_paths(self):
    ref_path, summ_path = self.ref_path, self.summ_path
    if not(os.path.exists(ref_path) and os.path.isfile(ref_path)):
      print("Path '%s' does not exists, permission denied or is not a file." % ref_path, file=sys.stderr)
      exit(1)

    if not(os.path.exists(summ_path) and os.path.isfile(summ_path)):
      print("Path '%s' does not exists, permission denied or is not a file." % summ_path, file=sys.stderr)
      exit(1)

  def prerun(self):
    self.stime = time()
    print("Counting lines...")
    with open(self.ref_path) as f:
      self.ref_len = sum(1 for line in f)
    with open(self.summ_path) as f:
      self.summ_len = sum(1 for line in f)
    self.iters = min(self.ref_len, self.summ_len)
    print("Refs: %d lines\tSummaries: %d lines" % (self.ref_len, self.summ_len))


  def files_reader(self):
    """ (ref, summ) pairs generator
    """
    ref_file = open(self.ref_path)
    summ_file = open(self.summ_path)

    while True:
      ref = ref_file.readline()
      summ = summ_file.readline()

      if not ref or not summ:
        break
      yield (ref, summ)


  def run(self):
    """Main function, create threads, waits for it and returns output
    """
    q = Queue()
    mgr = manager = Manager()
    shared = manager.dict()
    consumer = Process(target=self._consumer, args=(q,shared))
    consumer.start()

    proc = []
    for count, (ref, summ) in enumerate(self.files_reader()):
      proc.append(Process(target=self._producer, args=(q, count, ref, summ)))
      proc[-1].start()

    def join_if_alive(process):
      if process.is_alive():
        process.join()

    for p in proc:
      join_if_alive(p)

    q.put(None)
    join_if_alive(consumer)
    ret = (shared["scores"], shared["count"])
    return ret

  def _producer(self, q, line, ref, summ):
    q.put([line, ref, summ, get_rouge(ref, summ)])

  def _consumer(self, q, shared):
    print_scores, verbose = self.print_scores, self.verbose
    self.prerun()

    scores = {"ROUGE-1": [], "ROUGE-2": [], "ROUGE-3": [], "ROUGE-SU4": [], "ROUGE-L": []}
    
    q.cancel_join_thread()
    _verbose = verbose
    count = 0
    while True:
      data = q.get()
      if data is None:
        break
      line, ref, summ, score = data
      
      count += 1
      verbose = _verbose and (count % 10)==0

      progress_ratio = count / self.iters
      elapsed_time = time() - self.stime
      lps = count / elapsed_time
      est_duration = 0 if count == 0 else (elapsed_time * (1/progress_ratio))-elapsed_time

      if verbose:  
        log("\rLines #%d/%d (%.4f%%)\tLine per second: %.0f\tRemaining time: %s" % (count+1, self.iters, 100*progress_ratio, lps, fltohm(est_duration)), end="")
        if q.full():
          log("[WARNING] Queue is full")

      for s in score:
        scores[s].append(score[s])
     
            
      if print_scores:
        if verbose and sys.stdout.isatty() and sys.stderr.isatty():
          print("") 
        print("%d\t%f\t%f\t%f\t%f\t%f"
          % (line, score["ROUGE-1"], score["ROUGE-2"], score["ROUGE-3"], score["ROUGE-SU4"], score["ROUGE-L"]))

    q.close()
    shared["scores"] = scores
    shared["count"] = count

def main():
  import argparse

  parser = argparse.ArgumentParser(description="Multithreaded line by line ROUGE score of two files.")

  parser.add_argument('--ref', help="Full ref file", required=True)
  parser.add_argument('--summ', help="Summaries", required=True)
  parser.add_argument('--verbose', dest='verbose', action='store_true')
  parser.add_argument('--no-verbose', dest='verbose', action='store_false')

  parser.set_defaults(verbose=False)
  parser.set_defaults(avg=True)
  
  args = parser.parse_args()

  ref_path = args.ref
  summ_path = args.summ
  verbose = args.verbose

  stime = time()
  scores, lines = RougeFromFiles(ref_path, summ_path, verbose=verbose).run()
  etime = time() - stime

  log("\n\nEvaluated %d ref/summary pairs in %.3f seconds (%.3f lines/sec)" % (lines, etime, lines/etime))
  for s in ["ROUGE-1", "ROUGE-2", "ROUGE-3", "ROUGE-L", "ROUGE-SU4"]:
    log("%s: %f" % (s, np.mean(scores[s])))


if __name__ == '__main__':
  main()
