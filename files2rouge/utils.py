#!/usr/bin/env python
from __future__ import print_function
import os


def mkdir(path):
    os.mkdir(path)


def mkdirs(paths):
    for path in paths:
        mkdir(path)


def line_count(path):
    with open(path) as f:
        for i, line in enumerate(f):
            pass
    n = i + 1
    return n


def tee(saveto, *args, **kwargs):
    """Mimic the tee command, write on both stdout and file
    """
    print(*args, **kwargs)
    if saveto is not None:
        print(file=saveto, *args, **kwargs)


def split_files(model_path, system_path, model_dir, system_dir,
                ignore_empty_reference=False,
                ignore_empty_summary=False,
                eos="."):
    def outputs(line, f):
        split_sen = (" %s\n" % eos).join(line.split(" %s" % eos))
        print(split_sen, end="", file=f)

    # First, assert line counts match
    model_count = line_count(model_path)
    system_count = line_count(system_path)
    if model_count != system_count:
        raise ValueError("Model and System line counts must match, %d != %d"
                         % (model_count, system_count))

    lines_to_ignore = []
    with open(model_path) as fmodel:
        with open(system_path) as fsystem:
            for i, (mod_line, sys_line) in enumerate(zip(fmodel, fsystem)):
                mod_line = mod_line.strip()
                sys_line = sys_line.strip()

                if mod_line == "":
                    if ignore_empty_reference:
                        lines_to_ignore.append(i + 1)
                        continue
                    else:
                        raise ValueError("Empty reference at line %d."
                                         " Use `--ignore_empty_reference` to ignore it"
                                         % (i + 1))

                if sys_line == "":
                    if ignore_empty_summary:
                        lines_to_ignore.append(i + 1)
                        continue
                    else:
                        raise ValueError("Empty summary at line %d."
                                         " Use `--ignore_empty_summary` to ignore it"
                                         % (i + 1))
                with open("%s/m.A.%d.txt" % (model_dir, i), "w") as f:
                    outputs(mod_line, f)

                with open("%s/s.%d.txt" % (system_dir, i), "w") as f:
                    outputs(sys_line, f)
    return lines_to_ignore
