#!/bin/env python3

import os
import sqlite3

dirs_table_def=\
    '''
    dirs
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    parent TEXT,
    parent_id INT
    )
    '''
    
#FOREIGN KEY (parent_id) references dirs(id)

files_table_def=\
    '''
    files
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent INT
    name TEXT,
    extension TEXT,
    codec TEXT,
    bit_rate INT,
    converted BOOLEAN,
    FOREIGN KEY (parent) references dirs(id)
    )
    '''

if __name__ == "__main__":
    cwd = os.getcwd()
    db_file = "music.sqlitedb"
    db_file_path = cwd + "/" + db_file
    if os.path.isfile(db_file_path):
        os.remove(db_file_path)
    connector = sqlite3.connect(db_file)
    cursor = connector.cursor()
    cursor.execute('PRAGMA foreign_keys = ON;')
    cursor.execute('PRAGMA journal_mode = WAL;')
    cursor.execute('CREATE TABLE IF NOT EXISTS %s' % dirs_table_def)
    cursor.execute('CREATE TABLE IF NOT EXISTS %s' % files_table_def)
    for root, dirs, files in os.walk(cwd):
        for dir in dirs:
            cursor.execute('INSERT INTO dirs(name,parent) VALUES (?, ?)', (dir,root,))
            print(f'INSERTING {dir}')
    pass