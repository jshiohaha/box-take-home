#!/bin/bash
for fullfile in "./Test/*.in"; do
    for file in $fullfile; do
    	filename=$(basename "$file")
		extension="${filename##*.}"
		filename="${filename%.*}"

		input="$filename.in"
		output="$filename.out"

		# echo -e 'input: \t' $input
		# echo -e 'output: ' $output

		echo 'python myShogi.py -f ./Test/' $input
		# python 'myShogi.py' -f './Test/'$input > output.out | diff -u './Test/'$output - 
    done
done