#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
  Multithreaded line by line ROUGE Scoring.
  
  ROUGE scoring for each lines from `ref_path` and `summ_path`
  in parrallel.
  - n producers, putting ROUGE score in queue using pythonrouge
  - 1 consumer, get current line value, storing it and printing logs

  We haven't found any case where the consumer is the bottleneck, thus,
  keeping a single process consumer make sense.

  In addition, we give each producers not a single (ref, sum) pair
  but instead a "chunk" of `chunk_size` pairs. We did this to avoid having
  too much producer process, which can raise error (e.g.Too many opened file)

  Usage
    python rouge_files.py [-h] SUMMARIES_PATH REFERENCES_PATH 
                  [--verbose] [--no-verbose]
                  [--avg] [--no-avg] 
                  [--progress] [--no-progress]

  Written in January, 2017 by pltrdy <pltrdy@gmail.com>
  on https://github.com/pltrdy/pythonrouge
"""
from __future__ import absolute_import
from __future__ import print_function, division
from multiprocessing import Process, Queue, Manager
import sys
import os
import numpy as np
from time import time, sleep
from pythonrouge import pythonrouge
from files2rouge import settings

def get_rouge(reference, summary, rouge_settings, score="F"):
    """Computing ROUGE score for a reference/summary pair
    """
    ROUGE_path = rouge_settings.data['ROUGE_path']
    ROUGE_data = rouge_settings.data['ROUGE_data']
    scores = pythonrouge.pythonrouge(reference, summary,
      ROUGE_path=ROUGE_path, data_path=ROUGE_data)

    return scores[score]

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
           format (separated by tabs): nline, R-1, R-2, R-3, R-S4, R-L
  """
  def __init__(self, ref_path, summ_path, rouge_settings, verbose=False, print_scores=False, score="F"):
    self.ref_path = ref_path
    self.summ_path = summ_path
    self.verbose = verbose
    self.print_scores = print_scores
    self.score = score
    self.rouge_settings = rouge_settings
    
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


  def files_reader(self, chunk_size):
    """ (ref, summ) pairs generator
    """
    ref_file = open(self.ref_path)
    summ_file = open(self.summ_path)

    done = False
    count = 0
    while not done:
      refs = []
      summs = []
      for count in range(chunk_size):
        ref = ref_file.readline()
        summ = summ_file.readline()

        if not ref or not summ:
          done = True
          break

        refs += [ref]
        summs += [summ]

      yield (len(refs), refs, summs)


  def run(self):
    """Main function, create threads, waits for it and returns output
    """
    q = Queue()
    mgr = manager = Manager()
    shared = manager.dict()
    consumer = Process(target=self._consumer, args=(q,shared))
    consumer.start()

    proc = []
    chunk_size = 64
    count = 0
    for (n, refs, summs) in self.files_reader(chunk_size):
      proc.append(Process(target=self._producer, args=(q, count, refs, summs)))
      count += n
      while True:
        try:
          proc[-1].start()
          break
        except Exception as e:
          print("Error starting producer")
          print(e)
          sleep(0.5)

    def join_if_alive(process):
      if process.is_alive():
        process.join()

    for p in proc:
      join_if_alive(p)

    q.put(None)
    join_if_alive(consumer)
    ret = (shared["scores"], shared["count"])
    return ret

  def _producer(self, q, count, refs, summs):
    for (c, (ref, summ)) in enumerate(zip(refs, summs)):
      q.put_nowait([count+c, ref, summ, get_rouge(ref, summ, self.rouge_settings, score=self.score)])

  def _consumer(self, q, shared):
    print_scores, verbose = self.print_scores, self.verbose
    self.prerun()

    scores = {"ROUGE-1": [], "ROUGE-2": [], "ROUGE-3": [], "ROUGE-S4": [], "ROUGE-L": []}
    
    q.cancel_join_thread()
    _verbose = verbose
    count = 0
    while True:
      #can be helful to figure out which of (producer, consumer) is the bottleneck
      #in practice the producer is i.e. the consumer waits a lot.
      #print(q.qsize())
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
          % (line, score["ROUGE-1"], score["ROUGE-2"], score["ROUGE-3"], score["ROUGE-S4"], score["ROUGE-L"]))

    q.close()
    shared["scores"] = scores
    shared["count"] = count

def main():
  import argparse

  parser = argparse.ArgumentParser(description="Calculating ROUGE score between two files (line-by-line)")

  parser.add_argument("summary", help="Path of summary file")
  parser.add_argument("reference", help="Path of references file")
  parser.add_argument("--score", dest="score", help="Rouge Variant (F1, Recall, Precision)", choices=["F", "R", "P"], default="F")
  parser.add_argument('--verbose', dest='verbose', action='store_true')
  parser.add_argument('--no-verbose', dest='verbose', action='store_false')
  parser.add_argument('--saveto', dest="saveto", help="File to save scores")
  parser.set_defaults(verbose=True)
  
  args = parser.parse_args()

  ref_path = args.reference
  summ_path = args.summary
  verbose = args.verbose
  score = args.score
  saveto = args.saveto

  if saveto is not None:
    saveto = open(saveto, 'w')

  s = settings.Settings()
  s._load()

  stime = time()
  scores, lines = RougeFromFiles(ref_path, summ_path, s,verbose=verbose, score=score).run()
  etime = time() - stime

  def tee(*args, **kwargs):
    """Mimic the tee command, write on both stdout and file
    """
    print(*args, **kwargs)
    if saveto is not None:
      print(file=saveto, *args, **kwargs)

  tee("\n\nEvaluated %d ref/summary pairs in %.3f seconds (%.3f lines/sec)" % (lines, etime, lines/etime))
  for s in ["ROUGE-1", "ROUGE-2", "ROUGE-3", "ROUGE-L", "ROUGE-S4"]:
    tee("%s (%s): %f" % (s, score, np.mean(scores[s])))

if __name__ == '__main__':
  main()
