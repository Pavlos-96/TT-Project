from neo4j import GraphDatabase
from sql import read_xml_file
import random

class Database:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def update_graph(self, function, args):
        with self.driver.session() as session:
            node = session.write_transaction(function, *args)

    @staticmethod
    def _create_node(tx, node_type, name):
        result = tx.run(f"MERGE (a:{node_type} {{name:'{name}'}}) ")
        return result.single()

    @staticmethod
    def _create_relationship(tx, name_a, name_b, rel):
        result = tx.run(f"MATCH (a{{name:'{name_a}'}}) "
                        f"MATCH (b{{name:'{name_b}'}}) "
                        f"CREATE (a)-[rel:{rel}]->(b) ")
        return result.single()

    @staticmethod
    def _create_relationships(tx, name_a, name_b, rel1, rel2):
        result = tx.run(f"MATCH (a{{name:'{name_a}'}}) "
                        f"MATCH (b{{name:'{name_b}'}}) "
                        f"CREATE (a)-[rel1:{rel1}]->(b) "
                        f"CREATE (b)-[rel2:{rel2}]->(a) ")
        return result.single()

    @staticmethod
    def _delete_node(tx, name):
        result = tx.run(f"MATCH (a{{name:'{name}'}}) "
                        "DETACH DELETE a ")
        return None

    @staticmethod
    def _set_property(tx, name, prop_name, prop_value):
        result = tx.run(f"MATCH (a{{name:'{name}'}}) "
                        f"SET a. {prop_name} = '{prop_value}' ")
        return result.single()

    @staticmethod
    def _delete_db(tx):
        result = tx.run(f"MATCH (a) "
                        "DETACH DELETE a ")
        return None


class Paper:
    def __init__(self,title, url, doi, pages, language,
                 isbn, publisher, conference_name, address, month,
                 year, journal, volume, number, authors):
        self.title = title
        self.url = url
        self.doi = doi
        self.pages = pages
        self.language = language
        self.isbn = isbn
        self.publisher = publisher

        self.conference_name = conference_name
        self.address = address
        self.month = month
        self.year = year

        self.journal = journal
        self.volume = volume
        self.number = number
        self.authors = authors  # as list of author names


def import_paper(paper, db):
    try:
        if paper.conference_name:
            db.update_graph(db._create_node, ["Conference", "Conference"])
            db.update_graph(db._create_node, ["Paper", paper.title])
            db.update_graph(db._create_relationship, [paper.title, "Conference", "IS_IN"])
            db.update_graph(db._create_node, ["Conference", paper.conference_name])
            db.update_graph(db._create_relationship, [paper.conference_name, "Conference", "IS"])
            db.update_graph(db._create_relationship, [paper.title, paper.conference_name, "APPEARED_IN"])
            for author in paper.authors:
                db.update_graph(db._create_node, ["Author", author])
                db.update_graph(db._create_relationship, [author, paper.title, "EDITED"])
                db.update_graph(db._create_relationship, [author, paper.conference_name, "ATTENDED"])
            if paper.year:
                db.update_graph(db._create_node, ["Year", paper.year])
                db.update_graph(db._create_relationship, [paper.title, paper.year, "APPEARED_IN"])
            if paper.month:
                db.update_graph(db._create_node, ["Month", paper.month])
                db.update_graph(db._create_relationship, [paper.title, paper.month, "APPEARED_IN"])
            if paper.year and paper.month:
                db.update_graph(db._create_relationship, [paper.month, paper.year, "IN"])
            db.update_graph(db._create_node, ["Publisher", paper.publisher])
            db.update_graph(db._create_relationship, [paper.publisher, paper.title, "PUBLISHED"])
        elif paper.journal:
            db.update_graph(db._create_node, ["Journal", "Journal"])
            db.update_graph(db._create_node, ["Paper", paper.title])
            db.update_graph(db._create_relationship, [paper.title, "Journal", "IS_IN"])
            db.update_graph(db._create_node, ["Journal", paper.journal])
            db.update_graph(db._create_relationship, [paper.journal, "Journal", "IS"])
            db.update_graph(db._create_relationship, [paper.title, paper.journal, "APPEARED_IN"])
            for author in paper.authors:
                db.update_graph(db._create_node, ["Author", author])
                db.update_graph(db._create_relationship, [author, paper.title, "EDITED"])
                db.update_graph(db._create_relationship, [author, paper.journal, "WROTE_ARTICLE_IN"])
            if paper.year:
                db.update_graph(db._create_node, ["Year", paper.year])
                db.update_graph(db._create_relationship, [paper.title, paper.year, "APPEARED_IN"])
            if paper.month:
                db.update_graph(db._create_node, ["Month", paper.month])
                db.update_graph(db._create_relationship, [paper.title, paper.month, "APPEARED_IN"])
            if paper.year and paper.month:
                db.update_graph(db._create_relationship, [paper.month, paper.year, "IN"])
            if paper.number:
                db.update_graph(db._set_property, [paper.title, "Number", paper.number])
            if paper.volume:
                db.update_graph(db._set_property, [paper.title, "Volume", paper.volume])

        if paper.address:
            db.update_graph(db._set_property, [paper.title, "Address", paper.address])
        if paper.url:
            db.update_graph(db._set_property, [paper.title, "URL", paper.url])
        if paper.doi:
            db.update_graph(db._set_property, [paper.title, "DOI", paper.doi])
        if paper.language:
            db.update_graph(db._set_property, [paper.title, "Language", paper.language])
        if paper.isbn:
            db.update_graph(db._set_property, [paper.title, "ISBN", paper.isbn])
    except:
        pass




if __name__ == "__main__":
    db = Database("bolt://localhost:7687", "neo4j", "password")

    db.update_graph(db._delete_db, [])
    '''journal = Paper("Title1", None, None, None, None,
     None, None, None, None, "Month1",
     "Year1", "J_Title", "Volume", "Number", ["author1", "author2"])
    article = Paper("Title2", None, None, None, None,
     None, "Publisher", "C_Title", None, "Month1",
     "Year2", None, None, None, ["author3", "author2"])
    import_paper(article, db)
    import_paper(journal, db)'''
    xml = read_xml_file()
    random.shuffle(xml)
    #from pprint import pprint
    i = 0
    for paper in xml:
        i+=1
        #pprint(vars(paper))
        import_paper(paper, db)
        if i % 1000 == 0:
            print(str(i) + 'of' + str(len(xml)))
    db.close()