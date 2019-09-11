#!/bin/bash

##credit to shmerl@GitHub
# Run from location where you have audio
# from the <game-dir>/streammusic directory

mp3s=(
   [0-5]*.wav
   mus_{a,b,t}*.wav
   evil_ending.wav
   credits.wav
)

wavs=(
   al_*.wav
   mus_loadscreen.wav 
)

mkdir -p fixed

for src in ${mp3s[@]}; do
   target="fixed/${src%%.*}.mp3"
   echo "fixing ${src} -> ${target}"
   dd if=${src} of=${target} ibs=1 skip=58 obs=10M
done

for src in ${wavs[@]}; do
   target="fixed/${src}"
   echo "fixing ${src} -> ${target}"
   dd if=${src} of=${target} ibs=1 skip=470 obs=10M
done