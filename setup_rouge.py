#!/usr/bin/env python
"""
    Utility to copy ROUGE script.
    It has to be run before `setup.py`

"""
from files2rouge import settings
import os
import shutil
import sys


def get_input(*args, **kwargs):
    # Support Python 2 and 3 input
    # Default to Python 3's input()
    fct = input

    # If this is Python 2, use raw_input()
    if sys.version_info[:2] <= (2, 7):
        fct = raw_input

    return fct(*args, **kwargs)

def copy_ROUGE():
  home = os.environ['HOME']

  src_ROUGE_root = "./files2rouge/RELEASE-1.5.5/"

  default_root = os.path.join(home, '.files2rouge/')

  print("files2rouge uses scripts and tools that will not be stored with the python package")
  path = get_input("where do you want to save it? [default: %s]" % default_root)

  if path == "": 
    path = default_root

  ROUGE_data = os.path.join(path, "data")
  ROUGE_path = os.path.join(path, "ROUGE-1.5.5.pl")

  print("Copying '%s' to '%s'" % (src_ROUGE_root, path))
  shutil.copytree(src_ROUGE_root, path) 


  return {"ROUGE_path": ROUGE_path, "ROUGE_data": ROUGE_data}


conf_path = "./files2rouge/settings.json"
s = settings.Settings(path=conf_path)
data = copy_ROUGE()
s._generate(data)

