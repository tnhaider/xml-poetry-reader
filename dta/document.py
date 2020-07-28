#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from lxml import etree
from inout.dta.poem import Poem
from inout.utils.helper import *


class Document(object):
    def __init__(self, teipath):
        self.teipath = teipath
        self.author = 'N.A.'
        self.year = 'N.A.'
        self.birthyear = 'N.A.'
        self.deathyear = 'N.A.'
        self.header = 'N.A.'
        self.genre = 'N.A.'
        self.period = 'N.A.'
        self.bibl = 'N.A.'
        self.urn = 'N.A.'
        self.poems = []
        self.rhyme_pairs = []

        self.xmlinfo = """<?xml version = "1.0" encoding = "UTF-8"? > \n
        <?oxygen RNGSchema = "http://www.deutschestextarchiv.de/basisformat.rng" type = "xml"? > \n
        <TEI xmlns = "http://www.tei-c.org/ns/1.0" > \n """

    def read(self):
        if len(self.teipath) > 0:
            self.afile = open(self.teipath, 'r')
        else:
            return "TEI path not set"

        print ("PARSING", str(self.teipath))
        print ("Finding header")
        self.find_tei_header()
        print ("Find metadata, author, year, etc")
        self.find_metadata()
        print ("Find poems")
        self.find_poems()
        print ("Got " + str(len(self.get_poems())) + " poems")
        print ()

    def get_amountof_poems(self):
        return len(self.poems)

    def find_metadata(self):
        if len(self.teipath) > 0:
            self.afile = open(self.teipath, 'rb')
        else:
            return "TEI path not set"

        surname = ''
        forename = ''

        for event, element in etree.iterparse(self.afile, events=('start',), remove_comments=True):
            elem = element.tag.split('}')[1]
            if elem == 'author':
                for name in list(element):
                    if name.tag.split('}')[1] == 'persName':
                        for child in list(name):
                            if child.tag.split('}')[1] == 'surname':
                                surname = child.text
                            if child.tag.split('}')[1] == 'forename':
                                forename = child.text
                        try:
                            self.author = surname + ", " + forename
                        except TypeError:
                            if surname == None:
                                self.author = forename
                            elif forename == None:
                                self.author = surname
            elif elem == 'idno':
                if element.get('type') == "URN":
                    self.urn = element.text
            elif elem == 'bibl':
                if element.get('type') == "M":
                    self.bibl = element.text
            elif elem == 'date':
                if element.get('type') == "publication":
                    self.year = element.text
            elif elem == 'birth':
                for name in list(element):
                    if name.tag.split('}')[1] == 'date':
                        self.birthyear = name.text
                        #for child in list(name):
                        #    if child.tag.split('}')[1] == 'surname':
                        #        surname = child.text
                        #    if child.tag.split('}')[1] == 'forename':
                        #        forename = child.text
            elif elem == 'classCode':
                if element.get('scheme').endswith('dwds1sub'):
                    self.genre = element.text 
                if element.get('scheme').endswith('period'):
                    self.period = element.text
        print('Author: ', self.author)
        print('Year: ', self.year)
        print('Birth: ', self.birthyear)
        print('Death: ', self.deathyear)
        print('Genre: ', self.genre)
        print('Period: ', self.period)
                

    def find_poems(self):
        if len(self.teipath) > 0:
            self.afile = open(self.teipath, 'rb')
        else:
            return "TEI path not set"

        lastdiv = etree.Element('root')
        for event, element in etree.iterparse(self.afile, events=('start',), remove_comments=True):
            try:
                elem = element.tag.split('}')[1]
                elem = elem.strip()
            except IndexError:
                print ("MAJOR POEM PARSING ERROR!!!")
                print (elem)
                print (element)
                print 
                continue

            if elem == 'div':
                lastdiv = element
            if elem == 'lg' and element.get('type') == 'poem':
                #poem = Poem(element, self.header, self.author, self.birthyear); poem.find_title()
                        #poem = Poem(element, self.header, self.author, self.year, title=title)
                #if title == None or title == '' or title == ' ':
                #            head_e = child.find(".//{*}head")
                #            p_e = child.find(".//{*}p")
                #            try:
                                #title = head_e.text
                #                title = ''.join(head_e.itertext()).strip()
                #                title = title + ''.join(p_e.itertext()).strip()
                                #print('TITLE: ', title)
                #            except AttributeError:
                                #print('Broken Title')
                #                pass

               poem = Poem(lastdiv, element, self.header, self.author, self.year, self.genre, self.period, self.bibl, self.urn)
               #if len(self.period) != 'N.A.':
               #    poem.set_period(self.period)
               self.poems.append(poem)

    def find_text(self):
        if len(self.teipath) > 0:
            self.afile = open(self.teipath, 'rb')
        else:
            return "TEI path not set"
        for event, element in etree.iterparse(self.afile, events=('start',)):
            try:
                elem = element.tag.split('}')[1]
                elem = elem.strip()
            except IndexError:
                print ("MAJOR POEM PARSING ERROR!!!")
                print (elem)
                print (element)
                print 
                continue
            if elem == 'text':
                txt = strip_text_from_xml(element)
        return txt
    
    def get_graphem_phonem_dict(self, file_path):
        char_tokens = {} # c_id:string
        trs_tokens = {} # c_id:phonemes
        char_phon = {} # grapheme_str:[phoneme_strings]
        if len(file_path) > 0:
            afile = open(file_path, 'rb')
        else:
            return "TEI path not set"
        for event, element in etree.iterparse(afile, events=('start',)):
            try:
                elem = element.tag.split('}')[1]
                elem = elem.strip()
                #print(elem)
            except IndexError:
                print ("MAJOR POEM PARSING ERROR!!!")
                print (elem)
                print (element)
                print 
                continue
            if elem == 'token':
                c_id = element.get('ID')
                char_string = element.text
                char_tokens[c_id] = char_string 
            if elem == 'trs':
                p_id = element.get('tokenIDs')
                phon_string = element.text 
                trs_tokens[p_id] = phon_string
        for id, token in char_tokens.items():
            try:
                token = str(token.lower())
                char_phon.setdefault(token, []).append(trs_tokens[id])
            except (KeyError, AttributeError) as e:
                continue
        return char_phon
    
    def find_tcf_trs_tokens(self):
        tokens = []
        if len(self.teipath) > 0:
            self.afile = open(self.teipath, 'rb')
        else:
            return "TEI path not set"
        for event, element in etree.iterparse(self.afile, events=('start',)):
            try:
                elem = element.tag.split('}')[1]
                elem = elem.strip()
                #print(elem)
            except IndexError:
                print ("MAJOR POEM PARSING ERROR!!!")
                print (elem)
                print (element)
                print 
                continue
            if elem == 'trs':
                txt = element.text 
                #print(txt)
                #txt = strip_text_from_xml(element)
                tokens.append(txt)
        return tokens 
    
    def find_tcf_char_tokens(self):
        tokens = []
        if len(self.teipath) > 0:
            self.afile = open(self.teipath, 'rb')
        else:
            return "TEI path not set"
        for event, element in etree.iterparse(self.afile, events=('start',)):
            try:
                elem = element.tag.split('}')[1]
                elem = elem.strip()
                #print(elem)
            except IndexError:
                print ("MAJOR POEM PARSING ERROR!!!")
                print (elem)
                print (element)
                print 
                continue
            if elem == 'token':
                txt = element.text 
                #print(txt)
                #txt = strip_text_from_xml(element)
                tokens.append(txt)
        return tokens 
    
    def find_tcf_sentences(self):
        tokens = {}
        sentences = {}
        if len(self.teipath) > 0:
            self.afile = open(self.teipath, 'rb')
        else:
            return "TEI path not set"
        for event, element in etree.iterparse(self.afile, events=('start',)):
            try:
                elem = element.tag.split('}')[1]
                elem = elem.strip()
                #print(elem)
            except IndexError:
                print ("MAJOR POEM PARSING ERROR!!!")
                print (elem)
                print (element)
                print 
                continue
            if elem == 'token':
                i = element.get('ID')
                tokens[i] = element.text
            if elem == 'sentence':
                i = element.get('ID')
                tids = element.get('tokenIDs').split()
                sentences[i] = tids
        return tokens, sentences 


    def find_tei_header(self):
        if len(self.teipath) > 0:
            self.afile = open(self.teipath, 'rb')
        else:
            return "TEI path not set"

        for event, element in etree.iterparse(self.afile, events=('start',)):
            elem = element.tag.split('}')[1]
            if elem == 'teiHeader':
                self.header = element

    def get_author(self):
        return self.author

    def get_year(self):
        return self.year

    def get_birth_year(self):
        return self.birthyear

    def get_death_year(self):
        return self.deathyear

    def get_header(self):
        return self.header

    def get_poems(self):
        return self.poems

    def get_path(self):
        return self.teipath
    
    def get_genre(self):
        return self.genre

if __name__ == '__main__':
    d = Document(sys.argv[1])
    d.get_graphem_phonem_dict(d.get_path())
