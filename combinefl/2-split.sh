#!/bin/bash
if [ x$1 != x ]; then
    n=$1
else
    n=10
fi

# split
for (( i=0; i<$n; i++ )) do
    python split.py $i $n &
done
wait
echo "$n-fold split finished."
