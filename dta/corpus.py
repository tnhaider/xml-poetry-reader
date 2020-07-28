#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, re
import json, csv
import shutil, string
import numpy as np
from lxml import etree
from collections import Counter
from operator import itemgetter
from inout.utils.helper import *
from random import shuffle
import json

from inout.dta.document import Document
from inout.dta.poem import Poem



#import pyphen
#from textblob_de import TextBlobDE as tb
#from sklearn.feature_extraction import DictVectorizer as DV


class Corpus(object):
    def __init__(self, corpuspath, debug=False):
        self.debug = debug
        self.corpuspath = corpuspath
        print('TEI corpus at path ' + corpuspath + ' initialized.')
        #self.allpoems = self.find_poems(self.corpuspath, debug=True)
        #self.all_rhyme_pairs = self.find_rhyme_pairs()
        #self.all_non_rhyme_pairs = self.find_non_rhyme_pairs()

    def doc_iter(self):
        paths = [os.path.join(self.corpuspath, fn) for fn in next(os.walk(self.corpuspath))[2]]
        corpus_files = []
        alldocs = []
        for path in paths:
            # print path
            if not path.endswith('.swp'):  # and '18' in path:
                doc = Document(path)
                #doc.read()
                alldocs.append(doc)
        return alldocs

    def get_all_g2p(self):
        init_dict = {}
        paths = [os.path.join(self.corpuspath, fn) for fn in next(os.walk(self.corpuspath))[2]]
        c = 0
        for path in paths:
            c += 1
            print(c, len(paths), path)
            d = Document(path)
            g2p_dict = d.get_graphem_phonem_dict(d.get_path())
            init_dict.update(g2p_dict)
        return init_dict

    def print_rhyme_pairs(self):
        for rp in self.all_rhyme_pairs:
            print (rp)
        print (len(self.all_rhyme_pairs))

    def get_authors(self):
        authors = []
        for poem in self.allpoems:
            authors.append(poem.get_author())
        for i, j in sorted(Counter(authors).items(), key=itemgetter(1))[::-1]:
            print ("H: ", j, " ... ", "S: ", i, "\\\\")

    def read_poems(self):
        a_dir = self.corpuspath
        if self.debug==True:
            paths = [os.path.join(a_dir, fn) for fn in next(os.walk(a_dir))[2]][:5]
        if self.debug==False:
            paths = [os.path.join(a_dir, fn) for fn in next(os.walk(a_dir))[2]]
        corpus_files = []
        allpoems = []
        print('Loading ' + str(len(paths)) + ' documents.')
        c = 0
        n_poems = 0
        for path in paths:
            c += 1
            print('\nLoaded ' + str(n_poems) + ' poems in ' + str(c) + ' documents of ' + str(len(paths)) + ' documents so far.')
            #print path
            if not path.endswith('.swp'):  # and '18' in path:
                doc = Document(path)
                doc.read()
                n_poems += doc.get_amountof_poems()
                for poem in doc.get_poems():
                    yield poem
        #return allpoems

    def find_rhyme_pairs(self):
        allpairs = []
        for poem in self.allpoems:
            for stanza in poem.get_stanzas():
                pairs = stanza.get_rhyme_pairs()
                for pair in pairs:
                    allpairs.append(pair)
        return allpairs
    
    def find_non_rhyme_pairs(self):
        allpairs = []
        for poem in self.allpoems:
            for stanza in poem.get_stanzas():
                pairs = stanza.get_non_rhyme_pairs()
                for pair in pairs:
                    allpairs.append(pair)
        return allpairs

    def get_rhyme_pairs(self):
        return self.rhyme_pairs

    def get_poems(self):
        return self.allpoems

    def get_all_poems(self):
        return self.allpoems

    def get_corpuspath(self):
        return self.corpuspath
    
    
    def get_4_schemas(self):
        schemas = []
        for poem in self.allpoems:
            stanzas = poem.get_stanzas()
            for stanza in stanzas:
                schema = stanza.get_rhyme_schema()
                try:
                    if len(schema) == 4:
                        if schema == "None":
                            print (poem.get_author())
                            print (poem.get_year())
                            #print(etree.tostring(poem.get_lg_element(), pretty_print=True))
                        else:
                            schemas.append(schema)
                except TypeError:
                    continue
        #for schema in schemas:
        #    print schema
        for i, j in sorted(Counter(schemas).items(), key=itemgetter(1))[::-1]:
            print ("H: ", j, " ... ", "S: ", i, "\\\\")
        print (len(schemas))
        
    def get_all_schemas(self):
        all_schemas = {}
        for poem in self.allpoems:
            stanzas = poem.get_stanzas()
            for stanza in stanzas:
                schema = stanza.get_rhyme_schema()
                if not schema == "None":
                    try:
                        group = all_schemas.setdefault(len(schema), [])
                        group.append(schema)
                    except TypeError:
                        continue
        for length, schemas in all_schemas.items():
            print()
            print ("LENGTH:", length)
            alllen = 0
            for i, j in sorted(Counter(schemas).items(), key=itemgetter(1))[::-1]:
                alllen += j
            print("#ALL:", int(alllen/2))
            for i, j in sorted(Counter(schemas).items(), key=itemgetter(1))[::-1]:
                print ("W:", round(j/float(alllen),3), " ... ", "H: ", int(j/2), " ... ", "S: ", i, "\\\\")
   



    def get_stats(self):
        no_poems = len(self.allpoems)
        no_stanzas = 0
        no_lines = 0
        no_token = 0
        no_syllables = 0
        no_line_syllables = []
        authors = []

        for poem in self.allpoems:
            author = poem.get_author()
            authors.append(author)
            no_stanzas += len(poem.get_stanzas())
            for stanza in poem.get_stanzas():
                lines = stanza.get_lines()
                no_lines += len(lines)
                for line in lines:
                    tokens = line.split()
                    no_token += len(tokens)
                    syll_per_line = 0
                    for token in tokens:
                        hyphenated = syllabify(token)
                        syllables = hyphenated.split('-')
                        no_syllables += len(syllables)
                        syll_per_line += len(syllables)
                    no_line_syllables.append(syll_per_line)

        author_distr = sorted(Counter(authors).items(), key=itemgetter(1))[::-1]

        print ("Syllables per line Distrib: ", str(sorted(Counter(no_line_syllables).items(), key=itemgetter(1))))

        for author, count in author_distr:
            print (author, " & ", count, " \\\\")

        print ("Authors Distrib: ", str(author_distr))
        print ("POEMS: ", str(no_poems))
        print ("STANZAS: ", str(no_stanzas))
        print ("VERSES: ", str(no_lines))
        print ("TOKENS: ", str(no_token))
        print ("Syllables: ", str(no_syllables))
        print ("Syllables per line average: " + str(np.mean(no_line_syllables)))
        print ("Syllables per line median: " + str(np.median(no_line_syllables)))
        print ("No of Authors: ", str(len(dict(author_distr).keys())))
        print ("Poems per Author Mean: ", str(np.mean(dict(author_distr).values())))
        print ("Poems per Author Median: ", str(np.median(dict(author_distr).values())))
        print ("Min Max Poems per Author: ", str(np.min(dict(author_distr).values())), str(np.max(dict(author_distr).values())))


    
if __name__ == '__main__':
    
    c = Corpus(sys.argv[1])
    #c.get_all_schemas()
    
    '''
    #g2p = c.get_all_g2p()
    #for item in g2p.items():
    #    print(item)
        
    #f = open('g2p.dict.json', 'w')
    #json.dump(g2p, f)
    
    
    all_rhyme_pairs = c.find_rhyme_pairs()
    all_non_rhyme_pairs = c.find_non_rhyme_pairs()
    #print (all_non_rhyme_pairs)
    
    anrp = []
    for r1, r2 in all_non_rhyme_pairs:
        if str(r1) != str(r2):
            anrp.append((r1, r2))
    all_non_rhyme_pairs = list(set(anrp))
    
    print(all_rhyme_pairs)
    #print(all_non_rhyme_pairs)
    
    
    
    mixed = []
    shuffle(all_non_rhyme_pairs)
    
    for r1, r2 in set(all_rhyme_pairs):
        if r1.startswith("xmlns") or r2.startswith("xmlns") or " " in r1 or " " in r2: 
            continue
        else:
            mixed.append([r1, r2, 'y'])
        
    #c = 0
    #while c < len(all_rhyme_pairs):
    for nr1, nr2 in all_non_rhyme_pairs:
        if "xmlns" in nr1 or "xmlns" in nr2 or " " in nr1 or " " in nr2:
            continue
        else:
            mixed.append([nr1, nr2, 'n'])
            #c += 1
        
        
    newmixed = []    
    for w1, w2, label in mixed:
        if w1.endswith('ln'):
            w1 = w1[:-2]
        if w2.endswith('ln'):
            w2 = w2[:-2]
        newmixed.append((w1.lower(),w2.lower(),label))
        
        
    rp_file = open('hiphop_full_train_with_assonance.csv', 'w')
    rp0_file = open('hiphop_full_test_with_assonance.csv', 'w')
    #nrp_file = open('non_rhyme_pairs_dta.csv', 'w')
        
    shuffle(newmixed)
    
    for r1, r2, i in newmixed:
        line = r1 + u"\t" + r2 + u"\t" + i
        rp_file.write(line)
        rp_file.write('\n')
        
    for r1, r2, i in newmixed:
        if i == 'n':
            i = '0'
        elif i == 'y':
            i = '1'
        line = i+ u"\t" + r1 + u"\t" + r2
        rp0_file.write(line)
        rp0_file.write('\n')
        
    #counter = 0
    #for r1, r2 in all_non_rhyme_pairs:
    #    counter += 1
    #    line = str(str(counter) + u"\t" + str(r1) + u"\t" + str(r2))
    #    nrp_file.write(line)
    #    nrp_file.write('\n')
    '''
        
    
