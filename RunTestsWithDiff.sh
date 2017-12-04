#!/bin/bash
count=0
increment=1
for fullfile in "./Test/*.in"; do
    for file in $fullfile; do
    	filename=$(basename "$file")
		extension="${filename##*.}"
		filename="${filename%.*}"

		input="$filename.in"
		output="$filename.out"
		count=$(($count+$increment))

		echo -e 'Running test '$count'... \t' $input
		python './src/myShogi.py' -f './Test/'$input | diff -u './Test/'$output -
    done
done