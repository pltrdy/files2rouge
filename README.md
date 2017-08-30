# Files2ROUGE
Multi-threaded ROUGE scoring.   
It uses [pythonrouge](https://github.com/pltrdy/pythonrouge).   
See [ROUGE Official website]() as well as [this paper about ROUGE variants](http://83.212.103.151/~mkalochristianakis/techNotes/ipromo/rougen5.pdf)

## Motivations
Computing ROUGE score between an automatically generated summary and a reference file.

```shell
$ files2rouge -h
usage: files2rouge.py [-h] [--score {F,R,P}] [--verbose] [--no-verbose]
                      summary reference

Calculating ROUGE score between two files (line-by-line)

positional arguments:
  summary          Path of summary file
  reference        Path of references file

optional arguments:
  -h, --help       show this help message and exit
  --score {F,R,P}  Rouge Variant (F1, Recall, Precision)
  --verbose
  --no-verbose
```

## Getting Started
**0) Pre-requisites**
```bash
git clone https://github.com/pltrdy/pythonrouge.git
cd pythonrouge
python setup.py install
```

**1) Clone the repo, setup the module and ROUGE**
```bash
git clone https://github.com/pltrdy/files2rouge.git     
cd files2rouge
python setup_rouge.py
python setup.py install
```
**Do not forget to run `setup_rouge`**    

**2) Run `files2rouge.py`** 
```bash
files2rouge summaries.txt references.txt --verbose 
```

**Outputs:**
When `--verbose` is set, the script prints progress and remaining time on `stderr`.   
At the end, metrcis averages are printed:
- ROUGE-1
- ROUGE-2
- ROUGE-3
- ROUGE-L
- ROUGE-S4

[More information about ROUGE metric](http://83.212.103.151/~mkalochristianakis/techNotes/ipromo/rougen5.pdf)

## More informations
* **Use cases:**
  * [Text Summarization using OpenNMT](./experiments/openNMT.0.md)
* About `files2rouge.py`: run `files2rouge.py --help`
* About ROUGE Metric: [project webpage](http://www.berouge.com/Pages/default.aspx)

