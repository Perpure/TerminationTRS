#!/bin/bash

for (( count=1; count<=100; count++ ))
  do
    echo Test "$count"
    ./test_gen 
    timeout 15 python3 run_test.py
    rm -f test.trs
    ./test_check
    rm -f result
  done
./total_results
rm -f witness.txt pass.txt
sleep 1
