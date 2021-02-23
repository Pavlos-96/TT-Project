from pybtex.database.input import bibtex
import xml.etree.ElementTree as ET
import sys
import re

parser = bibtex.Parser()
# anthology has been edited in Notepad++ in order to avoid unicode errors 
# to reproduce, perform search&replace [^\x00-\x7F]+ 
data = parser.parse_file('./anthology_cleaned.bib')

# write dump to file
sys.stdout = open('./anthology.xml', 'a')

# future XML elements as lists
entry_type = []
pages = []
year = []
publisher = []
booktitle = []
address = []
url = []
doi = []
isbn = []
language = []
abbrev = []
month = []

volume = []
journal = []
number = []

# TODO: clean these ones
author = []
editor = []
title = []

#print(data.entries['cl-2020--2'])


# retrieve entry type
for key in data.entries:
    entry_type.append(data.entries.get(key).type)

# retrieve bibtex data and fill lists
for k1, v1 in data.entries.items():
    temp = ''
    temp += k1

    abbrev.append(k1)


    if 'language' in v1.fields:
        language.append(v1.fields['language'])
    else:
        language.append('null')

    if 'isbn' in v1.fields:
        isbn.append(v1.fields['isbn'])
    else:
        isbn.append('null')

    if 'doi' in v1.fields:
        doi.append(v1.fields['doi'])
    else:
        doi.append('null')

    if 'url' in v1.fields:
        url.append(v1.fields['url'])
    else:
        url.append('null')

    if 'address' in v1.fields:
        address.append(v1.fields['address'])
    else:
        address.append('null')

    if 'booktitle' in v1.fields:
        booktitle.append(v1.fields['booktitle'])
    else:
        booktitle.append('null')

    if 'publisher' in v1.fields:
        publisher.append(v1.fields['publisher'])
    else:
        publisher.append('null')

    if 'month' in v1.fields:
        month.append(v1.fields['month'])
    else:
        month.append('null')

    if 'year' in v1.fields:
        year.append(v1.fields['year'])
    else:
        year.append('null')

    if 'title' in v1.fields:
        title.append(v1.fields['title'])
    else:
        title.append('null')

    if 'pages' in v1.fields:
        pages.append(v1.fields['pages'])
    else:
        pages.append('null')

    if 'journal' in v1.fields:
        journal.append(v1.fields['journal'])
    else:
        journal.append('null')

    if 'volume' in v1.fields:
        volume.append(v1.fields['volume'])
    else:
        volume.append('null')

    if 'number' in v1.fields:
        number.append(v1.fields['number'])
    else:
        number.append('null')

    if v1.persons.items():
        for k2, v2 in v1.persons.items():
            temp2 = ''
            temp2 += k2

            if 'editor' in k2:
                entryEditorList = []
                for name in v2:
                    entryEditorList.append(str(name))
                editor.append(entryEditorList)
            else:
                editor.append('null')

            if 'author' in k2:
                entryAuthorList = []
                for name in v2:
                    entryAuthorList.append(str(name))
                author.append(entryAuthorList)
            else:
                author.append('null')
    else:
        editor.append('null')
        author.append('null')

    #print(len(abbrev), len(author))


# clean and unify month values
for i in range(len(month)):
    if month[i] != 'null':
        month[i] = re.sub(r'5', 'may', str(month[i]))
        month[i] = re.sub(r'6', 'jun', str(month[i]))
        month[i] = re.sub(r'7', 'jul', str(month[i]))
        month[i] = re.sub(r'\d+', '', str(month[i]))
        month[i] = re.sub(r' ', '', str(month[i]))
        month[i] = re.sub(r'\W+', '', str(month[i]))
        month[i] = str(month[i][:3].lower())


# header and root node of the .xml file
print('<?xml version="1.0" encoding="UTF-8"?>')
print('<root>')

# create XML tree
for value in range(len(author)):

    if entry_type[value] == 'inproceedings':
        entryElement = ET.Element('inproceedings_entry')
        entryElement.set("id", abbrev[value])
    elif entry_type[value] == 'proceedings':
        entryElement = ET.Element('proceedings_entry')
        entryElement.set("id", abbrev[value])
    elif entry_type[value] == 'article':
        entryElement = ET.Element('article_entry')
        entryElement.set("id", abbrev[value])
    if year[value] != 'null':
        yearElement = ET.SubElement(entryElement, 'year')
        yearElement.text = year[value]
    if month[value] != 'null':
        monthElement = ET.SubElement(entryElement, 'month')
        monthElement.text = month[value]
    if publisher[value] != 'null':
        publisherElement = ET.SubElement(entryElement, 'publisher')
        publisherElement.text = publisher[value]

    if booktitle[value] != 'null':
        booktitleElement = ET.SubElement(entryElement, 'booktitle')
        booktitleElement.text = booktitle[value]

    if address[value] != 'null':
        addressElement = ET.SubElement(entryElement, 'address')
        addressElement.text = address[value]

    if title[value] != 'null':
        titleElement = ET.SubElement(entryElement, 'title')
        titleElement.text = title[value]
    if pages[value] != 'null':
        titleElement.set('pages', pages[value])
    if language[value] != 'null':
        titleElement.set('language', language[value])
    if doi[value] != 'null':
        titleElement.set('doi', doi[value])
    if isbn[value] != 'null':
        titleElement.set('isbn', isbn[value])
    if url[value] != 'null':
        titleElement.set('url', url[value])

    if journal[value] != 'null':
        journalElement = ET.SubElement(entryElement, 'journal')
        journalElement.text = journal[value]
    if volume[value] != 'null':
        journalElement.set('volume', volume[value])
    if number[value] != 'null':
        journalElement.set('number', number[value])

    if author[value] != 'null':
        authorsElement = ET.SubElement(entryElement, 'authors')
        for name in author[value]:
            authorElement = ET.SubElement(authorsElement, 'author')
            authorElement.text = name

    if editor[value] != 'null':
        editorsElement = ET.SubElement(entryElement, 'editors')
        for name in editor[value]:
            editorElement = ET.SubElement(editorsElement, 'editor')
            editorElement.text = name

    ET.dump(entryElement)

print('</root>')
