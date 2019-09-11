#!/usr/bin/env bash
IFS=$'\n';
find "$(pwd)" -type f -name "jobs.txt" -delete

for f in $(find . -regextype egrep -iregex ".*\.(flac|wav|m4a|mp3|ogg|wma)$") ;
do
    extension=${f##*.}
    codec=$(ffprobe -v error -select_streams a:0 -show_entries stream=codec_name -of default=nk=1:nw=1 "$f")
    bitrate=$(ffprobe -v quiet -select_streams a:0 -show_entries stream=bit_rate -of default=nk=1:nw=1 "$f")
    max_bitrate=256000

    # To be added back in after parallelizing sqlitedb population
    # case "$extension" in
    #     flac|wav|wma) SELECT * from files where extension ~ "(flac|wav|wma) "
    #         echo "ffmpeg -y -i \"$f\" -vn -c:a aac -b:a 192k \"${f%.*}.m4a\"" >> jobs.txt ;;
    #     mp3|ogg)
    #         if (( $bitrate > $max_bitrate ));
    #         then echo "ffmpeg -y -i \"$f\" -vn -c:a aac -b:a 192k \"${f%.*}.m4a\"" >> jobs.txt ;
    #         fi ;;
    #     m4a)
    #         if [[ "$codec" = 'alac' ]];
    #         then echo "ffmpeg -y -i \"$f\" -vn -c:a aac -b:a 192k \"${f%.*}_lossy.m4a\"" >> jobs.txt ;
    #         elif (( "$bitrate" > $max_bitrate ));
    #         then echo "ffmpeg -y -i \"$f\" -vn c:a aac -b:a 192k \"${f%.*}_lossier.m4a\"" >> jobs.txt ;
    #         fi ;;
    # esac ;
done ;
parallel --bar --eta :::: jobs.txt