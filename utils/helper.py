#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re, string
import pyphen
from lxml import etree
from lxml.etree import tostring
#from itertools import chain


pyphen.language_fallback('de_DE_variant1')
syllable_dict = pyphen.Pyphen(lang='de_DE')

# exclude = set(string.punctuation)
#regex = re.compile('[%s]' % re.escape(string.punctuation + '.' + ',' + '—' + '-' + '--' + '–' +
#                                          '!' + '?' + '"' + '“' + '”' + "'" + ")" + "(" + "/" + "\\"))
regex = re.compile('[%s]' % re.escape("""1234567890!"#$%&\'()*+,-–./:;<=>?@[\\]^_`{|}~“”"""))

def find_ngrams(input_list, n):
    return zip(*[input_list[i:] for i in range(n)])

def get_vowels():
    vowels = set(u'aeiouäöüyauͤͤoͤ')
    return vowels

def get_diphtongs():
    diphtonge = []
    for v in get_vowels():
        for w in get_vowels():
            diphtonge.append(str(v+w))
            diphtonge.append(str(w+v))
    diphtonge = set(diphtonge)
    return diphtonge


def remove_punct(s):  # From Vinko's solution, with fix.
    newstr = regex.sub('', str(s))
    #if newstr2.endswith("/"):
    #    newstr2 = newstr2[:-1]
    return newstr

def syllabify_sonori(a_word):
    return sp(a_word)

def syllabify(a_word):
    return syllable_dict.inserted(str(a_word))

def strip_text_from_xml(node):
    etree.strip_tags(node, "*")
    stringparts = etree.tostring(node)
    #parts = ([node.text] +
    #        list(chain(*([c.text, tostring(c), c.tail] for c in node.getchildren()))) +
    #        [node.tail])
    #newparts = [i for i in filter(None, parts)]
    # filter removes possible Nones in texts and tails
    #print (''.join(newparts))
    #return ''.join(newparts)
    return stringparts

def get_nucleus(syllable):
    for d in diphtonge:
        if d in syllable:
            return d
    for v in get_vowels():
        if v in syllable:
            return v

def simplify_pos_label(label):
	if label.startswith('ADV'):
		return 'ADV'
	elif label.startswith('ADJ'):
		return 'ADJ'
	else:
		return label[:2]

def get_versification(meter_line):
        meter = ''.join(meter_line)
        meter = re.sub('\+', 'I', meter)
        meter = re.sub('\-', 'o', meter)
        #print(meter)
        hexameter =       re.compile('Ioo?Ioo?Ioo?Ioo?IooIo$')
        alxiambichexa =   re.compile("oIoIoIoIoIoIo?$")
        asklepiade =      re.compile("IoIooIIooIoI$") # 12 Ode
        glykoneus =       re.compile("IoIooIoI$")     # 8  Ode
        pherekrateus =    re.compile("IoIooIo$")      # 7  Ode
        iambelegus =      re.compile('oIoIoIoIIooIooI$')
        elegiambus =      re.compile('IooIooIo?oIoIoIoo?$')
        diphilius =       re.compile('IooIooI..IooI..$')
        prosodiakos =     re.compile('.IooIooII?$')
        sapphicusmaior =  re.compile('IoIIIooIIooIoI.$')
        sapphicusminor =  re.compile('IoI.IooIoI.$')
        iambicseptaplus = re.compile("oIoIoIoIoIoIoIo?")
        iambicpenta =     re.compile("oIoIoIoIoIo?$")
        iambicpentaspond= re.compile("IIoIoIoIoIo?$")
        iambictetra =     re.compile(".IoIoIoIo?$")
        iambictri =       re.compile(".IoIoIo?$")
        iambicdi =        re.compile(".IoIo?$")
        iambic =          re.compile(".IoIo?")
        iambicsingle =    re.compile("oI$")
        trochseptaplus =  re.compile('IoIoIoIoIoIoIo?')
        trochhexa =       re.compile('IoIoIoIoIoIo?$')
        trochpenta =      re.compile('IoIoIoIoIo?$')
        trochtetra =      re.compile('IoIoIoIo?$')
        trochtri =        re.compile('IoIoIo?$')
        trochdi =         re.compile('IoIo?$')
        trochsingle =     re.compile("Io$")
        troch =           re.compile('IoIo?')
        amphidi =         re.compile('o?IooIo$')
        amphidimix =      re.compile('^oIooIo')
        amphitri =        re.compile('o?IooIooIo?$')
        amphitetra =      re.compile('o?IooIooIooIo?$')
        amphipentaplus =  re.compile('o?IooIooIooIooIo?')
        amphisingle =     re.compile('oIo$')
        adoneus =         re.compile('IooI.$')
        adoneusspond =    re.compile('IooII$')
        amphiiambicmix =  re.compile('oI.*oIooIoo?I')
        amphitrochmix =   re.compile('Io.*oIooIoo?I')
        iambicseptainvert=re.compile("IooIoIoIoIoIoIo?$")
        iambichexainvert =re.compile("IooIoIoIoIoIo?$")
        iambicpentainvert=re.compile("IooIoIoIoIo?$")
        iambictetrainvert=re.compile("IooIoIoIo?$")
        iambictriinvert = re.compile("IooIoIo?$")
        iambicinvert =    re.compile('IooIoI')
        trochextrasyll=   re.compile('^I.*IooI.+')
        iambicextrasyll=  re.compile('^o.*IooI.+')
        #iambiccholstrict =re.compile('.IoI.IoIoII.$')
        iambiccholstrict =re.compile("oIoIoIoIoIooI$")
        iambicchol       =re.compile('o?.*IooI$')
        artemajor =       re.compile('oIooIooIooIo$')
        artemajorhalf =   re.compile('oIooIo$')
        zehnsilber =      re.compile('...I.....I$')
        anapaestdiplus =  re.compile('ooIooI')
        daktylpenta =     re.compile('o?IooIooIooIooIo?o?$')
        daktyltetra =     re.compile('o?IooIooIooIo?o?$')
        daktyltri =       re.compile('o?IooIooIo?o?$')
        daktyldi =        re.compile('o?IooIoo$')
        anapaestinit =    re.compile('ooI')
        daktylinit =      re.compile('o?Ioo')
        spondeus =        re.compile('II$')
        singleup =        re.compile('I$')
        singledown =      re.compile('o$')
        #alexandriner =    re.compile('oIoIoIoIoIoIo?$')
        #adoneus =        re.compile('IooIo$')
        #iambicamphicentermix = re.compile('oIoIooIoI$')

        verses = {'iambic.septa.plus':iambicseptaplus,\
                  'hexameter':hexameter,\
                  'alexandrine.iambic.hexa':alxiambichexa,\
                  'iambic.penta':iambicpenta,\
                  'iambic.penta.spondeus':iambicpentaspond,\
                  'iambic.tetra':iambictetra,\
                  'iambic.tri':iambictri,\
                  'iambic.di':iambicdi,\
                  'troch.septa.plus':trochseptaplus,\
                  'troch.hexa':trochhexa,\
                  'troch.penta':trochpenta,\
                  'troch.tetra':trochtetra,\
                  'troch.tri':trochtri,\
                  'troch.di':trochdi,\
                  'asklepiade':asklepiade,\
                  'glykoneus':glykoneus,\
                  'pherekrateus':pherekrateus,\
                  'iambelegus':iambelegus,\
                  'elegiambus':elegiambus,\
                  'diphilius':diphilius,\
                  'prosodiakos':prosodiakos,\
                  'sapphicusmaior':sapphicusmaior,\
                  'sapphicusminor':sapphicusminor,\
                  'amphi.penta.plus':amphipentaplus,\
                  'amphi.tetra':amphitetra,\
                  'amphi.tri':amphitri,\
                  'iambic.septa.invert':iambicseptainvert,\
                  'iambic.hexa.invert':iambichexainvert,\
                  'iambic.penta.invert':iambicpentainvert,\
                  'iambic.tetra.invert':iambictetrainvert,\
                  'iambic.tri.invert':iambictriinvert,\
                  'iambic.invert':iambicinvert,\
                  'daktyl.penta':daktylpenta,\
                  'daktyl.tetra':daktyltetra,\
                  'daktyl.tri':daktyltri,\
                  'troch.relaxed.syll':trochextrasyll,\
                  'iambic.relaxed.syll':iambicextrasyll,\
                  'iambic.chol.strict':iambiccholstrict,\
                  'iambic.chol.relaxed':iambicchol,\
                  'arte_major':artemajor,\
                  'arte_major.half':artemajorhalf,\
                  'adoneus':adoneus,\
                  'adoneus.spond':adoneusspond,\
                  'anapaest.di.plus':anapaestdiplus,\
                  'daktyl.di':daktyldi,\
                  'amphi.di.relaxed':amphidi,\
                  'amphi.single':amphisingle,\
                  'amphi.iambic.mix':amphiiambicmix,\
                  'amphi.troch.mix':amphitrochmix,\
                  'anapaest.init':anapaestinit,\
                  'daktyl.init':daktylinit,\
                  'amphi.di.mix':amphidimix,\
                  'zehnsilber':zehnsilber,\
                  'spondeus':spondeus,\
                  'iambic.single':iambicsingle,\
                  'troch.single':trochsingle,\
                  'single.down':singledown,\
                  'single.up':singleup}

        label = None
        for label, pattern in verses.items():
                result = pattern.match(meter)
                #if label == 'chol.iamb':
                #       result = pattern.search(meter)
                if result != None:
                        return label
        else: return 'other'

