# Files2ROUGE
Multi-threaded ROUGE scoring.   
It uses [pythonrouge](https://github.com/pltrdy/pythonrouge).   

## Motivations
Computing ROUGE score between an automatically generated summary and a reference file.

## Getting Started
**1) Clone the repo & get submodules**
```bash
git clone --recursive https://github.com/pltrdy/files2rouge.git     
cd files2rouge
```
(If you want to install `pythonrouge` run `cd pythonrouge && sudo pip install .`)
**2) Run `files2rouge.py`** 
```bash
./files2rouge.py --ref references.txt --summ summary.txt --verbose
```

## More informations
* **Use cases:**:
  * [Text Summarization using OpenNMT](./experiments/openNMT.0.md)
* About `files2rouge.py`: run `./files2rouge.py --help`
* About ROUGE Metric: [project webpage](http://www.berouge.com/Pages/default.aspx)

