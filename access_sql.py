import os
import sqlite3
from typing import List


class Paper:
    def __init__(self):
        self.title = None
        self.authors = None
        self.abstract = None
        self.url = None
        self.doi = None
        self.pages = None
        self.language = None
        self.isbn = None

        self.conference_name = None
        self.address = None
        self.month = None
        self.year = None

    def add_info(self, title, authors, conference_name, address):
        self.title = title
        self.authors = authors
        self.conference_name = conference_name
        self.address = address

    def get_author_info(self) -> List[str]:
        return self.authors

    def get_conference_info(self) -> dict:
        info = {}
        if self.conference_name:
            info['name'] = self.conference_name
        if self.address:
            info['address'] = self.address
        if self.month:
            info['month'] = self.month
        if self.year:
            info['year'] = self.year
        return info

    def get_paper_info(self) -> dict:
        info = {'title': self.title}
        if self.abstract:
            info['abstract'] = self.abstract
        if self.url:
            info['url'] = self.url
        if self.doi:
            info['doi'] = self.doi
        if self.pages:
            info['pages'] = self.pages
        if self.language:
            info['language'] = self.language
        if self.isbn:
            info['isbn'] = self.isbn
        return info


def read_xml_file():
    xml_data = []

    # create paper obj
    paper = Paper()
    paper.add_info(title='An Analysis of Annotated Corpora for Emotion Classification in Text',
                   authors=['Roman Klinger', 'Laura-Ana-Maria Bostan'],
                   conference_name='Proceedings of the 27th International Conference on Computational Linguistics',
                   address='Santa Fe, New Mexico, USA')
    xml_data.append(paper)

    paper = Paper()
    paper.add_info(title='Lost in Back-Translation: Emotion Preservation in Neural Machine Translation',
                   authors=['Enrica Troiano', 'Roman Klinger', 'Sebastian Padó'],
                   conference_name='Proceedings of the 28th International Conference on Computational Linguistics',
                   address='Barcelona, Spain (Online)')
    xml_data.append(paper)
    return xml_data


def insert_to_authors(author: str) -> int:
    sql = "INSERT OR IGNORE INTO authors (name) VALUES (?)"

    # insert into db
    cursor.execute(sql, (author,))
    return cursor.lastrowid


def insert_to_conferences(conference_info: dict):
    fields = []
    info = ()

    for key, value in conference_info.items():
        fields.append(key)
        info += (value,)

    values = ['?'] * len(info)
    sql = 'INSERT OR IGNORE INTO conferences (' + ','.join(fields) + ') VALUES (' + ','.join(values) + ')'
    cursor.execute(sql, info)
    return cursor.lastrowid


def insert_to_papers(paper_info: dict, conference_id: int):
    fields = ['conference_id']
    info = (conference_id,)

    for key, value in paper_info.items():
        fields.append(key)
        info += (value,)

    values = ['?'] * len(info)
    sql = 'INSERT OR IGNORE INTO papers (' + ','.join(fields) + ') VALUES (' + ','.join(values) + ')'
    cursor.execute(sql, info)
    return cursor.lastrowid


def insert_to_authors_papers(author_id: int, paper_id: int):
    sql = """INSERT INTO author_paper (author_id, paper_id) VALUES (?, ?)"""
    cursor.execute(sql, (author_id, paper_id))


def create_tables():
    authors_sql = """CREATE TABLE IF NOT EXISTS authors ( id INTEGER PRIMARY KEY,
                                                        name TEXT NOT NULL UNIQUE )"""

    conferences_sql = """CREATE TABLE IF NOT EXISTS conferences ( id INTEGER PRIMARY KEY,
                                                    name TEXT NOT NULL UNIQUE,
                                                    address TEXT,
                                                    month INTEGER,
                                                    year TEXT )"""

    papers_sql = """CREATE TABLE IF NOT EXISTS papers ( id INTEGER PRIMARY KEY,
                                                        title TEXT NOT NULL UNIQUE,
                                                        conference_id INTEGER NOT NULL,
                                                        abstract TEXT,  
                                                        url TEXT, 
                                                        doi TEXT, 
                                                        pages TEXT, 
                                                        language TEXT, 
                                                        ISBN TEXT,
                                                        FOREIGN KEY (conference_id) REFERENCES conferences (id) )"""

    authors_papers_sql = """CREATE TABLE IF NOT EXISTS author_paper ( author_id INTEGER NOT NULL,
                                                                    paper_id INTEGER NOT NULL,
                                                                    FOREIGN KEY (author_id) REFERENCES authors (id),
                                                                    FOREIGN KEY (paper_id) REFERENCES papers (id) )"""
    cursor.execute(authors_sql)
    cursor.execute(conferences_sql)
    cursor.execute(papers_sql)
    cursor.execute(authors_papers_sql)
    connection.commit()


def insert_data_to_tables():
    # make sure to check conference and author if already exists before inserting

    for data_point in data:
        # insert conference
        conference = data_point.get_conference_info()
        if conference['name'] not in conference2id:
            conference_id = insert_to_conferences(conference_info=conference)
            conference2id[conference['name']] = conference_id
            id2conference[conference_id] = conference['name']
        else:
            conference_id = conference2id[conference['name']]

        # insert paper
        paper = data_point.get_paper_info()
        paper_id = insert_to_papers(paper_info=paper, conference_id=conference_id)
        paper2id[paper['title']] = paper_id
        id2paper[paper_id] = paper['title']

        # insert authors
        authors = data_point.get_author_info()  # as list of authors
        for author in authors:
            if author not in author2id:
                author_id = insert_to_authors(author=author)
                author2id[author] = author_id
                id2author[author_id] = author
            else:
                author_id = author2id[author]

            # insert to author-paper table
            insert_to_authors_papers(author_id=author_id, paper_id=paper_id)
        connection.commit()  # commit the change


if __name__ == "__main__":
    # from an XML file, create an SQL database
    db_name = 'acl_sql.db'
    connection = sqlite3.connect(os.path.join(os.getcwd(), db_name))  # establish a connection
    cursor = connection.cursor()  # create the cursor object

    data = read_xml_file()  # read data

    author2id = {}
    id2author = {}
    conference2id = {}
    id2conference = {}
    paper2id = {}
    id2paper = {}

    create_tables()  # create tables in the database
    insert_data_to_tables()
