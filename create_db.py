import sqlalchemy as alch
from os import path
from os import walk
from os import getcwd
import sqlalchemy.types as alch_types
import sqlalchemy.ext as alch_ext
import sqlalchemy.engine as alch_engine
from sqlalchemy.ext.declarative import declarative_base
import acoustid


class SQLiteDB(object):
    file_path = None
    base = declarative_base()
    def __init__(self):
        engine = alch.create_engine('sqlite:///:memory:', echo=True)
    def __init__(self, db_name):
        try:
            file_path = path.join(getcwd, db_name)
            engine = alch.create_engine(f'sqlite://{file_path}', echo=True)
        except:
            print("Uh-oh")

class Dirs_Table_Row(SQLiteDB):
    __tablename__ = 'dirs'
    def __init__(self, database):
        pass
    inode = alch.Column(alch_types.Integer, primary_key=True)
    name = alch.Column(alch.String)
    parent_inode = alch.Column(alch.Integer, alch.ForeignKey(Dirs_Table_Row.inode))


class Files_Table_Row(SQLiteDB):
    __tablename__ = 'files'
    def __init__(self, database):
        pass
    id = alch.Column(alch.Integer, primary_key=True)
    name = alch.Column(alch.String)
    parent_inode = alch.Column(alch.Integer, alch.ForeignKey(Dirs_Table_Row.inode))
    size = alch.Column(alch.Integer)
    is_audio = alch.Column(alch.Boolean)


class Audio_Metadata_Table_Row(SQLiteDB):
    __tablename__ = 'audio_metadata'
    def __init__(self, database):
        pass
    id = alch.Column(alch.Integer, alch.ForeignKey(Files_Table_Row.id))
    codec = alch.Column(alch.String)
    bit_rate = alch.Column(alch.Integer)
    title = alch.Column(alch.String)
    artist = alch.Column(alch.String)
    album = alch.Column(alch.String)
    date = alch.Column(alch.String)
    duration = alch.Column(alch.Float)
    genre = alch.Column(alch.String)
    acoustid = alch.Column(alch.String)

Music_Database = SQLiteDB('music.sqlitedb')

def main():
    # TODO: Implement walk(getcwd) to iterate through dirs and populate Dirs table
    # TODO: Implement walk(getcwd) to iterate through files and populate Files & Metadata tables, possibly concurrently?
    pass

if __name__ == "__main__":
    main()