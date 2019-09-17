#!/bin/env python3

import os
import sqlite3
import re
import subprocess
import json

dirs_table_def =\
    '''
    dirs
    (inode INTEGER PRIMARY KEY,
    name TEXT,
    parent_inode INT,
    FOREIGN KEY (parent_inode) references dirs(inode)
    )
    '''

files_table_def =\
    '''
    files
    (id INTEGER PRIMARY KEY,
    name TEXT,
    parent_inode INT,
    size INT,
    is_audio BOOLEAN,
    FOREIGN KEY (parent_inode) references dirs(inode)
    )
    '''

metadata_table_def =\
    '''
    metadata
    (
    id INTEGER,
    extension TEXT,
    codec TEXT,
    bit_rate INT,
    converted BOOLEAN,
    FOREIGN KEY (id) references files(id)
    )
    '''

audio_file_extension_regex = re.compile('.*\.(flac|wa?v|m4a|mp[34]|ogg|wma)$', re.IGNORECASE)

def initialize_db(connector, cursor, wd):
    cursor.execute('PRAGMA foreign_keys = ON;')
    cursor.execute('PRAGMA journal_mode = WAL;')
    cursor.execute(f'CREATE TABLE IF NOT EXISTS {dirs_table_def}')
    cursor.execute(f'CREATE TABLE IF NOT EXISTS {files_table_def}')
    cursor.execute(f'CREATE TABLE IF NOT EXISTS {metadata_table_def}')
    cursor.execute('INSERT INTO dirs (inode, name) VALUES (?, ?)',
                   (os.stat(wd).st_ino, os.path.abspath(wd)))
    connector.commit()

def populate_dirs_table(connector, cursor, wd):
    for root, dirs, files in os.walk(wd):
        for dir in dirs:
            inode = os.stat(os.path.join(root, dir)).st_ino
            parent_inode = os.stat(root).st_ino
            cursor.execute('''INSERT INTO dirs(inode, name, parent_inode)
                            VALUES (?, ?, ?)''', (inode, dir, parent_inode))
    connector.commit()

def populate_files_table(connector, cursor, wd):
    for root, dirs, files in os.walk(wd):
        for file in files:
            if re.match(audio_file_extension_regex, file): 
                is_audio = True 
            else:
                is_audio = False
            parent_inode = os.stat(root).st_ino
            cursor.execute('INSERT INTO files (name, parent_inode, size, is_audio) VALUES (?, ?, ?, ?)',
                           (file, parent_inode, os.stat(os.path.join(root,file)).st_size, is_audio))
    connector.commit()


def populate_metadata_table(connector, cursor, wd):
    empty_metadata_query='FROM files JOIN metadata ON files.id = metadata.id WHERE files.is_audio IS TRUE and codec IS NULL'
    cursor.execute('INSERT INTO metadata(id) SELECT files.id FROM files WHERE (files.is_audio=1)')
    connector.commit()
    audio_files_count = (cursor.execute(f'SELECT COUNT(*) {empty_metadata_query}').fetchall())[0]
    print(audio_files_count)
    while audio_files_count[0] > 0:
        file_id = cursor.execute(f'SELECT metadata.id {empty_metadata_query} LIMIT 1').fetchall()
        # Get full path from DB
        selection = cursor.execute('''
                        WITH RECURSIVE filepath(parent, name, dir_level) AS
                        (SELECT files.parent_inode, files.name, 0 FROM FILES WHERE files.id = (?)
                        UNION SELECT dirs.parent_inode, dirs.name, filepath.dir_level+1 FROM dirs, filepath WHERE inode=filepath.parent)
                        SELECT filepath.name FROM filepath ORDER BY dir_level DESC''', file_id)
        file_path = os.path.join(*(s[0] for s in selection))
        ffprobe_command = ['ffprobe', '-v', 'error', '-select_streams', 'a:0',
                           '-show_format', '-show_streams', '-of', 'json=compact=1', file_path]
        ffprobe_stdout = subprocess.run(ffprobe_command, capture_output=True).stdout
        ffprobe_json = json.loads(ffprobe_stdout)
        codec = ffprobe_json["streams"][0]["codec_name"]
        file_format = ffprobe_json["format"]["format_name"]
        cursor.execute('INSERT INTO metadata (id, codec, extension) VALUES (?, ?, ?)', (file_id, codec, file_format))
        audio_files_count_sql = cursor.execute(f'SELECT count(files.id) {empty_metadata_query}')
        connector.commit()


def main():
    cwd = os.getcwd()
    db_file = "music.sqlitedb"
    db_file_path = os.path.join(cwd, db_file)
    if os.path.isfile(db_file_path):
        os.remove(db_file_path)
    connector = sqlite3.connect(db_file)
    cursor = connector.cursor()
    initialize_db(connector, cursor, '.')
    populate_dirs_table(connector, cursor, '.')
    populate_files_table(connector, cursor, '.')
    populate_metadata_table(connector, cursor, '.')

if __name__ == "__main__":
    main()
