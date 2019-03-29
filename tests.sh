#!/bin/bash

# python3 downloadMusic.py > log/downloadMusic.log

for i in {2..4}
do
   python3 runHashprint.py $i > log/runHashprint_$i.log
done


