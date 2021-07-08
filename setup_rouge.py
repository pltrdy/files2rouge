#!/usr/bin/env python
"""
    Utility to copy ROUGE script.
    It has to be run before `setup.py`

"""
import os
import shutil

from files2rouge import settings
from six.moves import input


def copy_rouge():
    if 'HOME' not in os.environ:
        home = os.environ['HOMEPATH']
    else:
        home = os.environ['HOME']

    src_rouge_root = "./files2rouge/RELEASE-1.5.5/"

    default_root = os.path.join(home, '.files2rouge/')

    print("files2rouge uses scripts and tools that will not be stored with "
          "the python package")
    path = input(
        "where do you want to save it? [default: %s]" % default_root)

    if path == "":
        path = default_root

    rouge_data = os.path.join(path, "data")
    rouge_path = os.path.join(path, "ROUGE-1.5.5.pl")

    print("Copying '%s' to '%s'" % (src_rouge_root, path))
    shutil.copytree(src_rouge_root, path)

    return {"ROUGE_path": rouge_path, "ROUGE_data": rouge_data}


conf_path = "./files2rouge/settings.json"
s = settings.Settings(path=conf_path)
data = copy_rouge()
s._generate(data)
