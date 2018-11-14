#!/usr/bin/env python
from __future__ import print_function
import os

def mkdir(path):
    os.mkdir(path)

def mkdirs(paths):
    for path in paths:
        mkdir(path)

def tee(saveto, *args, **kwargs):
    """Mimic the tee command, write on both stdout and file
    """
    print(*args, **kwargs)
    if saveto is not None:
        print(file=saveto, *args, **kwargs)

def split_files(model_file, system_file, model_dir, system_dir, eos="."):
    def outputs(line, f): 
        split_sen = " .\n".join(line.split(" %s " % eos))
        print(split_sen, end="", file=f)

    with open(model_file) as fmodel:
        for (i, line) in enumerate(fmodel):
            if not line:
                break
            if len(line) == 0:
                continue

            with open("%s/m.A.%d.txt" % (model_dir, i), "w") as f:
                outputs(line, f)

    with open(system_file) as fsystem:
        for (i, line) in enumerate(fsystem):
            if not line:
                break
            if len(line) == 0:
                continue
        
            with open("%s/s.%d.txt" % (system_dir, i), "w") as f:
                outputs(line, f)

