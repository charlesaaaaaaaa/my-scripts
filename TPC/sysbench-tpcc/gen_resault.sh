tail -25 $1 | sed 's/./||/' | sed 's/$/||/' | sed 's/:/:||/' > resault_$1
