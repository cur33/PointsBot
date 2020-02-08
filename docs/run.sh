#!/usr/bin/env bash

# If files specified, only make them; otherwise, make all
if [[ $# -gt 0 ]]; then
    docfiles=( "$@" )
else
    docfiles=( $(ls *.md) )
fi

for fname in "${docfiles[@]}"; do
    outname="_${fname/%md/html}"
    echo $fname "->" $outname
    pandoc -s -f gfm -t html $fname -o $outname --metadata pagetitle="$outname"
    open $outname
done
