import os
import sys
import string
import sqlite3
import xmlschema
from xml.etree import ElementTree
from typing import List


class Paper:
    def __init__(self):
        self.id = None
        self.title = None
        self.authors = []  # as list of author names
        self.url = None
        self.doi = None
        self.pages = None
        self.language = None
        self.isbn = None
        self.publisher = None

        self.conference_name = None
        self.address = None
        self.month = None
        self.year = None

        self.journal = None
        self.volume = None
        self.number = None

    def get_author_info(self) -> List[str]:
        return self.authors

    def where_published(self):
        if self.conference_name:
            return 'conference'
        elif self.journal:
            return 'journal'
        return None

    def get_conference_info(self) -> dict:
        info = {}
        if self.conference_name:
            info['conference'] = self.conference_name
        if self.address:
            info['address'] = self.address
        if self.month:
            info['month'] = self.month
        if self.year:
            info['year'] = self.year
        return info

    def get_journal_info(self) -> dict:
        info = {}
        if self.journal:
            info['journal'] = self.journal
        if self.volume:
            info['volume'] = self.volume
        if self.number:
            info['number'] = self.number
        return info

    def get_paper_info(self) -> dict:
        info = {'id': self.id, 'title': self.title}
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


def read_xml_file() -> List[Paper]:
    """
    Read  the XML file. Create a Paper object for each paper

    :return: a list of Paper objects
    """

    if os.path.exists(os.path.join(os.getcwd(), 'anthology.xsd')) and \
            os.path.exists(os.path.join(os.getcwd(), 'anthology.xml')):
        xs = xmlschema.XMLSchema(os.path.join(os.getcwd(), 'anthology.xsd'))
        xml = ElementTree.parse(os.path.join(os.getcwd(), 'anthology.xml'))
        assert xs.is_valid(xml)  # make sure the xml is valid
    else:
        print('Make sure to have both XML file and its schema in your current working directory.')
        sys.exit()

    xml_data = xs.to_dict(xml)
    paper_collection = []

    # loop through two big entries, inproceedings and articles
    for entry_type in ['inproceedings_entry', 'article_entry']:
        entries = xml_data[entry_type]

        # the 2nd loop goes over each paper (or entry)
        for entry in entries:
            if entry['title']:  # if the title does not empty --> exists a paper
                paper = Paper()  # create paper obj

                for field, value in entry.items():
                    if field.replace('@', '') == 'id':
                        paper.id = value
                    elif field.replace('@', '') == 'year':
                        paper.year = value
                    elif field.replace('@', '') == 'month':
                        paper.month = value
                    elif field.replace('@', '') == 'publisher':
                        paper.publisher = value
                    elif field.replace('@', '') == 'booktitle':
                        value = value.replace('{', '')
                        value = value.replace('}', '')
                        paper.conference_name = value
                    elif field.replace('@', '') == 'address':
                        paper.address = value

                    elif field.replace('@', '') == 'authors':
                        if type(value) == dict:
                            value = value['author']
                        elif type(value) == list:
                            value = value[0]['author']

                        for name in value:  # string as last_name, first_name
                            name = name.split(', ')  # turn string into list
                            name.reverse()
                            name = ' '.join(name)
                            name = name.translate(str.maketrans('', '', string.punctuation))  # remove punc in name
                            paper.authors.append(name)  # append string as 'first_name last_name'

                    elif field.replace('@', '') == 'journal':
                        for journal_key, journal_val in value.items():
                            if journal_key.replace('@', '') == 'volume':
                                paper.volume = journal_val
                            elif journal_key.replace('@', '') == 'number':
                                paper.number = journal_val
                            elif journal_key.replace('@', '') == '$':
                                journal_val = journal_val.replace('{', '')
                                journal_val = journal_val.replace('}', '')
                                paper.journal = journal_val

                    elif field.replace('@', '') == 'title':
                        for title_key, title_val in value.items():
                            if title_key.replace('@', '') == 'doi':
                                paper.doi = title_val
                            elif title_key.replace('@', '') == 'isbn':
                                paper.isbn = title_val
                            elif title_key.replace('@', '') == 'language':
                                paper.language = title_val
                            elif title_key.replace('@', '') == 'pages':
                                paper.pages = title_val
                            elif title_key.replace('@', '') == 'url':
                                paper.url = title_val
                            elif title_key.replace('@', '') == '$':
                                title_val = title_val.replace('{', '')
                                title_val = title_val.replace('}', '')
                                paper.title = title_val

                paper_collection.append(paper)
    return paper_collection


def insert_to_authors(author: str) -> int:
    """
    Insert author to the authors table
    :param author: name of author
    :return: author id
    """
    sql = "INSERT OR IGNORE INTO authors (author) VALUES (?)"
    cursor.execute(sql, (author,))  # insert into db
    return cursor.lastrowid  # return author id


def insert_to_conferences(conference_info: dict) -> int:
    """
    Insert data into conferences table
    :param conference_info: a dict storing info for conferences table
    :return: the conference id
    """

    fields = []  # list of column names with values to insert into the table
    info = ()  # a set of corresponding values of the fields

    for key, value in conference_info.items():
        fields.append(key)
        info += (value,)

    values = ['?'] * len(info)  # placeholders in the sql string
    sql = 'INSERT OR IGNORE INTO conferences (' + ','.join(fields) + ') VALUES (' + ','.join(values) + ')'
    cursor.execute(sql, info)  # finally add values into the table
    return cursor.lastrowid


def insert_to_journals(journal_info: dict) -> int:
    """
    Insert data into journals table
    :param journal_info: a dict storing info for journals table
    :return: the journal id
    """
    # prepare the column names and corresponding values
    fields = []
    info = ()

    for key, value in journal_info.items():
        fields.append(key)
        info += (value,)

    values = ['?'] * len(info)  # placeholders in the sql string
    sql = 'INSERT OR IGNORE INTO journals (' + ','.join(fields) + ') VALUES (' + ','.join(values) + ')'
    cursor.execute(sql, info)  # add data into the table
    return cursor.lastrowid


def insert_to_papers(paper_info: dict, conference_id=None, journal_id=None, where=None) -> str:
    """
    Insert data into papers table
    :param paper_info: a dict storing info for papers table
    :param conference_id: if exists, id of conference the paper appears in
    :param journal_id: if exists, id of journal the paper appears in
    :param where: if exists, conference or journal the paper appear in
    :return: the paper id (in string)
    """
    # prepare data
    fields = []
    info = ()

    # a paper can only appear either in a conference or a journal, if any
    if where == 'conference':
        fields.append('conference_id')
        info += (conference_id,)
    elif where == 'journal':
        fields.append('journal_id')
        info += (journal_id,)

    for key, value in paper_info.items():
        fields.append(key)
        info += (value,)

    values = ['?'] * len(info)
    sql = 'INSERT OR IGNORE INTO papers (' + ','.join(fields) + ') VALUES (' + ','.join(values) + ')'
    cursor.execute(sql, info)
    return paper_info['id']


def insert_to_authors_papers(author_id: int, paper_id: str) -> None:
    """
    Insert data into authors_papers table
    :param author_id: author id
    :param paper_id: paper id
    :return: None
    """
    sql = """INSERT INTO author_paper (author_id, paper_id) VALUES (?, ?)"""
    cursor.execute(sql, (author_id, paper_id))  # add data to table


def create_tables() -> None:
    """
    Create tables in the SQL database
    :return: None
    """
    authors_sql = """CREATE TABLE IF NOT EXISTS authors ( id INTEGER PRIMARY KEY,
                                                        author TEXT NOT NULL UNIQUE )"""

    conferences_sql = """CREATE TABLE IF NOT EXISTS conferences ( id INTEGER PRIMARY KEY,
                                                    conference TEXT NOT NULL UNIQUE,
                                                    address TEXT,
                                                    month TEXT,
                                                    year TEXT )"""

    journal_sql = """CREATE TABLE IF NOT EXISTS journals ( id INTEGER PRIMARY KEY,
                                                        journal TEXT NOT NULL UNIQUE,
                                                        number TEXT,
                                                        volume TEXT)"""

    papers_sql = """CREATE TABLE IF NOT EXISTS papers ( id TEXT PRIMARY KEY,
                                                        title TEXT NOT NULL UNIQUE,
                                                        conference_id INTEGER,
                                                        url TEXT, 
                                                        doi TEXT, 
                                                        pages TEXT, 
                                                        language TEXT, 
                                                        ISBN TEXT,
                                                        journal_id INTEGER,
                                                        volume TEXT,
                                                        number TEXT,
                                                        FOREIGN KEY (conference_id) REFERENCES conferences (id),
                                                        FOREIGN KEY (journal_id) REFERENCES journals (id) )"""

    authors_papers_sql = """CREATE TABLE IF NOT EXISTS author_paper ( author_id INTEGER NOT NULL,
                                                                    paper_id TEXT NOT NULL,
                                                                    FOREIGN KEY (author_id) REFERENCES authors (id),
                                                                    FOREIGN KEY (paper_id) REFERENCES papers (id) )"""
    cursor.execute(authors_sql)
    cursor.execute(conferences_sql)
    cursor.execute(journal_sql)
    cursor.execute(papers_sql)
    cursor.execute(authors_papers_sql)
    connection.commit()  # commit changes


def insert_data_to_tables() -> None:
    """
    Insert data to all tables in the SQL database
    :return: None
    """

    # conference, journal, and author might already exist before inserting a new paper
    # because a conference and a journal can contain more than one paper
    # and a paper can have more than one author

    # data = list of all Paper objects read from XML file
    for data_point in data:

        # each data point is a Paper object
        # see Paper obj for its structure
        where_published = data_point.where_published()
        conference = data_point.get_conference_info()  # as dict
        journal = data_point.get_journal_info()  # as dict
        paper = data_point.get_paper_info()  # as dict
        authors = data_point.get_author_info()  # as list of authors

        if where_published == 'conference':
            # insert conference
            conference = data_point.get_conference_info()
            if conference['conference'] not in conference2id:  # check if exists
                conference_id = insert_to_conferences(conference_info=conference)
                conference2id[conference['conference']] = conference_id
                id2conference[conference_id] = conference['conference']

        elif where_published == 'journal':
            # insert into journal
            if journal['journal'] not in journal2id:  # check if exists
                journal_id = insert_to_journals(journal_info=journal)
                journal2id[journal['journal']] = journal_id
                id2journal[journal_id] = journal['journal']

        # insert paper
        if where_published == 'conference':
            conference_id = conference2id[conference['conference']]
            paper_id = insert_to_papers(paper_info=paper, conference_id=conference_id, where=where_published)
        elif where_published == 'journal':
            journal_id = journal2id[journal['journal']]
            paper_id = insert_to_papers(paper_info=paper, journal_id=journal_id, where=where_published)
        else:
            paper_id = insert_to_papers(paper_info=paper)

        paper2id[paper['title']] = paper_id
        id2paper[paper_id] = paper['title']

        # insert authors
        for author in authors:
            if author not in author2id:  # check if exists
                author_id = insert_to_authors(author=author)
                author2id[author] = author_id
                id2author[author_id] = author
            else:
                author_id = author2id[author]

            # insert to author-paper table
            insert_to_authors_papers(author_id=author_id, paper_id=paper_id)
        connection.commit()  # commit the changes


if __name__ == "__main__":

    # create an SQL database
    db_name = 'acl_sql.db'
    connection = sqlite3.connect(os.path.join(os.getcwd(), db_name))  # establish a connection
    cursor = connection.cursor()  # create the cursor object

    # to track the conference, journal, author, paper
    author2id = {}
    id2author = {}
    conference2id = {}
    id2conference = {}
    journal2id = {}
    id2journal = {}
    paper2id = {}
    id2paper = {}

    print('\nCreate database and tables...')
    create_tables()  # create tables in the SQL database

    print('\nRead the XML file...')
    data = read_xml_file()  # read data from XML file
    print('Number of papers:', len(data))

    print('\nInsert data into the database...')
    insert_data_to_tables()  # insert data into SQL tables
