#! /usr/bin/env bash

# ./convert.sh *.m4a *.flac *.wav
# ./convert.sh $(find . -iname "*.m4a")
# etc

_convert() {
    local name=${1##*/}
    local codec=$(ffprobe -v error -select_streams a:0 -show_entries stream=codec_name -of default=nk=1:nw=1 "$1")
    case "$codec" in
        flac|pcm_s16le|alac)
            ffmpeg -y -i "$1" -vn -c:a aac -b:a 192k "${name%.*}_lossy.m4a" ;;
        aac)
            ffmpeg -y -i "$1" -vn -c:a copy "${name%.*}_copy.m4a" ;;
    esac
}

export -f _convert

for f; do printf '%s\0' "$f"; done | xargs -0 -I{} -n1 -P4 $SHELL -c '_convert "{}"'