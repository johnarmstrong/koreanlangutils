# -*- coding: utf-8 -*-
'''
Created on May 12, 2016

@author: John
'''

import sys

import unittest

import koreanmorphutils as mu

from test_koreanmorphutils_data import *

def squote(s,esc=False):
    sEsc = s
    if esc:
        sEsc = s.replace('\\','\\\\')
        sEsc = sEsc.replace('\'','\\\'')
    return '\'' + sEsc + '\''

def quotedOrNone(s):
    return squote(s) if s else 'None'

def quotedOrNoneUni(s):
    return 'u' + squote(s) if s else 'None'


class Test(unittest.TestCase):

    def setUp(self):
        pass


    def tearDown(self):
        pass

    def test_getEndingAdderForStem(self):
        for stem,irr,expectedEndingAdderName in test_getEndingAdderForStem_data:
            endingAdderClass = mu.getEndingAdderForStem(stem,irr)
            endingAdderName = endingAdderClass().getName()
            if True:
                self.assertEquals(endingAdderName,expectedEndingAdderName)
            else:
                print >> sys.stderr,  "(u'%s',%s,'%s')," % (stem,quotedOrNone(irr),endingAdderName)


    def test_determineEndingType(self):
        for postC,postV,expectedEndingType,expectedDerivedPostV in test_determineEndingType_data:
            endingType,derivedPostV = mu.determineEndingType(postC,postV) # returns (endingType,postV)
            if True:
                self.assertEquals(endingType,expectedEndingType)
                self.assertEquals(derivedPostV,expectedDerivedPostV)  
            else:                      
                print >> sys.stderr, "(u'%s',%s,'%s',u'%s')," %(postC,quotedOrNoneUni(postV),endingType,derivedPostV)
            
    def test_addParticle(self):
        for word,postC,postV,expectedWordPlusParticle in test_addParticle_data:
            wordPlusParticle = mu.addParticle(word,postC,postV)
            if True:
                self.assertEquals(wordPlusParticle,expectedWordPlusParticle)
            else:
                print >> sys.stderr, "(u'%s',u'%s',%s,'%s')," %(word,postC,quotedOrNoneUni(postV),wordPlusParticle)

    def test_makeInfinitive(self):
        for stem,irr,expectedStemPlusInfEnding,_ in test_makeInfinitive_data:
            stemPlusInfEnding = mu.makeInfinitive(stem,irr,False)
            if True:
                self.assertEquals(stemPlusInfEnding,expectedStemPlusInfEnding)
            else:
                stemPlusInfEndingMaxVariants = mu.makeInfinitive(stem,irr,True)
                print >> sys.stderr, "(u'%s',%s,u'%s',u'%s')," % (stem,quotedOrNone(irr),stemPlusInfEnding,stemPlusInfEndingMaxVariants)

    def test_makeInfinitive_maxVariants(self):
        for stem,irr,_,expectedStemPlusInfEndingMaxVariants in test_makeInfinitive_data: # same data as for test_makeInfinitive
            stemPlusInfEndingMaxVariants = mu.makeInfinitive(stem,irr,True)
            if True:
                self.assertEquals(stemPlusInfEndingMaxVariants,expectedStemPlusInfEndingMaxVariants)
            
    def test_addEnding(self):
        prevStem = None
        for stem,irr,postC,postV,expectedStemPlusEnding in test_addEnding_data: 
            stemPlusEnding = mu.addEnding(stem,irr,postC,postV)
            if True:
                self.assertEquals(stemPlusEnding,expectedStemPlusEnding)
            else:
                if stem != prevStem:
                    print >> sys.stderr,'' # put empty lines between stem and ending sets
                    prevStem = stem
                else:
                    print >> sys.stderr, "(u'%s',%s,u'%s',%s,u'%s')," %(stem,quotedOrNone(irr),postC,quotedOrNoneUni(postV),stemPlusEnding)






if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()