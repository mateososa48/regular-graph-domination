#!/bin/bash
# Launch symmetric CEGAR block searches in the background (each writes its own log).
mkdir -p "$HOME/math-research/runs/cegar"
cd "$HOME/math-research/runs/cegar" || exit 1
P="$HOME/math-research/venv/bin/python"
S="$HOME/math-research/code/cegar_sym2.py"
widths() { local s="3"; local i=0; while [ "$i" -lt "$1" ]; do s="$s,4"; i=$((i+1)); done; echo "$s"; }
go() { nohup nice -n 5 "$P" "$S" "$1" "$2" "$(widths "$3")" 3 7 1000000000 8 > "z$1_t$2_s$3.log" 2>&1 < /dev/null & }
# Z3: one orbit of three 3-clauses (deficiency 3)
go 3 4 5; go 3 5 6; go 3 6 8
# Z4: one orbit of four 3-clauses (deficiency 4)
go 4 3 3; go 4 4 5
# Z5: one orbit of five 3-clauses (deficiency 5)
go 5 3 3; go 5 4 5; go 5 5 6; go 5 6 8
sleep 1
ps aux | grep cegar_sym2 | grep -v grep | wc -l
