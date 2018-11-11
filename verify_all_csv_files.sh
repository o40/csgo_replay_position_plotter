#!/bin/bash

for f in csv/*.csv; do
	./verify_csv_data.py --input $f
	if [ $? != 0 ]; then
		mv $f csv/broken
	fi
done

echo "Verification done"
