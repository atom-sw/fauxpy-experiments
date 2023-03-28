# CombineFL on BugsInPy

## Requirements

We built our package in this directory 
on top of the replication package of
[CombineFL](https://damingz.github.io/combinefl/index.html).
Since `CombineFL` is written on Python 2.7, we also
used Python 2.7 for the package in this directory
to be able to adopt it to our experiments with only a few changes.
Thus, this package is only tested on Python 2.7 and may not work
on Python 3. The package `CombineFL` uses
[Support Vector Machine for Ranking](https://www.cs.cornell.edu/people/tj/svm_light/svm_rank.html),
which is already included in the package in [SVMRank](SVMRank) directory.
So, there is no need to download it or install it.
