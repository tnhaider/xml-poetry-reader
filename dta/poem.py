#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re, string
import pyphen
#from textblob_de import TextBlobDE as tb
from inout.dta.stanza import Stanza
from inout.utils.helper import *



class Poem(object):
    """
    <div n="1">
        <lg type="poem">
        <head>RONDEL</head><lb/>
            <lg n="1" type="stanza" rhyme="abbba">
                <l>Verflossen ist das Gold der Tage,</l><lb/>
                <l>Des Abends braun und blaue Farben:</l><lb/>
                <l>Des Hirten sanfte Flöten starben</l><lb/>
                <l>Des Abends blau und braune Farben</l><lb/>
                <l>Verflossen ist das Gold der Tage.</l><lb/>
            </lg>
        </lg>
    </div>
    """

    def __init__(self, divelement, linegroupelement, teiheader, author, year, genre, period, booktitle, urn):
        self.xmlinfo = ("<?xml version = \"1.0\" encoding = \"UTF-8\"?>\n"
                        "<?xml-model href=\"Schema/basisformat_lyrik.rng\" type=\"application/xml\" schematypens=\"http://relaxng.org/ns/structure/1.0\"?>")
        self.lgelement = linegroupelement
        self.divelement = divelement
        self.urn = urn
        self.tei_header = teiheader
        self.title = 'N.A.'
        self.author = author
        self.year = year
        self.period = period
        self.genre = genre
        self.bibl = booktitle
        self.stanza_lens = []
        self.stanzas = []
        self.find_stanzas()
        self.rhyme_pairs = []
        self.non_rhyme_pairs = []

        self.find_title()
        #self.find_stanzas()


    def find_stanzas(self):
        lgcounter = 0
        for child in list(self.lgelement): # iterating over lg type='poem'
            
            childtag = child.tag.split('}')[1]
            if childtag == 'lg': # finding stanzas
                #sublgs = [ctag.tag.split('}')[1] for ctag in list(child)].count('lg') # checking if stanza is actually stanzagroup
                ctags = [str(ctag.tag) for ctag in list(child)]
                #print(ctags)
                sublgs = [ctag.split('}')[1] for ctag in ctags].count('lg')
                if sublgs > 1:
                    # child is group
                    # child.set("type", "group")
                    for childchild in list(child):
                        if childchild.tag.split('}')[1] == 'lg':
                            #if childchild.attrib.get('type') == 'stanza':
                            stanza = Stanza(childchild)
                            #print ("CHILDCHILD")
                            self.stanzas.append(stanza)

                else: # default case
                    #if child.attrib.get('type') == 'stanza':
                    stanza = Stanza(child)
                    #print ("CHILD")
                    self.stanzas.append(stanza)

        if len(self.stanzas) == 0: # if it's a lonely stanza
            stanza = Stanza(self.lgelement)
            #print ("NOCHILD")
            self.stanzas.append(stanza)


    def find_rhyme_pairs(self):
        rhyme_pairs = []
        for stanza in self.get_stanzas():
            for rhyme_pair in stanza.get_rhyme_pairs():
                print(rhyme_pair)
                rhyme_pairs.append(rhyme_pair)
        #print (rhyme_pairs)
        return rhyme_pairs
    
    def find_non_rhyme_pairs(self):
        rhyme_pairs = []
        for stanza in self.get_stanzas():
            for non_rhyme_pair in stanza.get_non_rhyme_pairs():
                non_rhyme_pairs.append(non_rhyme_pair)
        return non_rhyme_pairs

    def find_title(self):
        title = 'N.A.'
        #print("Looking for the title")
        #print(etree.tostring(self.divelement, pretty_print=False))
        new_tree = etree.ElementTree(self.lgelement)
        head_e = new_tree.find(".//{*}head")
        if not head_e == None:
            title = ' '.join(head_e.itertext())
            #return
        else:
            new_tree = etree.ElementTree(self.divelement)
            head_e = new_tree.find(".//{*}head")
            p_e = new_tree.find("p")
            #p_e = new_tree.find(".//{*}p")
            if not head_e == None:
                t = ' '.join(head_e.itertext())
                if not p_e == None:
                    t = t + ' '.join(p_e.itertext())
                title = t
                #return
            else:
                title = 'N.A.'
        title = title.strip()
        title = ' \n '.join(title.split('\n'))
        self.title = title
        return title
        

    def set_period(self, period):
        self.period = period

    def get_period(self):
        return self.period

    def get_booktitle(self):
        return self.bibl

    def get_title(self):
        return self.title

    def get_genre(self):
        return self.genre

    def get_urn(self):
        return self.urn

    def get_lg_element(self):
        return self.lgelement

    def get_xmlinfo(self):
        return self.xmlinfo

    def get_tei_header(self):
        return self.tei_header

    def get_stanza_sizes(self):
        return self.stanzas

    def get_stanzas(self):
        return self.stanzas

    def get_author(self):
        return self.author

    def get_teipath(self):
        return self.teipath

    def get_year(self):
        return self.year
    
    def get_lines(self):
        lines = []
        for stanza in self.get_stanzas():
            for line in stanza.get_lines():
                lines.append(line)
        return lines 

    def get_rhyme_pairs(self):
        return self.rhyme_pairs
    
    def get_non_rhyme_pairs(self):
        return self.non_rhyme_pairs
