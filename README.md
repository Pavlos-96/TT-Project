# Text Technology Project WS2021
# ACL Anthology

## XML database

.xml file is created from the full BibTeX anthology.bib found [here](https://www.aclweb.org/anthology/anthology.bib.gz). It can be validated against the anthology.xsd file in the repository. 

## SQL Queries on *acl_sql.db*

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

