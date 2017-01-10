
# Motivations

* Replicate results for Text Summarization task on Gigaword (see 'About')
* Getting started with Text Summarization using `OpenNMT` ([src](https://github.com/OpenNMT/OpenNMT))
* Getting started with ROUGE scoring using `files2rouge` ([src](https://github.com/pltrdy/files2rouge)) 

# About
 * Reference: http://opennmt.net//Models/#english-summarization
 * Dataset: https://github.com/harvardnlp/sent-summary 
 * Expected results:
   * R1: 33.13 
   * R2: 16.09 
   * RL: 31.00
 * OpenNMT v0.2.0. (precisely using commit from the 4th of Jan., 2017, 561994adcd147f9f77cc744a041152c3182a9300)
 * file2rouge commit: 5397befa8397017964d21aa61a4e399dedd5c340

# Setup

```shell
git clone https://github.com/OpenNMT/OpenNMT.git opennmt
git clone --recursive https://github.com/pltrdy/files2rouge.git files2rouge
```
Download data from [here](https://github.com/harvardnlp/sent-summary) and extract (`tar -xzf summary.tar.gz`) to `./data`.


**We assume that your file system is like:**

```
./   
  opennmt/   
  data/   
  file2rouge/   
```

# Building model
Following the [guide](http://opennmt.net//Guide/)
```shell
# First, move to OpenNMT dir
cd opennmt
```
**1) Preprocess**   
```shell
th preprocess.lua -train_src ../data/train/train.article.txt -train_tgt ../data/train/train.title.txt -valid_src ../data/train/valid.article.filter.txt -valid_tgt ../data/train/valid.title.filter.txt -save_data ../data/train/textsum
```
**2) Train**   
```shell
th train.lua -data ./textsum_train/textsum-train.t7  -save_model textsum
```
or using GPU:
```shell
th train.lua -data ./textsum_train/textsum_model-train.t7  -save_model textsum -gpuid 1
```
**3) Generate summary**   
```shell
th translate.lua -model textsum_final.t7 -src ../data/Giga/inputs.txt
```
**(add `-gpuid 1` if you trained the model using GPU)**     
The output will be in `pred.txt`

# ROUGE Scoring using `files2rouge`
```shell
cd ../files2rouge
./files2rouge --ref ../data/Giga/task1_ref0.txt --summ ../opennmt/pred.txt
```

# Results
| ROUGE-1 | ROUGE-2 | ROUGE-L |
|---------|---------|---------|
|  34.2   |  16.2   |  31.9   |
