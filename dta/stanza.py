#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, re, string
import pyphen
from inout.utils.helper import *
#from textblob_de import TextBlobDE as tb

 
class Line(object):
    def __init__(self, line_element):
        self.line_element = line_element
        self.text = ''
        self.meter = ''
        self.rhythm = ''
        self.emo1 = None
        self.emo2 = None
        self.enj = None
        self.enj_k = None
        #self.syllables = []
        
    def get_text(self):
        if self.line_element.text != None:
            txt = self.line_element.text
        else:
            txt = strip_text_from_xml(self.line_element)
        try:
            txt = txt.decode()
        except (UnicodeDecodeError, AttributeError):
            pass
        txt = re.sub('\|', '', txt)
        return txt 

    def get_emotion1(self):
        self.emo1 = self.line_element.get('emo1')
        return self.emo1

    def get_emotion2(self):
        self.emo2 = self.line_element.get('emo2')
        return self.emo2

    def get_enjambement(self):
        self.enj = self.line_element.get('enj')
        return self.enj

    def get_enjambement_kontext(self):
        self.enj_k = self.line_element.get('enj_k')
        return self.enj_k
    
    def get_meter(self):
        self.meter = self.line_element.get('met')
        return self.meter 
    
    def get_rhythm(self):
        self.rhythm = self.line_element.get('rhythm')
        return self.rhythm
    
    def get_syllables(self):
        #tb_line = tb(self.get_text())
        #tokens = tb_line.words
        ##hyphenated = [syll for tokens in syllabify(word).split('-') for syllin tokens] 
        ##hyphenated = [syll for syllabify(word).split('-') in tokens for syll in word]
        hyphenated = []
        for word in tokens:
            for syll in syllabify(word).split('-'):
                hyphenated.append(syll)
        return hyphenated    


class Stanza(object):
    def __init__(self, stanza_element):
        self.stanza_element = stanza_element
        self.rhyme_schema = ''
        self.rhyme_indices = []
        self.non_rhyme_indices = []
        self.line_elements = []
        self.line_objects = []
        #self.lines = self.find_lines()
        #self.find_rhyme_schema()
        #self.end_words = [self.find_end_word(line) for line in self.lines]
        #print (self.end_words)
        #self.rhyme_pairs = self.find_rhyme_pairs(syllab=False)
        #self.non_rhyme_pairs = self.find_non_rhyme_pairs(syllab=False)
        
        #print(self.rhyme_pairs)
        #print(self.non_rhyme_pairs)
        
    def get_line_objects(self):
        lines = []
        self.line_elements = list(self.stanza_element)
        lastline = '-'
        for stanzaelement in self.line_elements:
            line = ' '
            if stanzaelement.tag.split('}')[1] == 'l': #check if line
                line = Line(stanzaelement)
                lines.append(line)
        return lines 
        

    def find_lines(self):
        lines = []
        self.line_elements = list(self.stanza_element)
        lastline = '-'
        for stanzaelement in self.line_elements:
            line = ' '
            if stanzaelement.tag.split('}')[1] == 'l': #check if line
                if stanzaelement.text != None:
                    line = stanzaelement.text
                else:
                    line = strip_text_from_xml(stanzaelement)
                lines.append(line)
        #lines = [line.text for line in self.line_elements if line.tag.split('}')[1] == 'l']
        #print (lines)
        return lines

    def find_rhyme_schema(self, low=False):
        schema = self.stanza_element.attrib.get('rhyme')
        if low == True:
            self.rhyme_schema = self.stanza_element.attrib.get('rhyme').lower()
        else:
            self.rhyme_schema = self.stanza_element.attrib.get('rhyme')
            
    def get_rhyme_schema(self):
        return self.rhyme_schema

    def find_rhyme_pairs(self, syllab=False):
        rhyme_pairs = []
        self.find_rhyme_schema()
        schema = self.get_schema()
        if schema == None:
            schema = 'a'
        else:
            schema = schema[:len(self.lines)]
        rhyme_indices, non_rhyme_indices = self.index_rhyme_schema(schema)
        #print ("RHYME: " + str(rhyme_indices))
        for i, j in rhyme_indices:
            word1 = self.end_words[i]
            word2 = self.end_words[j]
            word1 = remove_punct(word1)
            word2 = remove_punct(word2)
            if syllab == True:
                word1 = syllabify(word1)
                word2 = syllabify(word2)
            rhyme_pairs.append((word1, word2))
        return rhyme_pairs
    
    
    def find_non_rhyme_pairs(self, syllab=False):
        non_rhyme_pairs = []
        self.find_rhyme_schema()
        schema = self.get_schema()
        if schema == None:
            schema = 'a'
        else:
            schema = schema[:len(self.lines)]
        rhyme_indices, non_rhyme_indices = self.index_rhyme_schema(schema)
        
        #print ("NON: " + str(non_rhyme_indices))
        for i, j in non_rhyme_indices:
            word1 = self.end_words[i]
            word2 = self.end_words[j]
            word1 = remove_punct(word1)
            word2 = remove_punct(word2)
            if syllab == True:
                word1 = syllabify(word1)
                word2 = syllabify(word2)
            #print (word1, word2) 
            non_rhyme_pairs.append((word1, word2))
        return non_rhyme_pairs
        

    def find_end_word(self, line):
        line = remove_punct(line)
        tokens = line.split()
        #blob = tb(line)
        #token = blob.tokens
        lastword = ''
        if len(tokens) > 0:
            pre_lastword = tokens[-1]
            if any((c in get_vowels()) for c in pre_lastword):
                lastword = pre_lastword
            elif len(tokens) > 1:
                lastword = tokens[-2]
            else:
                #print "ERROR1: " + str(token),
                #sys.stdout.flush()
                #break
                pass
        else:
            #print "ERROR2: " + str(token),
            #sys.stdout.flush()
            pass
        lastword = str(lastword)
        return lastword

    def index_rhyme_schema(self, rhyme_schema, assonance=True):
        #print rhyme_schema
        tuples = list(enumerate(rhyme_schema))
        for a in tuples:
            index_a = a[0]
            char_a = a[1]
            if assonance == False:
                if char_a == char_a.upper():
                    continue
            for b in tuples:
                index_b = b[0]
                char_b = b[1]
                
                if assonance == False:
                    if char_b == char_b.upper():
                        continue

                if char_a == char_b:
                    if index_a !=  index_b:
                        #print (index_a, index_b)
                        self.rhyme_indices.append((index_a, index_b))
                else:
                    if index_a != index_b:
                        #print (index_a, index_b)
                        self.non_rhyme_indices.append((index_a, index_b))
        clean_indices = []
        for i, j in list(set(self.rhyme_indices)):
            if not (j, i) in clean_indices:
                clean_indices.append((i, j))
                
        clean_non_indices = []
        for i, j in list(set(self.non_rhyme_indices)):
            if not (j, i) in clean_non_indices:
                clean_non_indices.append((i,j))
        #print (clean_indices, clean_non_indices)
        return clean_indices, clean_non_indices

    def get_lines(self):
        return self.lines

    def get_schema(self):
        return self.rhyme_schema

    def get_rhyme_pairs(self):
        return self.rhyme_pairs
    
    def get_non_rhyme_pairs(self):
        return self.non_rhyme_pairs

    def get_end_words(self):
        return self.end_words

