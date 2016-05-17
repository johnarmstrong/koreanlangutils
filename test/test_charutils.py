# -*- coding: utf-8 -*-
'''
Created on May 11, 2016

@author: John
'''
import unittest,re

from sys import maxunicode

import charutils as cu


class Test(unittest.TestCase):


    def setUp(self):
        pass

    def tearDown(self):
        pass
    
    def test_surrogatePairToCodepoint(self):
        cp32 = cu.surrogatePairToCodepoint(u'𠀀')
        self.assertEqual(cp32,0x20000)
        
    def test_codepointToSurrogatePair(self):
        sp = cu.codepointToSurrogatePair(0x20000)
        self.assertEquals(sp,u'𠀀')
        
    def test_findFirstSurrogatePair(self):
        for s,expected in ((u'a',-1),(u'aaaa',-1),(u'',-1),(u'𠀀',0),(u'a𠀀',1),(u'a𠀀b',1),(u'a𠀀b𠀀c',1)):
            offset = cu.findFirstSurrogatePair(s)
            self.assertEquals(offset,expected)
    
    def test_getSurrogatePairAtOffset(self):
        return
        for string,expectedOffset,expectedChar in ((u'𠀀',0,u'𠀀'),(u'a𠀀',1,u'𠀀'),(u'a𠀀b',1,u'𠀀'),(u'a𠀀b𠀀c',1,u'𠀀')):
            offset = cu.findFirstSurrogatePair(string)
            self.assertEquals(offset,expectedOffset)
            char = cu.getSurrogatePairAtOffset(string,offset)
            self.assertEquals(char,expectedChar,'Failure on ' + string)
        
    def test_getSurrogatePairAtOffset_bad_input(self):
        for string,offset in ((u'𠀀',-1,),(u'',0),(u'𠀀',1),(u'𠀀',2),(u'aa𠀀',0),(u'a𠀀',0)):
            #print string,offset
            self.assertRaises(Exception,lambda: cu.getSurrogatePairAtOffset(string,offset))

        
    def test_unicodeVersion(self):
        version = cu.unicodeVersion()
        #self.assertEquals(version,'5.2.0')
        self.assertTrue(re.match(r'\d+\.\d+(\.\d+)?',version))
        
    def test_maxSupportedCodePoint(self):
        self.assertEqual(cu.maxSupportedCodePoint(),maxunicode)
        
    def test_usesSurrogatePairs(self):
        if maxunicode <= 0xFFFF:
            self.assertTrue(cu.usesSurrogatePairs())
        else:
            self.assertFalse(cu.usesSurrogatePairs())
    
    def test_isAsciiChar(self):
        for obj,expected in ((u'a',True),(u'ab',False),('a',True),(u'',False),(None,False),(u'ㄱ',False),(u'가',False)):
            result = cu.isAsciiChar(obj)
            self.assertEquals(result,expected)

    def test_isStrChar(self):
        for obj,expected in ((u'a',False),('ab',False),('a',True),('',False),(None,False),('ㄱ',False),('가',False)): # last two are utf-8
            result = cu.isStrChar(obj)
            self.assertEquals(result,expected)

    def test_isUnicodeChar(self):
        for obj,expected in ((u'a',True),(u'ab',False),('a',False),(u'',False),(None,False),(u'ㄱ',True),(u'가',True),(u'가자',False),(u'㐀',True),(u'𠀀',True)):
            result = cu.isUnicodeChar(obj)
            self.assertEquals(result,expected)
            
    def test_isUnicodeString(self):
        for obj,expected in ((u'a',True),(u'ab',True),('a',False),(u'',True),(None,False),(u'ㄱ',True),(u'가',True),(u'가자',True),(u'㐀',True),(u'𠀀',True)):
            result = cu.isUnicodeString(obj)
            self.assertEquals(result,expected)
            
    def test_conversions(self):
        for char,expected in ((u'a','U+0061'),('a','U+0061'),(u'ㄱ','U+3131'),(u'가','U+AC00'),(u'㐀','U+3400'),(u'𠀀','U+20000')):
            cp = cu.characterToCodepoint(char) # ord(char)
            self.assertTrue(cu.codePointExists(cp))
            char2 = cu.codePointToCharacter(cp)
            self.assertTrue(cu.isUnicodeChar(char2))
            self.assertEquals(char,char2)
            cpStr = cu.codePointToCodePointString(cp)
            self.assertEquals(cpStr,expected)
            cp2 = cu.codePointStringToCodePoint(cpStr)
            self.assertEquals(cp,cp2)
            char3 = cu.codePointStringToCharacter(cpStr)
            self.assertEquals(char3,char)
            
    def test_codePointExists(self):
        for cp,expected in ((0x3130,False),(0x3131,True),(0x4DB5,True),(0x4DB6,False)):
            result = cu.codePointExists(cp)
            self.assertEquals(result,expected)
            if expected:
                cu.codePointToCharacter(cp)
            else:
                self.assertRaises(Exception,cu.codePointToCharacter,cp)
                
    def test_codePointExist_nonBMP(self):
        for cp,expected in ((0x20000,True),(0x2A6D7,True)): # XXX succeeds with surrogate pairs - but it misses fact that second codepoint does not exist
            result = cu.codePointExists(cp)
            self.assertEquals(result,expected)
            if expected:
                cu.codePointToCharacter(cp)
            else:
                self.assertRaises(Exception,cu.codePointToCharacter,cp)
 
    def test_hanjaCodePointRangeName(self):
        for char,expected in ((u'a',None),(u'가',None),(u'一','BASE'),(u'㐀','EXTA'),(u'𠀀','EXTB'),(u'𠀀','EXTB')):
            cp = cu.characterToCodepoint(char)
            result = cu.hanjaCodePointRangeName(cp)
            self.assertEqual(result,expected,'Char %s cp 0x%x: expected %s actual %s' % (char,cp,str(expected),str(result)))
                       
    def test_isHanjaChar(self):
        for char,expected in ((u'a',False),(u'ab',False),(u'가',False),(u'一',True),(u'㐀',True),(u'𠀀',True),(u'大韓民國',False)):
            result = not not cu.isHanjaChar(char)
            self.assertEqual(result,expected,'Char %s cp 0x%x: expected %s actual %s' % (char,safeOrd(char),str(expected),str(result)))
            
    def test_len_nonBMP(self):
        for char,inBMP in ((u'㐀',True),(u'𠀀',False),):
            result = len(char)
            if inBMP or maxunicode > 0xFFFF:
                self.assertEquals(result,1) # single codepoint
            else:
                self.assertEquals(result,2) # pair of surrogate codepoints
          
            
def safeOrd(obj):
    try:
        return cu.characterToCodepoint(obj)
    except:
        return -1          
            


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()