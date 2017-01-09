# Files2ROUGE
Multi-threaded ROUGE scoring

## Motivations
Computing ROUGE score between an automatically generated summary and a reference file.

## Getting Started
**1) Clone the repo & get submodules**
```bash
git clone git@github.com:pltrdy/files2rouge.git     
cd files2rouge
git submodule init
git submodule update
```

**2) Run `files2rouge.py`** 
```bash
./files2rouge.py --ref references.txt --summ summary.txt --verbose
```

## More informations
* About `files2rouge.py`: run `./files2rouge.py --help`
* About ROUGE Metric: [project webpage](http://www.berouge.com/Pages/default.aspx)
