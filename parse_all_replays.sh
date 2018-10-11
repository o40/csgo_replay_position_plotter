#!/bin/bash

if [ -z $1 ]; then
	echo "Need to supply search mask (e.g cache)"
	exit
fi

for f in replays/*$1*.dem; do
	csvfile=csv/$(basename "${f%.*}").csv
	if [ ! -f $csvfile ]; then
		echo "Parsing $f to $csvfile"
		# node parsePlayerPositions.js $f > $csvfile
	else
		echo "$csvfile already exists"
	fi
done
