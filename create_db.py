#!/bin/env python3

import sqlalchemy as alch
from os import path
from os import stat
from os import sep
from os import walk
from os import getcwd
import sqlalchemy.types as a_types
import sqlalchemy.ext as alch_ext
import sqlalchemy.engine as a_ngin
from sqlalchemy import Column as Col
from sqlalchemy.ext.declarative import declarative_base
import acoustid

Base = declarative_base()

class SQLiteDB(object):
    file_path = None
    could_not_connect_error='Could not connect to named database: '
    self.Engine = alch.engine.Engine
    

    def __init__(self):
        engine = a_ngin.create_engine('sqlite:///:memory:', echo=True)

    def __init__(self, db_name):
        try:
            file_path = path.join(getcwd(), db_name)
            engine = a_ngin.create_engine(f'sqlite://{file_path}', echo=True)
        except:
            print(f'{could_not_connect_error}{db_name} in the current working directory: {getcwd()}')

    def __init__(self, db_name, working_dir):
        try:
            file_path = path.join(working_dir, db_name)
            engine = a_ngin.create_engine(f'sqlite://{file_path}', echo=True)
        except:
            print(f'{could_not_connect_error}{db_name} in the working directory: {working_dir}')

class Dirs_Table_Row(Base):
    __tablename__ = 'dirs'
    def __init__(self, database):
        pass
    inode = Col(a_types.Integer, primary_key=True)
    dir_nam = Col(a_types.String)
    parent_inode = alch.Column(a_types.Integer, alch.ForeignKey("Dirs_Table_Row.inode"))
    direct_child_count = Col(a_types.Integer)
    recursive_child_count = Col(a_types.Integer)


class Files_Table_Row(Base):
    __tablename__ = 'files'
    def __init__(self, database):
        pass
    id = Col(a_types.Integer, primary_key=True)
    dir_nam = Col(a_types.String)
    parent_inode = Col(a_types.Integer, alch.ForeignKey(Dirs_Table_Row.inode))
    size = Col(a_types.Integer)
    is_audio = Col(alch.Boolean)


class Audio_Metadata_Table_Row(Base):
    __tablename__ = 'audio_metadata'
    def __init__(self, database):
        pass
    id = Col(a_types.Integer, alch.ForeignKey(Files_Table_Row.id))
    codec = Col(a_types.String)
    bit_rate = Col(a_types.Integer)
    title = Col(a_types.String)
    artist = Col(a_types.String)
    album = Col(a_types.String)
    date = Col(a_types.String)
    duration = Col(a_types.Float)
    genre = Col(a_types.String)
    acoustid = Col(a_types.String)
    json = Col(a_types.LargeBinary)

def main():
    Music_Database = SQLiteDB('music.sqlitedb')

    # TODO: Implement walk(getcwd) to iterate through dirs and populate Dirs table
    for (root, dirs, files) in walk(getcwd()):
        direct_subdirs_count = 0
        excluded_subdirectories = ("Album Artwork","iTunes")
        #dirs[:] = [_ for _ in dirs if  ] ###  TODO: maxdepth=1?
        dirs[:] = [_ for _ in dirs if _ not in excluded_subdirectories]
        for dir in dirs:
            direct_subdirs_count+=1
        dir_inode = stat(root).st_ino
        dir_name = path.basename(root)
        print(f'{dir_inode}, {direct_subdirs_count}, {dir_name}')
        

    # TODO: Implement walk(getcwd) to iterate through files and populate Files & Metadata tables, possibly concurrently?

if __name__ == "__main__":
    main()
