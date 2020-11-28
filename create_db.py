#!/bin/env python3

from os import path, getcwd, walk, stat

import sqlalchemy as alch
import sqlalchemy.engine as a_engine
import sqlalchemy.types as a_types
from sqlalchemy import Column
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class SQLiteDB(object):
    file_path = None
    could_not_connect_error = 'Could not connect to named database: '
    engine = None

    def __init__(self, db_name):
        # 2 args
        # try:
        #     file_path = path.join(working_dir, db_name)
        #     self.engine = a_engine.create_engine(f'sqlite://{file_path}', echo=True)
        #     self.engine.connect()
        # except:
        #     print(f'{self.could_not_connect_error}{db_name} in the working directory: {working_dir}')    

        # db_name = args[0]
        # working_directory = args[1]
        try:
            engine = a_engine.create_engine(f'sqlite:///{db_name}')
            engine.connect()
        except:
            print(f'{self.could_not_connect_error}{db_name} in the current working directory: {getcwd()}')

        # No args
        # self.engine = a_engine.create_engine('sqlite:///:memory:', echo=True)
        # print('Warning: working in memory-only DB')
        # self.engine.connect()
    # engine.echo = True


class Dirs_Table_Row(Base):
    __tablename__ = 'dirs'

    def __init__(self, database):
        pass

    inode = Column(a_types.Integer, primary_key=True)
    dir_nam = Column(a_types.String)
    parent_inode = alch.Column(a_types.Integer, alch.ForeignKey("Dirs_Table_Row.inode"))
    direct_child_count = Column(a_types.Integer)
    recursive_child_count = Column(a_types.Integer)


class Files_Table_Row(Base):
    __tablename__ = 'files'

    def __init__(self, database):
        pass

    id = Column(a_types.Integer, primary_key=True)
    dir_nam = Column(a_types.String)
    parent_inode = Column(a_types.Integer, alch.ForeignKey(Dirs_Table_Row.inode))
    size = Column(a_types.Integer)
    is_audio = Column(alch.Boolean)


class Audio_Metadata_Table_Row(Base):
    __tablename__ = 'audio_metadata'

    def __init__(self, database):
        pass

    id = Column(a_types.Integer, alch.ForeignKey(Files_Table_Row.id), primary_key=True)
    codec = Column(a_types.String)
    bit_rate = Column(a_types.Integer)
    title = Column(a_types.String)
    artist = Column(a_types.String)
    album = Column(a_types.String)
    date = Column(a_types.String)
    duration = Column(a_types.Float)
    genre = Column(a_types.String)
    acoustid = Column(a_types.String)
    json = Column(a_types.LargeBinary)


def main():
    Music_Database = SQLiteDB('music.db')
    print(Music_Database)
    Base = declarative_base()
    # TODO: Implement walk(getcwd) to iterate through dirs and populate Dirs table
    for (root, dirs, files) in walk(getcwd()):
        direct_subdirs_count = 0
        excluded_subdirectories = ("Album Artwork", "iTunes")
        # dirs[:] = [_ for _ in dirs if  ] ###  TODO: maxdepth=1?
        dirs[:] = [_ for _ in dirs if _ not in excluded_subdirectories]
        for dir in dirs:
            direct_subdirs_count += 1
        dir_inode = stat(root).st_ino
        dir_name = path.basename(root)
        print(f'{dir_inode}, {direct_subdirs_count}, {dir_name}')

    # TODO: Implement walk(getcwd) to iterate through files and populate Files & Metadata tables, possibly concurrently?


if __name__ == "__main__":
    main()
