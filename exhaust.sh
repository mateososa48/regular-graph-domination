#!/bin/bash
# sequential exhaustive checks; results appended to exhaust.log
run() { d=$1; n=$2; s=$(date +%s); r=$(nauty-geng -cq -d$d -D$d $n | ./regcheck $d 2>&1 | tr '\n' ' '); echo "deg=$d n=$n $r [$(( $(date +%s)-s ))s]" >> exhaust.log; }
for n in 6 8 10 12; do run 5 $n; done
for n in 7 8 9 10 11 12; do run 6 $n; done
for n in 4 6 8 10 12 14 16 18; do run 3 $n; done
run 4 15
run 5 14
run 6 13
run 3 20
run 4 16
run 3 22
