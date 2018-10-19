#!/bin/bash

if [ -z $1 ]; then
	echo "Need to supply search mask (e.g cache, or vs for all)"
	exit
fi

pcnt=0

for f in replays/*$1*.dem; do

	if [ $pcnt -gt 3 ]; then
    	wait
    	pcnt=0
	fi

	csvfile=csv/$(basename "${f%.*}").csv
	if [ ! -f $csvfile ]; then
		echo "[$pcnt] Parsing $f to $csvfile"
		node parsePlayerPositions.js $f > $csvfile &
		pcnt=$((pcnt + 1))
	else
		echo "$csvfile already exists"
	fi
done

wait

echo "All parsing done"
