#!/bin/env python3

import os
import sqlite3
import re
import subprocess
import json

dirs_table_def =\
    '''
    dirs
    (inode INT PRIMARY KEY,
    name TEXT,
    parent_inode INT,
    FOREIGN KEY (parent_inode) references dirs(inode)
    )
    '''

files_table_def =\
    '''
    files
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    (id INT,
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
    cursor.execute('CREATE TABLE IF NOT EXISTS %s' % dirs_table_def)
    cursor.execute('CREATE TABLE IF NOT EXISTS %s' % files_table_def)
    cursor.execute('CREATE TABLE IF NOT EXISTS %s' % metadata_table_def)
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
    cursor.execute('INSERT INTO metadata(id) SELECT files.id FROM files WHERE (files.is_audio=1)')
    connector.commit()
    # cursor.execute('WITH RECURISIVE filepath()')
    # file_path = os.path.join(os.path.abspath(root), file)
    # ffprobe_command = ['ffprobe', '-v', 'error', '-select_streams', 'a:0',
    #                     '-show_format', '-show_streams', '-of', 'json=compact=1', file_path]
    # _subprocess = subprocess.run(ffprobe_command, capture_output=True)
    # ffprobe_json = _subprocess.stdout

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
