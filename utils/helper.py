#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re, string
import pyphen
from lxml import etree
from lxml.etree import tostring
#from itertools import chain

from nltk import bigrams as bi


pyphen.language_fallback('de_DE_variant1')
syllable_dict = pyphen.Pyphen(lang='de_DE')

# exclude = set(string.punctuation)
#regex = re.compile('[%s]' % re.escape(string.punctuation + '.' + ',' + '—' + '-' + '--' + '–' +
#                                          '!' + '?' + '"' + '“' + '”' + "'" + ")" + "(" + "/" + "\\"))
regex = re.compile('[%s]' % re.escape("""1234567890!"#$%&\'()*+,-–./:;<=>?@[\\]^_`{|}~“”"""))

punct = """1234567890!"#$%&\'()*+,-–./:;<=>?@[\\]^_`{|}~“”"""
def find_ngrams(input_list, n):
    return zip(*[input_list[i:] for i in range(n)])

def get_vowels():
    vowels = set(u'aeiouäöüyauͤͤoͤ')
    return vowels

def get_foot_anno(footmeter, delimiter="\|"):
        feetout = []
        meter = re.sub(delimiter, '', footmeter)
        bimeter = bi([m for m in re.sub(delimiter, ':', str(footmeter))])
        for a, b in bimeter:
                if a == ':':
                        continue
                elif b == ':':
                        feetout.append(':')
                else:
                        feetout.append('.')
        if len(feetout) < len(meter):
                feetout.append('.')
        return feetout


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
    #for bad in node.xpath("//note[@anchored=\'true\']"):
    #for bad in node.xpath("//note"):
    #    bad.getparent().remove(bad)
    #etree.strip_elements(node, 'note', with_tail=False)
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


def normalize_characters(text):
        text = re.sub('<[^>]*>', '', text)
        text = re.sub('ſ', 's', text)
        text = re.sub('\[', '', text)
        text = re.sub('\]', '', text)
        #text = re.sub('’', "'", text)
        if text.startswith("b'"):
                text = text[2:-1]
        text = re.sub('&#223;', 'ß', text)
        text = re.sub('&#383;', 's', text)
        text = re.sub('u&#868;', 'ü', text)
        text = re.sub('a&#868;', 'ä', text)
        text = re.sub('o&#868;', 'ö', text)
        text = re.sub('&#246;', 'ö', text)
        text = re.sub('&#224;', 'a', text) # quam with agrave
        text = re.sub('&#772;', 'm', text) # Combining Macron in kom772t
        text = re.sub('&#8217;', "'", text)
        text = re.sub('&#42843;', "r", text) # small rotunda
        text = re.sub('&#244;', "o", text) # o with circumflex (ocr)
        text = re.sub('&#230;', "ae", text)
        text = re.sub('&#8229;', '.', text) # Two Dot Leader ... used as 'lieber A.'
        text = re.sub('Jch', 'Ich', text)
        text = re.sub('Jhr', 'Ihr', text)
        text = re.sub('Jst', 'Ist', text)
        text = re.sub('JCh', 'Ich', text)
        text = re.sub('jch', 'ich', text)
        text = re.sub('Jn', 'In', text)
        text = re.sub('DJe', 'Die', text)
        text = re.sub('Wje', 'Wie', text)
        text = re.sub('¬', '-', text) # negation sign
        text = re.sub(" ’ ", "'", text) # Strange Apostrophe
        text = re.sub("’", "'", text) # Strange Apostrophe
        text = re.sub("´", "'", text) # Strange Apostrophe
        text = re.sub("''", '"', text) # Strange Apostrophe
        text = re.sub("—", "--", text) # Is not recognized as symbol
        text = re.sub(" - ", "-", text) # Is not recognized as symbol
        text = re.sub("”", '"', text) # Is not recognized as symbol
        #text = re.sub('Jn', 'In', text)
        text = text.encode("utf-8", 'replace')
        #text = text.decode("utf-8", 'replace')
        text = re.sub(b'o\xcd\xa4', b'\xc3\xb6', text) # ö
        text = re.sub(b'u\xcd\xa4', b'\xc3\xbc', text) # ü
        text = re.sub(b'a\xcd\xa4', b'\xc3\xa4', text) # ä
        text = re.sub(b'&#771;', b'\xcc\x83', text) # Tilde
        text = re.sub(b'&#8222;', b'\xe2\x80\x9d', text) # Lower Quot Mark
        text = re.sub(b'\xea\x9d\x9b', b'r', text) # small Rotunda
        text = re.sub(b'\xea\x9d\x9a', b'R', text) # big Rotunda
        text = text.decode('utf-8')
        ftl = text[:2] # check if first two letters are capitalized
        try:
                if ftl == ftl[:2].upper():
                        text = ftl[0] + ftl[1].lower() + text[2:]
        except IndexError:
                pass
        return text

def manual_correction(hyphenated):
        hyphenated = re.sub('·', '-', hyphenated)
        if hyphenated == 'berwock':
                hyphenated = 'ber-wock'
        if hyphenated == 'again':
                hyphenated = 'a-gain'
        if hyphenated == 'awhile':
                hyphenated = 'a-while'
        if hyphenated == 'galumph':
                hyphenated = 'ga-lumph'
        if hyphenated == 'emy':
                hyphenated = 'e-my'
        if hyphenated == 'abide':
                hyphenated = 'a-bide'
        if hyphenated == 'Callay':
                hyphenated = 'Cal-lay'
        if hyphenated == 'ible':
                hyphenated = 'ib-le'
        if hyphenated == 'erthrow':
                hyphenated = 'er-throw'
        if hyphenated == 'present':
                hyphenated = 'pre-sent'
        if hyphenated == 'replies':
                hyphenated = 're-plies'
        if hyphenated == 'mankind':
                hyphenated = 'man-kind'
        if hyphenated == 'apests':
                hyphenated = 'a-pests'
        if hyphenated == 'Iam':
                hyphenated = 'I-am'
        if hyphenated == 'Dactyl':
                hyphenated = 'Dac-tyl'
        if hyphenated == 'alarm':
                hyphenated = 'a-larm'
        if hyphenated == 'Alone':
                hyphenated = 'A-lone'
        if hyphenated == 'asleep':
                hyphenated = 'a-sleep'
        if hyphenated == 'awoke':
                hyphenated = 'a-woke'
        if hyphenated == 'away':
                hyphenated = 'a-way'
        if hyphenated == 'awoke':
                hyphenated = 'a-woke'
        if hyphenated == 'Awake':
                hyphenated = 'A-wake'
        if hyphenated == 'apace':
                hyphenated = 'a-pace'
        if hyphenated == 'among':
                hyphenated = 'a-mong'
        if hyphenated == 'against':
                hyphenated = 'a-gainst'
        if hyphenated == 'immed':
                hyphenated = 'im-med'
        if hyphenated == 'thawed':
                hyphenated = 'thaw-ed'
        if hyphenated == 'ula':
                hyphenated = 'u-la'
        if hyphenated == 'able':
                hyphenated = 'ab-le'
        if hyphenated == 'ima':
                hyphenated = 'i-ma'
        if hyphenated == 'eter':
                hyphenated = 'e-ter'
        if hyphenated == 'yssin':
                hyphenated = 'ys-sin'
        if hyphenated == 'icate':
                hyphenated = 'i-cate'
        if hyphenated == 'cimer':
                hyphenated = 'ci-mer'
        if hyphenated == 'whoso':
                hyphenated = 'who-so'
        if hyphenated == 'gazes':
                hyphenated = 'ga-zes'
        if hyphenated == 'mazes':
                hyphenated = 'ma-zes'
        if hyphenated == 'fairest':
                hyphenated = 'fair-est'
        if hyphenated == 'adise':
                hyphenated = 'a-dise'
        if hyphenated == 'deathbed':
                hyphenated = 'death-bed'
        if hyphenated == 'crossed':
                hyphenated = 'cross-ed'
        if hyphenated == 'laden':
                hyphenated = 'lad-den'
        if hyphenated == 'ation':
                hyphenated = 'a-tion'
        if hyphenated == 'lazy':
                hyphenated = 'la-zy'
        if hyphenated == 'blanker':
                hyphenated = 'blan-ker'
        #hyphenated = check_sonority(hyphenated)
        hyphenated = re.sub('-', '·', hyphenated)
        return hyphenated


def fix_dangling(characters, tokenized):
        #try:
        if tokenized.count(characters) > 0:
                s_index = tokenized.index(characters)
                tokenized[s_index-1:s_index+1] = [''.join([tokenized[s_index-1], "", tokenized[s_index]])]
        else: pass
        #except ValueError:
        #       pass
        return tokenized


def concatenate_words(tokenized):
        try:
                tokenized = fix_dangling('s', tokenized)
                tokenized = fix_dangling("'s", tokenized)
                tokenized = fix_dangling("'d", tokenized)
                tokenized = fix_dangling("t'", tokenized)
                tokenized = fix_dangling('st', tokenized)
                tokenized = fix_dangling('ll', tokenized)
                tokenized = fix_dangling("'ll", tokenized)
                tokenized = fix_dangling("'ve", tokenized)
                tokenized = fix_dangling("'re", tokenized)
                tokenized = fix_dangling("n't", tokenized)
                tokenized = fix_dangling("'", tokenized)
                tokenized = fix_dangling('d', tokenized)
                consonants = "bcdfghjklmnpqrstvwxz"
                for consonant in consonants:
                        app_consonant = "'" + consonant
                        tokenized = fix_dangling(consonant, tokenized)
                        tokenized = fix_dangling(app_consonant, tokenized)
                        for consonant1 in consonants:
                                dd_consonant = consonant + consonant1
                                tokenized = fix_dangling(dd_consonant, tokenized)
                #bigrams = [('that', 's'), ('had', 'st'), ('hill', 's'), ('vest', 's'), ('ry', 's'), ('en', 's'), ('I', 'll'), ('o', 'er'), ('sin', 'in'), ('man', 's'), ('ture', 's'), ('ri', 'ers'), ('you', 'll')]
                #bigrams = [('had', 'st'), ('I', 'll'), ('ev', 'n'), ('o', 'er'), ('sin', 'in'), ('ri', 'ers'), ('you', 'll'), ('cho', 'irs'), ('ceiv', 'st')]
                bigrams = [('mo', 're'), ('ha', 've'), ('breat', 'he'), ('lo', 'ne'), ('on', 'ce'), ('the', 'se'), ('tho', 'se'), ('sto', 'ne'), ('cu', 're'), ('nur', 'se'), ('ien', 'ce'), ('ev', 'n'), ('o', 'er'), ('sin', 'in'), ('ri', 'ers'), ('cho', 'irs'), ('ba', 're')]
                for i, j in bigrams:
                        if i in tokenized and j in tokenized :
                                #i_index = tokenized.index(i)
                                i_indices = [index for index, value in enumerate(tokenized) if value == i]
                                j_indices = [index for index, value in enumerate(tokenized) if value == j]
                                #j_index = tokenized.index(j)
                                for i_index in i_indices:
                                        for j_index in j_indices:
                                                if i_index + 1 == j_index:
                                                        print('COUPLE MATCH: ', tokenized[i_index], tokenized[j_index])
                                                        tokenized[i_index:j_index+1] = [''.join(tokenized[i_index:j_index+1])]
                        #except ValueError:
                        #       pass
        except IndexError:
                pass
        return tokenized



def get_versification(meter_line, measure_type='f'):
        # full = f
        # short = s
        # intermediate = i
        meter = ''.join(meter_line)
        meter = re.sub('\+', 'I', meter)
        meter = re.sub('\-', 'o', meter)
        #print(meter)
        hexameter =       re.compile('^Ioo?Ioo?Ioo?Ioo?IooIo$')
        alxiambichexa =   re.compile("^oIoIoIoIoIoIo?$")
        asklepiade =      re.compile("^IoIooIIooIoI$") # 12 Ode
        glykoneus =       re.compile("^IoIooIoI$")     # 8  Ode
        pherekrateus =    re.compile("^IoIooIo$")      # 7  Ode
        iambelegus =      re.compile('^oIoIoIoIIooIooI$')
        elegiambus =      re.compile('^IooIooIo?oIoIoIoo?$')
        diphilius =       re.compile('^IooIooI..IooI..$')
        prosodiakos =     re.compile('^.IooIooII?$')
        sapphicusmaior =  re.compile('^IoIIIooIIooIoI.$')
        sapphicusminor =  re.compile('^IoI.IooIoI.$')
        iambicseptaplus = re.compile("^oIoIoIoIoIoIoIo?")
        iambicpenta =     re.compile("^oIoIoIoIoIo?$")
        iambicpentaspond= re.compile("^IIoIoIoIoIo?$")
        iambictetra =     re.compile("^.IoIoIoIo?$")
        iambictri =       re.compile("^.IoIoIo?$")
        iambicdi =        re.compile("^.IoIo?$")
        iambic =          re.compile("^.IoIo?")
        iambicsingle =    re.compile("^oI$")
        trochseptaplus =  re.compile('^IoIoIoIoIoIoIo?')
        trochhexa =       re.compile('^IoIoIoIoIoIo?$')
        trochpenta =      re.compile('^IoIoIoIoIo?$')
        trochtetra =      re.compile('^IoIoIoIo?$')
        trochtri =        re.compile('^IoIoIo?$')
        trochdi =         re.compile('^IoIo?$')
        trochsingle =     re.compile("^Io$")
        troch =           re.compile('^IoIo?')
        amphidi =         re.compile('^o?IooIo$')
        amphidimix =      re.compile('^oIooIo')
        amphitri =        re.compile('^oIooIooIo?$')
        amphitriplus =    re.compile('^oIooIooIo')
        amphitetra =      re.compile('^oIooIooIooIo?$')
        amphitetraplus =  re.compile('^oIooIooIooIo')
        amphipentaplus =  re.compile('^oIooIooIooIooIo?')
        amphisingle =     re.compile('^oIo$')
        adoneus =         re.compile('^IooI.$')
        adoneusspond =    re.compile('^IooII$')
        daktylpenta =     re.compile('^IooIooIooIooIo?o?$')
        daktylpentaplus = re.compile('^IooIooIooIooIooIoo')
        daktyltetra =     re.compile('^IooIooIooIo?o?$')
        daktyltetraplus = re.compile('^IooIooIooIoo')
        daktyltri =       re.compile('^IooIooIo?o?$')
        daktyltriplus =   re.compile('^IooIooIoo')
        daktyldi =        re.compile('^IooIoo$')
        daktyldiplus =    re.compile('^IooIoo')
        amphiiambicmix =  re.compile('^oI.*oIooIoo?I')
        amphitrochmix =   re.compile('^Io.*oIooIoo?I')
        artemajor =       re.compile('^oIooIooIooIo$')
        artemajorhalf =   re.compile('^oIooIo$')
        iambicseptainvert=re.compile("^IooIoIoIoIoIoIo?$")
        iambichexainvert =re.compile("^IooIoIoIoIoIo?$")
        iambicpentainvert=re.compile("^IooIoIoIoIo?$")
        iambictetrainvert=re.compile("^IooIoIoIo?$")
        iambictriinvert = re.compile("^IooIoIo?$")
        iambicinvert =    re.compile('^IooIoI')
        trochextrasyll=   re.compile('^I.*IooI.+')
        iambicextrasyll=  re.compile('^o.*IooI.+')
        #iambiccholstrict =re.compile('.IoI.IoIoII.$')
        iambiccholstrict =re.compile("^oIoIoIoIoIooI$")
        iambicchol       =re.compile('^o?.*IooI$')
        zehnsilber =      re.compile('^...I.....I$')
        anapaestdiplus =  re.compile('^ooIooI')
        anapaesttriplus = re.compile('^ooIooIooI')
        anapaesttetraplus=re.compile('^ooIooIooIooI')
        anapaestinit =    re.compile('^ooI')
        daktylinit =      re.compile('^o?Ioo')
        spondeus =        re.compile('^II$')
        singleup =        re.compile('^I$')
        singledown =      re.compile('^o$')
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
                  'daktyl.penta':daktylpenta,\
                  'daktyl.tetra':daktyltetra,\
                  'daktyl.tri':daktyltri,\
                  'amphi.penta.plus':amphipentaplus,\
                  'amphi.tetra':amphitetra,\
                  'amphi.tetra.plus':amphitetraplus,\
                  'amphi.tri':amphitri,\
                  'amphi.tri.plus':amphitriplus,\
                  'amphi.relaxed':amphidi,\
                  'daktyl.penta.plus':daktylpentaplus,\
                  'daktyl.tetra.plus':daktyltetraplus,\
                  'daktyl.tri.plus':daktyltriplus,\
                  'daktyl.di.plus':daktyldiplus,\
                  'daktyl.di':daktyldi,\
                  'anapaest.tetra.plus':anapaesttetraplus,\
                  'anapaest.tri.plus':anapaesttriplus,\
                  'anapaest.di.plus':anapaestdiplus,\
                  'arte_major':artemajor,\
                  'arte_major.half':artemajorhalf,\
                  'adoneus':adoneus,\
                  'adoneus.spond':adoneusspond,\
                  'iambic.septa.invert':iambicseptainvert,\
                  'iambic.hexa.invert':iambichexainvert,\
                  'iambic.penta.invert':iambicpentainvert,\
                  'iambic.tetra.invert':iambictetrainvert,\
                  'iambic.tri.invert':iambictriinvert,\
                  'iambic.invert':iambicinvert,\
                  'troch.relaxed':trochextrasyll,\
                  'iambic.relaxed':iambicextrasyll,\
                  'iambic.chol.strict':iambiccholstrict,\
                  'iambic.relaxed.chol':iambicchol,\
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
                hebungen = meter.count('I')
                counters = {0:'zero', 1:'single', 2:'di', 3:'tri', 4:'tetra', 5:'penta', 6:'hexa', 7:'septa'}
                if hebungen > 6:
                        hebungen_label = 'septa.plus'
                else:
                        hebungen_label = counters[hebungen]
                if 'relaxed' in label:
                        label = re.sub('.relaxed', '.' + hebungen_label + '.relaxed', label)
                if result != None:
                        split = label.split('.')
                        if type = 's':
                                return split[0]
                        if type = 'i':
                                return '.'.join(split[:2])
                        else:
                                return label
        else: return 'other'


