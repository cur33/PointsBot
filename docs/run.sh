#!/usr/bin/env bash

docfiles=( $(ls *.md) )
for fname in "${docfiles[@]}"; do
    outname="${fname/%md/html}"
    pandoc -s -f gfm -t html $fname -o $outname --metadata pagetitle="$outname"
    open $outname
done
