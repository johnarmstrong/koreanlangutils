# -*- coding: utf-8 -*-
'''
Created on May 11, 2016

@author: John
'''
import unittest

import koreancharutils as kcu

def aquote(s): # copied from utils - the only thing we need from that module
    try:
        return '<'  + s + '>' # TODO escape internal quotes
    except:
        return '<'  + str(s) + '>'
        
class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass
    
    def test_isHangulSyllable(self):
        for char,expected in (('a',False),
                              ('!',False), # ASCII
                              ('！',False), # Korean
                              ('ㄱ',False), # Compatibility Jamo
                              (kcu.ensureHangulJamo_L(u'ㄱ'),False), # Combining Jamo
                              ('가',False), # UTF-8
                              (u'가',True), # unicode
                              (u'가자',False)): # more than one syllable
            result = kcu.isHangulSyllable(char)
            self.assertEquals(result,expected)

    def test_normalizeHangul(self):
        for hangul,expected in (
                                ('이ㅂ니까','입니까'),
                                ('라','라'),
                                ('라고','라고'),
                                ('ㄴ은','는'),
                                ('르ㄹ','를'),
                                ('ㄴ아ㄹ','날')):
            norm = kcu.normalizeHangul(unicode(hangul))
            self.assertEquals(norm,unicode(expected))
                
    def test_joinHangulChars(self):
        for end1,beg2,expected in (
                                ('라','고','라고'),
                                ('ㄴ','은','는'),
                                ('르','ㄹ','를')):
            joined = kcu.joinHangulChars(unicode(end1),unicode(beg2))
            self.assertEquals(joined,unicode(expected))

    def test_composeHangulJamoToSyllable_combining(self):
        for syll in ('감','가'):
            L,V,T = kcu.decomposeHangulSyllableToJamo(unicode(syll))
            syll2 = kcu.composeHangulJamoToSyllable(L,V,T)
            self.assertEquals(syll,syll2)

    def test_composeHangulJamoToSyllable_compatibility(self):
        for syll in ('감','가'):
            L,V,T = kcu.decomposeHangulSyllableToJamo(unicode(syll))
            LCompat = kcu.hangulJamoToCompatibility_L(L)
            VCompat = kcu.hangulJamoToCompatibility_V(V)
            TCompat = kcu.hangulJamoToCompatibility_T(T)
                
            syll2 = kcu.composeHangulJamoToSyllable(LCompat,VCompat,TCompat)
            self.assertEquals(syll,syll2)
            
    def test_hangulJamoToTrans(self): # note - there is no hangulCompatibilityJamoToTrans
        for syll,expected in (('감','g|a|m'),('가','g|a|')): 
            L,V,T = kcu.decomposeHangulSyllableToJamo(unicode(syll))
            transSyll = '|'.join([kcu.hangulJamoToTrans(L),kcu.hangulJamoToTrans(V),kcu.hangulJamoToTrans(T)])
            self.assertEquals(transSyll,expected)
            
    def test_decomposeHangulSyllableToTrans(self):
        for syll,expected in (('감','g|a|m'),('가','g|a|')): 
            LTrans,VTrans,TTrans = kcu.decomposeHangulSyllableToTrans(unicode(syll))
            transSyll = '|'.join([LTrans,VTrans,TTrans])
            self.assertEquals(transSyll,expected)
       
    def test_getNextHangulPos(self):
        s = u'"얘들아， 엄마 왔다!"'
        start,end,hangul = kcu.getNextHangulPos(s)
        self.assertEquals(hangul,u'얘들아')
        start,end,hangul = kcu.getNextHangulPos(s,end)
        self.assertEquals(hangul,u'엄마')
        start,end,hangul = kcu.getNextHangulPos(s,end)
        self.assertEquals(hangul,u'왔다')
        start,end,hangul = kcu.getNextHangulPos(s,end)
        self.assertEquals(hangul,None)
        
    def test_getNextNonHangulAndHangulPoses(self):
        s = u'"얘들아， 엄마 왔다!"'
        startNonHg,endNonHg,nonHg,startHg,endHg,hg =  kcu.getNextNonHangulAndHangulPoses(s)
        self.assertEquals(nonHg,u'"')
        self.assertEquals(hg,u'얘들아')
        startNonHg,endNonHg,nonHg,startHg,endHg,hg =  kcu.getNextNonHangulAndHangulPoses(s,endHg)
        self.assertEquals(nonHg,u'， ')
        self.assertEquals(hg,u'엄마')
        startNonHg,endNonHg,nonHg,startHg,endHg,hg =  kcu.getNextNonHangulAndHangulPoses(s,endHg)
        self.assertEquals(nonHg,u' ')
        self.assertEquals(hg,u'왔다')
        startNonHg,endNonHg,nonHg,startHg,endHg,hg =  kcu.getNextNonHangulAndHangulPoses(s,endHg)
        self.assertEquals(nonHg,u'!"')
        self.assertEquals(hg,None)

    def test_getNonHangulAndHangulPairs(self):
        s = u'"얘들아， 엄마 왔다!"'
        expected = [('"','얘들아'),
                  ('， ','엄마'),
                  (' ','왔다'),
                  ('!"',None)]
        pairs = kcu.getNonHangulAndHangulPairs(s)
        self.assertEquals(len(expected),len(expected))
        for i,pair in enumerate(pairs):
            expectedPair = expected[i]
            self.assertEquals(pair,expectedPair)
          


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_normalizeHangul']
    unittest.main()