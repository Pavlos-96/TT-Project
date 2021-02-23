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

## SQL 

### Create *acl_sql.db* database

Make sure to create or download the XML files `anthology.xml`
and `anthology.xsd` and have them in your working directory.

On your terminal, type:

```
python3 sql.py
```

It will create the sql database called `acl_sql.db` and
fill in data from xml file in the corresponding tables/columns.

See the file `SQL.png` for table structure. Except for the *id*,
all other column format is text.

### Queries on *acl_sql.db*

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

