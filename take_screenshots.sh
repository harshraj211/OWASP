#!/bin/bash
set -e

cd /home/kali/Desktop/OSWAP

mkdir -p docs/images

declare -A ports=(
    ["a07-easy"]=6019
    ["a07-medium"]=6020
    ["a07-hard"]=6021
    ["a08-easy"]=6022
    ["a08-medium"]=6023
    ["a08-hard"]=6024
    ["a09-easy"]=6025
    ["a09-medium"]=6026
    ["a09-hard"]=6027
    ["a10-easy"]=6028
    ["a10-medium"]=6029
    ["a10-hard"]=6030
)

for chal in "${!ports[@]}"; do
    # parse a07-easy into a07 easy
    IFS='-' read -ra PARTS <<< "$chal"
    cat=${PARTS[0]}
    lvl=${PARTS[1]}
    
    echo "Starting $chal..."
    ./scripts/start_challenge.sh $cat $lvl
    sleep 3
    
    port=${ports[$chal]}
    echo "Taking screenshot of http://127.0.0.1:$port/ ..."
    chromium --headless --disable-gpu --no-sandbox --window-size=1920,1080 --screenshot=/home/kali/Desktop/OSWAP/docs/images/web_${cat}_${lvl}.png http://127.0.0.1:$port/
    
    echo "Taking screenshot of /about page..."
    chromium --headless --disable-gpu --no-sandbox --window-size=1920,1080 --screenshot=/home/kali/Desktop/OSWAP/docs/images/web_${cat}_${lvl}_about.png http://127.0.0.1:$port/about
    
done

echo "Done taking screenshots."
