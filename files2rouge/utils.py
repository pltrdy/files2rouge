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


def split_files(model_file, system_file, model_dir, system_dir,
                ignore_empty=False, eos="."):
    def outputs(line, f):
        split_sen = " .\n".join(line.split(" %s" % eos))
        print(split_sen, end="", file=f)

    model_count = 0
    lines_to_ignore = []

    with open(model_file) as fmodel:
        for (i, line) in enumerate(fmodel):

            if not line:
                break
            if line == "\n":
                if ignore_empty:
                    lines_to_ignore.append(i)
                    continue
                else:
                    raise ValueError("Empty reference at line %d."
                                     " Use `--ignore_empty` to ignore it"
                                     % (i+1))

            model_count += 1
            with open("%s/m.A.%d.txt" % (model_dir, i), "w") as f:
                outputs(line, f)

    system_count = 0
    line_to_ignore_it = iter(lines_to_ignore)
    line_to_ignore = next(line_to_ignore_it, -1)

    with open(system_file) as fsystem:
        for (i, line) in enumerate(fsystem):
            if not line:
                break
            if i == line_to_ignore:
                line_to_ignore = next(line_to_ignore_it, -1)
                continue
            if line == "\n":
                raise ValueError("Empty summary at line %d" % (i+1))

            system_count += 1
            with open("%s/s.%d.txt" % (system_dir, i), "w") as f:
                outputs(line, f)
    if model_count != system_count:
        raise ValueError("Model and System line counts must match, %d != %d"
                         % (model_count, system_count))
    return lines_to_ignore
