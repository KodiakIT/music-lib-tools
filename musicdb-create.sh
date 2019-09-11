#!/usr/bin/env bash
IFS=$'\n';

db_name="music.sqlitedb"

files_table_def="(                              \
    id INTEGER PRIMARY KEY AUTOINCREMENT,       \
    canonical_path TEXT,                        \
    name TEXT,                                  \
    extension TEXT,                             \
    codec TEXT,                                 \
    bit_rate INT,                               \
    converted BOOLEAN                           \
    )"

files_row_format="(canonical_path,name,extension,codec,bit_rate)"

function initialize_db_row() {
    local canonical_path
    local name
    
    canonical_path=$(readlink -f "$1")    
    name=${1##*/}
    row=$(printf '("%s","%s")' "$canonical_path" "$name")

    sqlite3 -batch "$db_name" "INSERT INTO files (canonical_path, name) VALUES $row ;"
}

function populate_db_row() {
    local id
    local extension
    local codec
    local bit_rate

    id=$(sqlite3 -batch "$db_name" 'SELECT id FROM files WHERE codec IS NULL LIMIT 1;')
    name=$(sqlite3 -batch "$db_name" "SELECT name FROM files WHERE id=$id")

    extension=${name##*.}
    extension=${extension,,}
    codec=$(ffprobe -v error -select_streams a:0 -show_entries stream=codec_name -of default=nk=1:nw=1 "$1")
    bit_rate=$(ffprobe -v quiet -select_streams a:0 -show_entries stream=bit_rate -of default=nk=1:nw=1 "$1")

    printf '("%s","%s","%s")' "$extension" "$codec" "$bit_rate"
}

export db_name
export files_row_format
export -f initialize_db_row
export -f populate_db_row

find "$(pwd)" -type f -name "music.sqlitedb" -delete

sqlite3 -batch "$db_name" "CREATE TABLE files $files_table_def ;"
sqlite3 -batch "$db_name" "PRAGMA journal_mode=wal2;"

find . -regextype egrep -iregex ".*\.(flac|wa?v|m4a|mp[34]|ogg|wma)$" -exec bash -c 'initialize_db_row "$0"' {} \;

running=0
maxjobs=8;
for elem in "${array[@]}";
do if (( running++ >= n ));
then wait -n;
fi; populate_db_row "$elem" & done;
wait