#!/bin/bash

##credit to shmerl@GitHub
# Analysis of obfsuscated KoTOR II audio
#
# *** Stock mp3 encoded with lame
# position of LAME : 0x09c (156)
# position of Info : 0x024 (36)
#
# *** KoTOR II obfuscated audio (using bed_001ebo.wav)
# position of LAME : 0xc7 (199)
# position of Xing : 0x4f (79)
#
# *** Conclusion:
# Xing should match to Info, but position of Xing
# is different in different obfuscated files.
#
# Note: Some files don't have Xing, and should be handled individually.
# mus_kriea.wav       - uses regular Info instead of Xing
# mus_s_kreiaevil.wav - uses regular Info instead of Xing
# mus_a_main.wav      - uses regular Info instead of Xing
# mus_a_kreiadark.wav - uses regular Info instead of Xing
# bed_950mal.wav      - weird case (neither Xing nor Info).
#                       Chop off 58 bytes, similar to KoTOR I.
# *** Fixing method (for Xing/Info case):
# 1. Get position of first Xing/Info in the binary.
# 2. Chop everything before Xing/Info and Xing/Info itself (+4 after the position).
# 3. Prepend binary mp3 header to the result.

# Run from location where you have audio
# from the <game-dir>/StreamMusic directory.
# Make sure you have xxd hexdump tool installed.

function fix_with_header() {
   local src="$1"
   local offset="$2"
   local target_tmp="fixed/${src%%.*}.tmp"
   local target_mp3="fixed/${src%%.*}.mp3"

   echo "fixing ${src} -> ${target_mp3}"
   dd if=${src} of=${target_tmp} ibs=1 skip=${offset} obs=10M
   cat ${header_file} ${target_tmp} > ${target_mp3}
   rm ${target_tmp}   
}

function fix_chop() {
   local src="$1"
   local offset="$2"
   local target_mp3="fixed/${src%%.*}.mp3"
   
   echo "fixing ${src} -> ${target_mp3}"
   dd if=${src} of=${target_mp3} ibs=1 skip=${offset} obs=10M
}

hex_header='FFFB94640000000000000000000000000000000000000000000000000000000000000000496E666F'
header_file='fixed/header.hex'

mkdir -p fixed
echo $hex_header | xxd -r -p > $header_file

for src in *.wav; do
   if [ "$src" == "bed_950mal.wav" ]; then
      # No Xing or Info
      fix_chop "$src" 58 
   else
      match=$(grep --only-matching --byte-offset --binary --text "Xing" "$src")
      if (($? != 0)); then
         match=$(grep --only-matching --byte-offset --binary --text "Info" "$src")
         if (($? != 0)); then
            echo "Unknown case found: ${src}. Skipping."
            continue
         fi
      fi

      # Xing / Info case
      offset=$(( $(echo "$match" | cut -d : -f 1) + 4 ))
      fix_with_header "$src" $offset
   fi
done

rm $header_file