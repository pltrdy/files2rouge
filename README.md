# Files2ROUGE
## Motivations
Given two files with the same number of lines, `files2rouge` calculates the average ROUGE scores of each sequence (=line). Each sequence may contain multiple sentences. In this case, the end of sentence string must be passed using the `--eos` flag (default: "."). Running `files2rouge` with a wrong eos delimiter may lead to incorrect ROUGE-L score.

```shell
$ files2rouge -h
usage: files2rouge [-h] [-v] [-s SAVETO] [-e EOS] summary reference

Calculating ROUGE score between two files (line-by-line)

positional arguments:
  summary               Path of summary file
  reference             Path of references file

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Prints ROUGE logs
  -s SAVETO, --saveto SAVETO
                        File to save scores
  -e EOS, --eos EOS     End of sentence separator (for multisentence).
                        Default: "."
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
files2rouge summaries.txt references.txt
```

**Outputs:**
When `--verbose` is set, the script prints progress and remaining time on `stderr`.  This can be changed using `--verbose` in order to outputs ROUGE execution logs. 

Default output example:
```
Preparing documents...
Running ROUGE...
---------------------------------------------
1 ROUGE-1 Average_R: 0.28242 (95%-conf.int. 0.25721 - 0.30877)
1 ROUGE-1 Average_P: 0.30157 (95%-conf.int. 0.27114 - 0.33506)
1 ROUGE-1 Average_F: 0.28196 (95%-conf.int. 0.25704 - 0.30722)
---------------------------------------------
1 ROUGE-2 Average_R: 0.10395 (95%-conf.int. 0.08298 - 0.12600)
1 ROUGE-2 Average_P: 0.11458 (95%-conf.int. 0.08873 - 0.14023)
1 ROUGE-2 Average_F: 0.10489 (95%-conf.int. 0.08303 - 0.12741)
---------------------------------------------
1 ROUGE-L Average_R: 0.25231 (95%-conf.int. 0.22709 - 0.27771)
1 ROUGE-L Average_P: 0.26830 (95%-conf.int. 0.23834 - 0.29818)
1 ROUGE-L Average_F: 0.25142 (95%-conf.int. 0.22741 - 0.27533)

Elapsed time: 0.458 secondes

```

## ROUGE Args
One can specify which ROUGE args to use using the flag `--args` (or `-a`).    
The default behavior is equivalent to: 
```
files2rouge summary.txt reference.txt -a "-c 95 -r 1000 -n 2 -a" # be sure to write args betwen double-quotes
```
You can find more informations about these arguments [here](./files2rouge/RELEASE-1.5.5/README.txt)

## More informations
* [ROUGE Original Paper (Lin 2004)](http://www.aclweb.org/anthology/W04-1013)
* [ROUGE-1.5.5/README.txt](./files2rouge/RELEASE-1.5.5/README.txt)
* **Use cases:**
  * [Text Summarization using OpenNMT](./experiments/openNMT.0.md)
* About `files2rouge.py`: run `files2rouge.py --help`
