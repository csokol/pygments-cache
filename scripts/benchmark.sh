#!/bin/sh

PYGMENTIZE_CACHED_PATH=pygmentize-cached

run_original() {
    for file in $(ls examples); do
        #echo $file
        pygmentize -o ~/tmp/$file.html -f html examples/$file
    done
}
run_cached() {
    for file in $(ls examples); do
        #echo $file
        $PYGMENTIZE_CACHED_PATH -o ~/tmp/$file.html -f html examples/$file
    done
}

echo "starting benchmark for $(ls examples | wc -l) files..."
echo ""

echo "original pygmentize timings: "
time run_original
echo ""

echo "pygmentize-cached timings: "
time run_cached