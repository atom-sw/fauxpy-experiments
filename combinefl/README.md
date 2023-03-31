# CombineFL on BugsInPy

## Requirements

We built our package in this directory 
on top of the replication package of
[CombineFL](https://damingz.github.io/combinefl/index.html).
Since `CombineFL` is written in Python 2.7, we also
used Python 2.7 for the package in this directory
to be able to adopt it to our experiments with only a few changes.
Thus, this package is only tested on Python 2.7 and may not work
on Python 3.

The package `CombineFL` uses
[Support Vector Machine for Ranking](https://www.cs.cornell.edu/people/tj/svm_light/svm_rank.html),
which is already included in the current package in [SVMRank](SVMRank) directory.
So, there is no need to download it or install it.

## Supporting BugsInPy

In order to run `CombineFL` on BugsInPy, we replaced the
Defects4j's `release.json`
file with BugsInPy's `release_x.json` files (since the file
was to big, we split it into 10 files so that we could push
it to the repo), and Defects4j's `qid-lines.csv` 
with BugsInPy's `qid-lines.csv`. We generated these files at the
metric computation phase. We also change the rechniques names and
subject information in [1-combine.py](1-combine.py) to support BugsInPy.

## Running CombineFL on BugsInPy

To run `CombineFL` on BugsInPy, run the following commands in order:

```
python 1-combine.py

./2-split.sh

./3-crossvalidation.sh

python 4-calc-metric.py
```

## Results






