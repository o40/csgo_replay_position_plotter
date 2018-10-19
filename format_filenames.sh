#!/bin/bash
for file in replays/*; do
    if [[ $file == *"(2)"* ]]; then
    	echo "Renaming $file to ${file/ (2)/_2}"
    	mv "$file" "${file/ (2)/_2}"
    fi
    if [[ $file == *"(3)"* ]]; then
    	echo "Renaming $file to ${file/ (3)/_3}"
    	mv "$file" "${file/ (3)/_3}"
    fi
done