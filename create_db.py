#!/bin/env python3

import os, sqlite3, re, subprocess


dirs_table_def=\
    '''
    dirs
    (inode INT PRIMARY KEY,
    name TEXT,
    parent_inode INT,
    FOREIGN KEY (parent_inode) references dirs(inode)
    )
    '''
    

files_table_def=\
    '''
    files
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    parent INT,
    is_audio BOOLEAN,
    FOREIGN KEY (parent) references dirs(inode)
    )
    '''

metadata_table_def=\
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
    cursor.execute('INSERT INTO dirs (inode, name) VALUES (?, ?)',(os.stat('.').st_ino,'.'))
    audio_regex=re.compile('.*\.(flac|wa?v|m4a|mp[34]|ogg|wma)$', re.IGNORECASE)
    for root, dirs, files in os.walk('.'):
        for dir in dirs:
            inode=os.stat(os.path.join(root,dir)).st_ino
            parent_inode=os.stat(root).st_ino
            cursor.execute('INSERT INTO dirs(inode, name, parent_inode) VALUES (?, ?, ?)', (inode, dir, parent_inode))
            connector.commit()
        for file in files:
            if re.match(audio_regex,file):
                is_audio = True
            else:
                is_audio = False
            cursor.execute('INSERT INTO files (name, parent, is_audio) VALUES (?, ?, ?)', (file,parent_inode, is_audio))
            connector.commit()
    pass