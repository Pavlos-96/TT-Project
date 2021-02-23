# Text Technology Project WS2021
# ACL Anthology

### Dependencies

To install dependencies for Python, on your terminal, type:

```
pip install -r requirements.txt
```

See corresponding guidelines below on how to run and generate the files for this project.

Please make sure to have the original ACL anthology called `??????????.bib` in your current
working directory to generate first the XML file.


## XML database

.xml file is created from the full BibTeX anthology.bib found [here](https://www.aclweb.org/anthology/anthology.bib.gz). It can be validated against the anthology.xsd file in the repository. 

## SQL database

### Create *acl_sql.db* file

Make sure to create or download the XML files `anthology.xml`
and `anthology.xsd` and have them in your working directory.

On your terminal, type:

```
python3 sql.py
```

It will create the sql database called `acl_sql.db` and
fill in data from xml file in the corresponding tables/columns.

See the file `SQL.png` for table structure. Except for the *id*,
all other columns is in text format. Note that paper id is in text format
as we use the same id from the ACL anthology.

### Queries on *acl_sql.db*

You should, of course, have access to a sql interface such as *psql* on your computer.
Or a [SQL DB browser](https://sqlitebrowser.org/) can be used instead if one is not very familiar
with using SQL on the terminal.

The table that holds m-to-n relationship between authors and papers is called *author_paper*

Query to find a list of papers written by an author, e.g papers written by *Dyer*
```
SELECT author, title, conference, address
FROM papers 
JOIN author_paper ON papers.id = paper_id
JOIN authors ON authors.id = author_id
JOIN conferences ON conferences.id = conference_id
WHERE author LIKE '%dyer%'
```


Query to find a list of papers of a certain topic, e.g. papers about *parsing*
```
SELECT author, title
FROM papers 
JOIN author_paper ON papers.id = paper_id
JOIN authors ON authors.id = author_id
WHERE title LIKE '%parsing%'
```


Query to find a list of papers written by an author in a certain topic, e.g papers written by *Roman* about *emotion*
```
SELECT author, title
FROM papers 
JOIN author_paper ON papers.id = paper_id
JOIN authors ON authors.id = author_id
WHERE title LIKE '%emotion%'
AND author LIKE '%roman%'
```



## Neo4j graph database

### Create the data base
Make sure that Neo4j is installed on your computer.
Open it and add a local DBMS.

### Fill the data base
Make sure to create or download the XML files `anthology.xml`
and `anthology.xsd` and have them in your working directory.

As it could take more than 24 hours to processing all 60675 entries, we applied an early stopping mechanism where only 300 entries are considered which should take no longer than 3 minutes. The number of entries to be considered can still be adjusted by changing the integer in line 220.

To run the code with early stopping open your terminal and type:
```
python3 neo4j.py True
```
To run it without early stopping type:
```
python3 neo4j.py False
```

### Do queries
Look into the details of the data base in your desktop version of Neo4j and click on 'localhost' under 'IP' to open the data base in your browser.
To get an overview of the node types and relationships that exist in the data base you can have a look in our presentation.

Here are some example queries/query templates:

Query to find a paper that was written by '<author_name>' and where the title contains '<word_in_title>' (not that useful when having used early stopping)
```
MATCH (a:Paper)<-[:WROTE]-(b:Author) WHERE a.name CONTAINS '<word_in_title>' AND b.name CONTAINS '<author_name>' RETURN a
```
Query to find ten papers that were published in the year '2010' and where the title contains '<word_in_title>' (not that useful when having used early stopping)
```
MATCH (a:Paper)-[:APPEARED_IN]->(b:Year) WHERE b.name CONTAINS '2010' RETURN a,b LIMIT 10
```
Query to find an author who wrote an article in a journal and in a Conference:
```
MATCH (a:Conference)<-[:APPEARED_IN]-(b:Paper)<-[:WROTE]-(c:Author)-[:WROTE]->(d:Paper)-[:APPEARED_IN]->(e:Journal) RETURN a,b,c,d,e LIMIT 1
```




