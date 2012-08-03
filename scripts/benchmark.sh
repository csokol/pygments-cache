#!/bin/sh

declare -a PYGMENTS_TO_TEST

#PYGMENTS_TO_TEST[0]=/home/csokol/caelum/pygments-cache/pygmentize-cached
PYGMENTS_TO_TEST[0]=/usr/bin/pygmentize
PYGMENTS_TO_TEST[1]=/usr/bin/pygmentize-cached
#PYGMENTIZE_CACHED_PATH=pygmentize-cached

run_a_pygmentize() {
    for file in $(ls examples); do
        #echo $file
        $PYGMENTIZE_TO_RUN -o ~/tmp/$file.html -f html examples/$file
    done
}

echo "starting benchmark for $(ls examples | wc -l) files..."
echo ""

for path in "${PYGMENTS_TO_TEST[@]}"; do
    PYGMENTIZE_TO_RUN=$path
    echo "timings for: $path"
    time run_a_pygmentize
    echo ""
done
