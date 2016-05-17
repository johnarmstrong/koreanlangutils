# -*- coding: utf-8 -*-
'''
Created on Feb 11, 2015

@author: John
'''
import sys
from collections import defaultdict
from charutils import hb_in_range,hb_in_ranges,isAsciiChar,isUnicodeChar,isUnicodeString,codePointToCodePointString,codePointToCharacter


#    Notes on identifier names:
#    o    jamo without qualification always means hangul combining jamo
#    o    hangul compatibility jamo are always referred to as compatibilityJamo
#    o    syllable means hangul syllable (combined LVT)
#    o    items likely to be used outside this module also have hangul in their names


# ==================================================================
#
#    Low-level codepoint-based constants and functions - see doc at end of file for source
#
# ==================================================================

#def hb_in_range (u, lo, hi):
#    return lo <= u <= hi

#def hb_in_ranges(u, lo1, hi1, lo2, hi2):
#    return hb_in_range (u, lo1, hi1) or hb_in_range (u, lo2, hi2)

#def hb_in_ranges3(u, lo1, hi1, lo2, hi2, lo3, hi3):
#    return hb_in_range (u, lo1, hi1) or hb_in_range (u, lo2, hi2) or hb_in_range (u, lo3, hi3)

# Constants - from Unicode 4.0 p. 87

LBase = 0x1100
VBase = 0x1161
TBase = 0x11A7
LCount = 19
VCount = 21
TCount = 28
SBase = 0xAC00

NCount = (VCount * TCount)
SCount = (LCount * NCount)

# Add JA - Compatibility Jamo
CBase = 0x3131
CCount = 0x3190 - CBase

def isCombiningL(u):
    return hb_in_range(u, LBase, LBase+LCount-1)

def isCombiningV(u):
    return hb_in_range(u, VBase, VBase+VCount-1)
 
def isCombiningT(u):
    return hb_in_range(u, TBase, TBase+TCount-1)

def isCombinedS(u):
    return hb_in_range(u, SBase, SBase+SCount-1)
 
def isL(u):
    return hb_in_ranges(u, LBase, LBase+LCount-1, 0xA960, 0xA97C)

def isV(u):
    return hb_in_ranges(u, LBase, VBase+VCount-1, 0xD7B0, 0xD7C6)
    
def isT(u):
    return hb_in_ranges(u, TBase, TBase+TCount-1, 0xD7CB, 0xD7FB)

# Add JA
def isC(u):
    return hb_in_range(u, CBase, CBase+CCount-1)

def isHangulTone(u):
    return hb_in_range(u, 0x302E, 0x302F)

# ==================================================================
#
#    General character and string predicates
#
# ==================================================================

def isHangulChar(obj):
    if not isUnicodeChar(obj):
        return False
    if isAsciiChar(obj): # Most likely non-hangul char type
        return False
    if isHangulSyllable(obj) or isHangulCompatibilityJamo(obj) or isHangulJamo(obj):
        return True
    return False

def isHangulString(obj): # not necessarily well-formed
    if not isUnicodeString(obj):
        return False    
    try:
        for char in obj:
            if not isHangulChar(char):
                return False
        return True
    except:
        return False

# ==================================================================
#
#    Hangul syllable predicates
#
# ==================================================================

def isHangulSyllable(obj):
    if not isUnicodeChar(obj):
        return False
    cp = ord(obj)
    return isCombinedS(cp)

# ==================================================================
#
#   Combining jamo predicates
#
# ==================================================================

def isHangulJamo(obj): # combining only
    return isHangulJamo_L(obj) or isHangulJamo_V(obj) or isHangulJamo_T(obj)

def isHangulJamo_L(obj):
    if not isUnicodeChar(obj):
        return False
    cp = ord(obj)
    return isL(cp)

def isHangulJamo_V(obj):
    if not isUnicodeChar(obj):
        return False
    cp = ord(obj)
    return isV(cp)

def isHangulJamo_T(obj):
    if not isUnicodeChar(obj):
        return False
    cp = ord(obj)
    return isT(cp)

# ==================================================================
#
#   Compatibility jamo predicates
#
# ==================================================================

def isHangulCompatibilityJamo(obj):
    if not isUnicodeChar(obj):
        return False
    cp = ord(obj)
    return isC(cp)

def isHangulCompatibilityJamo_L(obj):
    return isHangulJamoOrCompatibilityJamo_L(obj) and isHangulCompatibilityJamo()


def isHangulCompatibilityJamo_V(obj):
    return isHangulJamoOrCompatibilityJamo_V(obj) and isHangulCompatibilityJamo()

def isHangulCompatibilityJamo_T(obj):
    return isHangulJamoOrCompatibilityJamo_T(obj) and isHangulCompatibilityJamo()


# ==================================================================
#
#   Combining or compatibility jamo predicates
#
# ==================================================================

def isHangulJamoOrCompatibilityJamo(obj):
    return isHangulJamo(obj) or isHangulCompatibilityJamo(obj)

 
def isHangulJamoOrCompatibilityJamo_L(obj):
    try:
        ensureHangulJamo_L(obj)
        return True
    except:
        return False 

def isHangulJamoOrCompatibilityJamo_V(obj):
    try:
        ensureHangulJamo_V(obj)
        return True
    except:
        return False 

def isHangulJamoOrCompatibilityJamo_T(obj):
    try:
        ensureHangulJamo_T(obj)
        return True
    except:
        return False 


# ==================================================================
#
#    Empty L and T jamo predicates
#
# ==================================================================

emptyJamoCodePoint_L = 0x110B # syllable-initial 'ᄋ'
emptyJamo_L = codePointToCharacter(emptyJamoCodePoint_L)

def isEmptyHangulJamo_L(jamo):
    return ord(jamo) == emptyJamoCodePoint_L # syllable-initial 'ᄋ'

emptyJamoCodePoint_T = TBase # 0x11A7 # not a jamo, rather one before the first jamo
emptyJamo_T = None # may not work everywhere

def isEmptyHangulJamo_T(jamo):
    return jamo == None or ord(jamo) == emptyJamoCodePoint_T # not a jamo, rather one before the first jamo


# ==================================================================
#
#    Convert combining jamo to compatibility jamo
#
# ==================================================================

def hangulJamoToCompatibility_L(obj):
    if not isHangulJamo_L(obj):
        raise Exception('Not combining jamo L: ' + str(obj))
    return _hangulJamoToCompatibility_X(obj)

def hangulJamoToCompatibility_V(obj):
    if not isHangulJamo_V(obj):
        raise Exception('Not combining jamo V: ' + str(obj))
    return _hangulJamoToCompatibility_X(obj)

def hangulJamoToCompatibility_T(obj):
    if obj == None:
        return None
    if not isHangulJamo_T(obj):
        raise Exception('Not combining jamo T: ' + str(obj))
    return _hangulJamoToCompatibility_X(obj)

def hangulJamoToCompatibility_X(obj): # returns compatibility jamo (one of L,V,T, don't know which) or None 
    if obj == None:
        return None
    if not isHangulJamo(obj):
        raise Exception('Not combining jamo: ' + str(obj))
    return _hangulJamoToCompatibility_X(obj)

def _hangulJamoToCompatibility_X(obj):  # returns compatibility jamo or None - no arg check, for internal use 
    cp = ord(obj)
    data = getJamoDataForCodePoint(cp)
    if not data:
        return None
    cp_compat = data[idxCompat]
    return codePointToCharacter(cp_compat)

# ==================================================================
#
#    Convert compatibility jamo to combining jamo
#
# ==================================================================
    
def hangulCompatibilityJamoToJamo_L(obj):
    L,V,T = hangulCompatibilityJamoToJamo_LVT(obj)
    if not L:
        raise Exception('Cannot convert compatibility jamo %s to Jamo_L' % (obj,))
    return L

def hangulCompatibilityJamoToJamo_V(obj):
    L,V,T = hangulCompatibilityJamoToJamo_LVT(obj)
    if not V:
        raise Exception('Cannot convert compatibility jamo %s to Jamo_V' % (obj,))
    return V

def hangulCompatibilityJamoToJamo_T(obj): # will fail when passed None indicating no T
    L,V,T = hangulCompatibilityJamoToJamo_LVT(obj)
    if not T:
        raise Exception('Cannot convert compatibility jamo %s to Jamo_T' % (obj,))
    return T

def hangulCompatibilityJamoToJamo_LVT(obj): # return triple L,V,T - at most two can be non-None - in some cases L and T
    if not isHangulCompatibilityJamo(obj):
        raise Exception('Not compatibility jamo V: ' + str(obj))
    cp = ord(obj)
    data = getJamoDataForCodePoint(cp)
    if not data:
        return None
    cpL = data[idxL]
    cpV = data[idxV]
    cpT = data[idxT]
    L = codePointToCharacter(cpL) if cpL else None
    V = codePointToCharacter(cpV) if cpV else None
    T = codePointToCharacter(cpT) if cpT else None
    return (L,V,T)

# ==================================================================
#
#    Convert compatibility jamo to combining jamo if not one already
#
# ==================================================================                
            
def ensureHangulJamo_L(obj):
    if isHangulJamo_L(obj):
        return obj
    elif isHangulCompatibilityJamo(obj):
        return hangulCompatibilityJamoToJamo_L(obj)
    else:
        raise Exception('Cannot convert object to hangul combining jamo L: ' + obj)

def ensureHangulJamo_V(obj):
    if obj == None:
        return None
    if isHangulJamo_V(obj):
        return obj
    elif isHangulCompatibilityJamo(obj):
        return hangulCompatibilityJamoToJamo_V(obj)
    else:
        raise Exception('Cannot convert object to hangul combining jamo V: ' + obj)
    
def ensureHangulJamo_T(obj):
    if obj == None:
        return None
    if isHangulJamo_T(obj):
        return obj
    elif isHangulCompatibilityJamo(obj):
        return hangulCompatibilityJamoToJamo_T(obj)
    else:
        raise Exception('Cannot convert object to hangul combining jamo T: ' + obj)
    
# ==================================================================
#
#    Convert combining jamo to transliteration (2000 Revised Standard)
#
# ==================================================================

def hangulJamoToTrans_L(jamo):
    if not isHangulJamo_L(jamo):
        raise Exception('Not a Hangul L Jamo: ' + unicode(jamo))
    cpL = ord(jamo)
    return jamoTransList_L[cpL - LBase]

def hangulJamoToTrans_V(jamo):
    if not isHangulJamo_V(jamo):
        raise Exception('Not a Hangul V Jamo: ' + unicode(jamo))
    cpL = ord(jamo)
    return jamoTransList_V[cpL - VBase]

def hangulJamoToTrans_T(jamo):
    if not isHangulJamo_T(jamo):
        raise Exception('Not a Hangul T Jamo: ' + unicode(jamo))
    cpL = ord(jamo)
    return jamoTransList_T[cpL - TBase]

def hangulJamoToTrans(jamo):
    if jamo == None: # Assume empty T
        return ''
    if not isUnicodeChar(jamo):
        raise Exception('Not a unicode char: ' + unicode(jamo))
    cp = ord(jamo)
    if isL(cp):
        return jamoTransList_L[cp - LBase]
    elif isV(cp):
        return jamoTransList_V[cp - VBase]    
    elif isT(cp):
        return jamoTransList_T[cp - TBase]
    else:
        raise Exception('Not a Hangul Jamo: ' + codePointToCodePointString(cp) + ' ' +unicode(jamo))
              
# ==================================================================
#
#    Composing and decomposing Hangul syllables
#
# ==================================================================

def _hangulJamoToIndex_L(L):
    if not isHangulJamo_L(L):
        raise Exception('Char not combining Jamo L: ' + L)
    return ord(L) - LBase

def _hangulJamoToIndex_V(V):
    if not isHangulJamo_V(V):
        raise Exception('Char not combining Jamo V: ' + V)
    return ord(V) - VBase

def _hangulJamoToIndex_T(T):
    if T == None:
        return 0
    if not isHangulJamo_T(T):
        raise Exception('Jamo not combining Jamo T: ' + T) 
    return ord(T)- TBase
    

def composeHangulJamoToSyllable(L0,V0,T0=None):
    if not ((L0 == None or isUnicodeChar(L0)) and isUnicodeChar(V0) and (T0 == None or isUnicodeChar(T0))):
        raise Exception('Jamo not unicode characters: %s %s %s' % (L0,V0,T0 if T0 != None else str(T0))) 
    if L0 == None:
        L0 = emptyJamo_L                                                
    if isHangulCompatibilityJamo(L0):
        L = hangulCompatibilityJamoToJamo_L(L0)
    else:
        L = L0
    if isHangulCompatibilityJamo(V0):
        V = hangulCompatibilityJamoToJamo_V(V0)
    else:
        V = V0
    if T0 != None:
        if isHangulCompatibilityJamo(T0):
            T = hangulCompatibilityJamoToJamo_T(T0)
        else:
            T = T0
    else:
        T = None # or do we want empty T pseudo Jamo?
    
    LIndex = _hangulJamoToIndex_L(L)
    VIndex = _hangulJamoToIndex_V(V)
    TIndex = _hangulJamoToIndex_T(T)
    
    cpSyll = (LIndex * VCount + VIndex) * TCount + TIndex + SBase
    
    if not isCombinedS(cpSyll):
        raise Exception("Codepoint produced by composition not Hangul syllable: " + codePointToCodePointString(cpSyll))
    
    return codePointToCharacter(cpSyll)    

def decomposeHangulSyllableToJamo(syll):
    if not isHangulSyllable(syll):
        raise Exception('Not a Hangul syllable: ' + unicode(syll))
    cpS = ord(syll)
    SIndex = cpS - SBase
    cpL = LBase + SIndex // NCount
    cpV = VBase + (SIndex % NCount) // TCount
    cpT = TBase + SIndex % TCount
    if cpT == emptyJamoCodePoint_T:
        return (unichr(cpL),unichr(cpV),None)
    else:
        return (unichr(cpL),unichr(cpV),unichr(cpT))

def decomposeHangulSyllableToTrans(syll):
    L,V,T = decomposeHangulSyllableToJamo(syll)
    return hangulJamoToTrans(L),hangulJamoToTrans(V),hangulJamoToTrans(T)


# ==================================================================
#
#    Join Hangul sequences including mixed syllable and jamo sequences
#
# ==================================================================
    
def joinHangul(hangul1,hangul2):
    if not isUnicodeString(hangul1):
        raise Exception('Not a unicode string: ' + hangul1)
    if not isUnicodeString(hangul2):
        raise Exception('Not a unicode string: ' + hangul2)
    if not hangul1 or not hangul2: # one or both is empty string
        return hangul1 + hangul2
    
    hg1LastChar = hangul1[-1]
    hg2FirstChar = hangul2[0]
    
    if isHangulSyllable(hg1LastChar) and isHangulSyllable(hg2FirstChar):
        return hangul1 + hangul2;
    
    joinedSyll = joinHangulChars(hg1LastChar,hg2FirstChar)
    hg1Beg = hangul1[0:-1]
    hg2End = hangul2[1:]
    joined = hg1Beg + joinedSyll + hg2End
    return joined
    
def joinJamoSeparatedHangul(hangul1,jamo, hangul2):
    if hangul1 and not isUnicodeString(hangul1):
        raise Exception('Not a unicode string: ' + hangul1)
    if hangul2 and not isUnicodeString(hangul2):
        raise Exception('Not a unicode string: ' + hangul2)
    if not isUnicodeChar(jamo):
            raise Exception('Not a unicode char: ' + hangul2)
        
    if not hangul1 and not hangul2:
        raise Exception('Adjacent Hangul strings both empty')
    
    # First try to join jamo to preceding syll
    if hangul1:
        hg1LastChar = hangul1[-1]
        try:
            joinedSyll = joinHangulSyllableAndJamo(hg1LastChar,jamo)
            joinedHangul = hangul1[:-1] + joinedSyll
            if hangul2:
                joinedHangul += hangul2
            return joinedHangul
        except:
            pass # fall through
    
    # If can't to preceding hangul, try to join to following jangul
    if hangul2:
        hg2FirstChar = hangul2[0]
        try:
            joinedSyll = joinHangulJamoAndSyllable(jamo,hg2FirstChar)
            joinedHangul = joinedSyll + hangul2[1:]
            if hangul1:
                joinedHangul = hangul1 + joinedHangul
            return joinedHangul
        except:
            pass # fall through
        
    raise Exception('Can\'t join hangul sequence: %s %s %s' % (str(hangul1),str(jamo),str(hangul2)))


def joinHangulChars(hg1LastChar,hg2FirstChar):
    if not (isUnicodeChar(hg1LastChar) and isUnicodeChar(hg2FirstChar)):
        raise Exception('Not unicode chars: ' + hg1LastChar + ' ' + hg2FirstChar )
        
    if isHangulSyllable(hg1LastChar) and isHangulSyllable(hg2FirstChar):
        return hg1LastChar + hg2FirstChar
    if not isHangulSyllable(hg1LastChar) and not isHangulSyllable(hg2FirstChar):
        raise Exception('Cannot join two non-syllables: ' + hg1LastChar + ' ' + hg2FirstChar)
    if isHangulSyllable(hg1LastChar):
        return joinHangulSyllableAndJamo(hg1LastChar,hg2FirstChar)
    else:
        return joinHangulJamoAndSyllable(hg1LastChar,hg2FirstChar)
    
def joinHangulJamoAndSyllable(jamo,syll):
        try:
            L1 = ensureHangulJamo_L(jamo) 
        except:
            raise Exception('jamo is not L: ' + jamo)
        L2,V2,T2 = decomposeHangulSyllableToJamo(syll)
        if not isEmptyHangulJamo_L(L2):
            raise Exception('Syllable has non-empty L: ' + syll)
        syll = composeHangulJamoToSyllable(L1,V2,T2)
        return syll

def joinHangulSyllableAndJamo(syll,jamo):
    try:
        T2 = ensureHangulJamo_T(jamo) 
    except:
        raise Exception('jamo is not T: ' + jamo)
    L1,V1,T1 = decomposeHangulSyllableToJamo(syll)
    if T1 == None or isEmptyHangulJamo_T(T1):
        syll = composeHangulJamoToSyllable(L1,V1,T2)
    elif hangulJamoToCompatibility_T(T1) == u'ㄹ' and hangulJamoToCompatibility_T(T2) == u'ㅁ': 
        syll = composeHangulJamoToSyllable(L1,V1,u'ㄻ')
    else:
        raise Exception('syllable has non-empty T: ' + syll)
   
    return syll
  
def normalizeHangul(hangul):
    if not isUnicodeString(hangul):
        raise Exception('Not unicode string: ' + str(hangul))
    
    if not isHangulString(hangul):
        return hangul
    
    prev = ''
    rest = hangul
    while rest:
        for i,char in enumerate(rest):
            if isHangulJamoOrCompatibilityJamo(char):
                prev += rest[:i]
                if i+1 == len(rest):
                    if prev:
                        joined = joinJamoSeparatedHangul(prev[-1],char,None)
                        prev = prev[:-1] + joined
                    else:
                        joined = joinJamoSeparatedHangul(None,char,None) # will raise exception
                        prev = joined
                    rest = None
                else:
                    if prev:
                        joined = joinJamoSeparatedHangul(prev[-1],char,rest[i+1])
                        prev = prev[:-1] + joined
                    else:
                        joined = joinJamoSeparatedHangul(None,char,rest[i+1]) # will raise exception
                        prev = joined
                    if i + 2 < len(rest):
                        rest = rest[i+2:]
                    else:
                        rest = None
                break
        else:
            prev += rest[:i+1]
            rest = None
                
    return prev

    

# ==================================================================
#
#    Transliteration-related
#
# ==================================================================

# Following three functions write template for jamoTransLists, which then have to be pasted into this file and have the actual transliteration values filled in

def printTransList_L(out):  
    print >> out, '\njamoTransList_L = ['
    for i in xrange(LCount):
        print >> out, '\'\', #',i,codePointToCodePointString(LBase + i),unichr(LBase + i)
    print ']'
    
def printTransList_V(out):
    print >> out, '\njamoTransList_V = ['
    for i in xrange(VCount):
        print >> out, '\'\', #',i,codePointToCodePointString(VBase + i),unichr(VBase + i)
    print ']'
    
def printTransList_T(out):
    print >> out, '\njamoTransList_T = ['
    for i in xrange(TCount):
        print >> out, '\'\', #',i,codePointToCodePointString(TBase + i),unichr(TBase + i)
    print ']'
    

jamoTransList_L = [
'g', # 0 U+1100 ᄀ
'kk', # 1 U+1101 ᄁ
'n', # 2 U+1102 ᄂ
'd', # 3 U+1103 ᄃ
'tt', # 4 U+1104 ᄄ
'r', # 5 U+1105 ᄅ
'm', # 6 U+1106 ᄆ
'b', # 7 U+1107 ᄇ
'pp', # 8 U+1108 ᄈ
's', # 9 U+1109 ᄉ
'ss', # 10 U+110A ᄊ
'', # 11 U+110B ᄋ
'j', # 12 U+110C ᄌ
'jj', # 13 U+110D ᄍ
'ch', # 14 U+110E ᄎ
'k', # 15 U+110F ᄏ
't', # 16 U+1110 ᄐ
'p', # 17 U+1111 ᄑ
'h', # 18 U+1112 ᄒ
]

jamoTransList_V = [
'a', # 0 U+1161 ᅡ
'ae', # 1 U+1162 ᅢ
'ya', # 2 U+1163 ᅣ
'yae', # 3 U+1164 ᅤ
'eo', # 4 U+1165 ᅥ
'e', # 5 U+1166 ᅦ
'yeo', # 6 U+1167 ᅧ
'ye', # 7 U+1168 ᅨ
'o', # 8 U+1169 ᅩ
'wa', # 9 U+116A ᅪ
'wae', # 10 U+116B ᅫ
'oe', # 11 U+116C ᅬ
'yo', # 12 U+116D ᅭ
'u', # 13 U+116E ᅮ
'weo', # 14 U+116F ᅯ # standard is wo
'we', # 15 U+1170 ᅰ
'wi', # 16 U+1171 ᅱ
'yu', # 17 U+1172 ᅲ
'eu', # 18 U+1173 ᅳ
'eui', # 19 U+1174 ᅴ # standard is ui
'i', # 20 U+1175 ᅵ
]

jamoTransList_T = [
'', # 0 U+11A7 ᆧ# not an actual char, rather cp(ᆨ) - 1
'g', # 1 U+11A8 ᆨ
'kk', # 2 U+11A9 ᆩ
'gs', # 3 U+11AA ᆪ
'n', # 4 U+11AB ᆫ
'nj', # 5 U+11AC ᆬ
'nh', # 6 U+11AD ᆭ
'd', # 7 U+11AE ᆮ
'l', # 8 U+11AF ᆯ
'lg', # 9 U+11B0 ᆰ
'lm', # 10 U+11B1 ᆱ
'lb', # 11 U+11B2 ᆲ
'ls', # 12 U+11B3 ᆳ
'lt', # 13 U+11B4 ᆴ
'lp', # 14 U+11B5 ᆵ
'lh', # 15 U+11B6 ᆶ
'm', # 16 U+11B7 ᆷ
'b', # 17 U+11B8 ᆸ
'bs', # 18 U+11B9 ᆹ
's', # 19 U+11BA ᆺ
'ss', # 20 U+11BB ᆻ
'ng', # 21 U+11BC ᆼ
'j', # 22 U+11BD ᆽ
'ch', # 23 U+11BE ᆾ
'k', # 24 U+11BF ᆿ
't', # 25 U+11C0 ᇀ
'p', # 26 U+11C1 ᇁ
'h', # 27 U+11C2 ᇂ
] 

# ==================================================================
#
#    Misc hangul utils
#
# ==================================================================

def makeHangulReverse(hangul):
    if not isUnicodeString(hangul):
        raise Exception('Not unicode: ' + hangul)
    return hangul[::-1] # idiom

def getNextHangulPos(s0,startPos=0): # return (start,end,hangul) if found else None
    s = s0[startPos:] + ' '
    hgStartPos = -1
    for i in xrange(len(s)):
        c = s[i]
        if isHangulChar(c):
            if hgStartPos == -1:
                hgStartPos = i
        else:
            if hgStartPos != -1:
                # we were in hangul and now we're out
                break
            else:
                # we haven't gotten into hangul yet, just keep going
                pass
            
    if hgStartPos == -1:
        return (None,None,None)
    
    adjHgStartPos = hgStartPos + startPos
    adjHgEndPos = i + startPos
    hangul = s0[adjHgStartPos:adjHgEndPos]
    
    return (adjHgStartPos,adjHgEndPos,hangul) 

def getNextNonHangulAndHangulPoses(s0,startPos=0): # return (nonHgStartPos,nonHgEndPos,nonHangul,hgStartPos,hgEndPos,hangul)
    
    if startPos >= len(s0):
        return (None,None,None,None,None,None)
    # Otherwise return non-None nonHgStartPos,nonHgEndPos (may represent empty string) and either hgStartPos,hgEndPos (nonempty) or (None,None) - means we're done
    hgStartPos,hgEndPos,hangul = getNextHangulPos(s0,startPos)
    nonHgStartPos = startPos 
    if hgStartPos == None:
        # s0 is nonHangul only
        nonHgEndPos = len(s0)
    else:
        nonHgEndPos = hgStartPos
    nonHangul = s0[nonHgStartPos:nonHgEndPos]
    if not nonHangul and not hangul:
        return (None,None,None,None,None,None)
    return (nonHgStartPos,nonHgEndPos,nonHangul,hgStartPos,hgEndPos,hangul)
        
def getNonHangulAndHangulPairs(s): # return list of (nonHangul,hangul)
    if not s:
        return []
    pairs = []
    startPos = 0
    while startPos != None:
        if len(pairs) > 2000:
            raise Exception('Infinite loop')
        nonHgStartPos,nonHgEndPos,nonHangul,hgStartPos,hgEndPos,hangul = getNextNonHangulAndHangulPoses(s,startPos)
        if nonHgStartPos == None:
            break
        pairs.append((nonHangul,hangul))
        if hgEndPos == None:
            break
        startPos = hgEndPos
    return pairs

# ==================================================================
#
#    Code for making the jamo dataset that is used by jamo converson functions
#
# ==================================================================

idxName = 0
idxL = 1
idxV = 2
idxT = 3
idxCompat = 4

# NOTE 2016-01-26: currently this dataset is made into a single dict that is indexed by all jama codepoints combining and compatibility.
# This means the conversions between them always involve a lookup in the dictionary.  It could be made more efficient by breaking it into two lists,
# one indexed by compatibility jamo codepoints and one indexed by combining jamo codepoints.  The dict is small enough and python effiencent enough
# that this optimization by itself does not seem worth doing.

_JamoDataSet = (
    ('A', None, 0x1161, None, 0x314F),
    ('AE', None, 0x1162, None, 0x3150),
    ('ARAEA', None, 0x119E, None, 0x318D),
    ('ARAEAE', None, None, None, 0x318E),
    ('CHIEUCH', 0x110E, None, 0x11BE, 0x314A),
    ('CIEUC', 0x110C, None, 0x11BD, 0x3148),
    ('E', None, 0x1166, None, 0x3154),
    ('EO', None, 0x1165, None, 0x3153),
    ('EU', None, 0x1173, None, 0x3161),
    ('HIEUH', 0x1112, None, 0x11C2, 0x314E),
    ('I', None, 0x1175, None, 0x3163),
    ('IEUNG', 0x110B, None, 0x11BC, 0x3147),
    ('KAPYEOUNMIEUM', 0x111D, None, 0x11E2, 0x3171),
    ('KAPYEOUNPHIEUPH', 0x1157, None, 0x11F4, 0x3184),
    ('KAPYEOUNPIEUP', 0x112B, None, 0x11E6, 0x3178),
    ('KAPYEOUNSSANGPIEUP', 0x112C, None, None, 0x3179),
    ('KHIEUKH', 0x110F, None, 0x11BF, 0x314B),
    ('KIYEOK', 0x1100, None, 0x11A8, 0x3131),
    ('KIYEOK-SIOS', None, None, 0x11AA, 0x3133),
    ('MIEUM', 0x1106, None, 0x11B7, 0x3141),
    ('MIEUM-PANSIOS', None, None, 0x11DF, 0x3170),
    ('MIEUM-PIEUP', 0x111C, None, 0x11DC, 0x316E),
    ('MIEUM-SIOS', 0xA971, None, 0x11DD, 0x316F),
    ('NIEUN', 0x1102, None, 0x11AB, 0x3134),
    ('NIEUN-CIEUC', 0x115C, None, 0x11AC, 0x3135),
    ('NIEUN-HIEUH', 0x115D, None, 0x11AD, 0x3136),
    ('NIEUN-PANSIOS', None, None, 0x11C8, 0x3168),
    ('NIEUN-SIOS', 0x115B, None, 0x11C7, 0x3167),
    ('NIEUN-TIKEUT', 0x1115, None, 0x11C6, 0x3166),
    ('O', None, 0x1169, None, 0x3157),
    ('OE', None, 0x116C, None, 0x315A),
    ('PANSIOS', 0x1140, None, 0x11EB, 0x317F),
    ('PHIEUPH', 0x1111, None, 0x11C1, 0x314D),
    ('PIEUP', 0x1107, None, 0x11B8, 0x3142),
    ('PIEUP-CIEUC', 0x1127, None, 0xD7E8, 0x3176),
    ('PIEUP-KIYEOK', 0x111E, None, None, 0x3172),
    ('PIEUP-SIOS', 0x1121, None, 0x11B9, 0x3144),
    ('PIEUP-SIOS-KIYEOK', 0x1122, None, None, 0x3174),
    ('PIEUP-SIOS-TIKEUT', 0x1123, None, 0xD7E7, 0x3175),
    ('PIEUP-THIEUTH', 0x1129, None, None, 0x3177),
    ('PIEUP-TIKEUT', 0x1120, None, 0xD7E3, 0x3173),
    ('RIEUL', 0x1105, None, 0x11AF, 0x3139),
    ('RIEUL-HIEUH', 0x111A, None, 0x11B6, 0x3140),
    ('RIEUL-KIYEOK', 0xA964, None, 0x11B0, 0x313A),
    ('RIEUL-KIYEOK-SIOS', None, None, 0x11CC, 0x3169),
    ('RIEUL-MIEUM', 0xA968, None, 0x11B1, 0x313B),
    ('RIEUL-PANSIOS', None, None, 0x11D7, 0x316C),
    ('RIEUL-PHIEUPH', None, None, 0x11B5, 0x313F),
    ('RIEUL-PIEUP', 0xA969, None, 0x11B2, 0x313C),
    ('RIEUL-PIEUP-SIOS', None, None, 0x11D3, 0x316B),
    ('RIEUL-SIOS', 0xA96C, None, 0x11B3, 0x313D),
    ('RIEUL-THIEUTH', None, None, 0x11B4, 0x313E),
    ('RIEUL-TIKEUT', 0xA966, None, 0x11CE, 0x316A),
    ('RIEUL-YEORINHIEUH', None, None, 0x11D9, 0x316D),
    ('SIOS', 0x1109, None, 0x11BA, 0x3145),
    ('SIOS-CIEUC', 0x1136, None, 0xD7EF, 0x317E),
    ('SIOS-KIYEOK', 0x112D, None, 0x11E7, 0x317A),
    ('SIOS-NIEUN', 0x112E, None, None, 0x317B),
    ('SIOS-PIEUP', 0x1132, None, 0x11EA, 0x317D),
    ('SIOS-TIKEUT', 0x112F, None, 0x11E8, 0x317C),
    ('SSANGCIEUC', 0x110D, None, 0xD7F9, 0x3149),
    ('SSANGHIEUH', 0x1158, None, None, 0x3185),
    ('SSANGIEUNG', 0x1147, None, 0x11EE, 0x3180),
    ('SSANGKIYEOK', 0x1101, None, 0x11A9, 0x3132),
    ('SSANGNIEUN', 0x1114, None, 0x11FF, 0x3165),
    ('SSANGPIEUP', 0x1108, None, 0xD7E6, 0x3143),
    ('SSANGSIOS', 0x110A, None, 0x11BB, 0x3146),
    ('SSANGTIKEUT', 0x1104, None, 0xD7CD, 0x3138),
    ('THIEUTH', 0x1110, None, 0x11C0, 0x314C),
    ('TIKEUT', 0x1103, None, 0x11AE, 0x3137),
    ('U', None, 0x116E, None, 0x315C),
    ('WA', None, 0x116A, None, 0x3158),
    ('WAE', None, 0x116B, None, 0x3159),
    ('WE', None, 0x1170, None, 0x315E),
    ('WEO', None, 0x116F, None, 0x315D),
    ('WI', None, 0x1171, None, 0x315F),
    ('YA', None, 0x1163, None, 0x3151),
    ('YAE', None, 0x1164, None, 0x3152),
    ('YE', None, 0x1168, None, 0x3156),
    ('YEO', None, 0x1167, None, 0x3155),
    ('YEORINHIEUH', 0x1159, None, 0x11F9, 0x3186),
    ('YESIEUNG', 0x114C, None, 0x11F0, 0x3181),
    ('YESIEUNG-PANSIOS', None, None, 0x11F2, 0x3183),
    ('YESIEUNG-SIOS', None, None, 0x11F1, 0x3182),
    ('YI', None, 0x1174, None, 0x3162),
    ('YO', None, 0x116D, None, 0x315B),
    ('YO-I', None, 0x1188, None, 0x3189),
    ('YO-YA', None, 0x1184, None, 0x3187),
    ('YO-YAE', None, 0x1185, None, 0x3188),
    ('YU', None, 0x1172, None, 0x3160),
    ('YU-I', None, 0x1194, None, 0x318C),
    ('YU-YE', None, 0x1192, None, 0x318B),
    ('YU-YEO', None, 0x1191, None, 0x318A),
    None
)

def makeCodePointJamoDataDict(jamoDataSet):
    cpDataDict = {}
    for data in jamoDataSet:
        if data != None:
            for cp in data[1:]:
                if cp != None:
                    cpDataDict[cp] = data
    return cpDataDict

_codePointJamoDataDict = makeCodePointJamoDataDict(_JamoDataSet)

def getJamoDataForCodePoint(cp):
    return _codePointJamoDataDict.get(cp)

def makeJamoDataFromUnicodeData(unicodeDataFilename,out):
    lines = open(unicodeDataFilename,'r')
    nameDataDict = defaultdict(lambda: [None,None,None,None,None]) # L, V, T (either one of both of L and T or V), compat

    for line in lines:
        cpStr,cpName,junk = line.split(';',2)
        if not 'HANGUL' in cpName:
            continue
        cp = '0x' + cpStr
        name = cpName.rsplit()[-1]
        data = nameDataDict[name]
        if 'CHOSEONG' in cpName:
            data[idxL] = cp
            #print '\t'.join([cpStr,'CHOSEONG',name])
        if 'JUNGSEONG' in cpName:
            data[idxV] = cp
            #print '\t'.join([cpStr,'JUNGSEONG',name])
        if 'JONGSEONG' in cpName:
            data[idxT] = cp
            #print '\t'.join([cpStr,'JONGSEONG',name])
        if cpName.startswith('HANGUL LETTER'):
            data[idxCompat] = cp
            #print '\t'.join([cpStr,'COMPAT',name])
         
    print '_JamoData = ('
    for name in sorted(nameDataDict.keys()):
        data = nameDataDict[name]
        data[idxName] = name
        if data[idxCompat]:
            print '\t(\'%s\', %s),' %(data[0], ', '.join(str(val) for val in data[1:]))
            #print name,data
    print '\tNone\n)'
     

# ==================================================================
#
#    Main routine with test code
#
# ==================================================================
      
    
if __name__ == '__main__':
    def main():
        
        # Write data in py nested tuple format, which needs to be pasted into this file. Function returns None.
        # The file UnicodeData.txt resides in the UCD directory of the Unicode data distribution.  See http://unicode.org/reports/tr44/#UCD_Files
        # Unicode 6 version was used to make data in this file
        
        makeJamoDataFromUnicodeData('UnicodeData.txt',sys.stdout)
        
        # Write templates for transLists - transliterations will be '' and will need to be filled in with actual values
        printTransList_L(sys.stdout)
        printTransList_V(sys.stdout)
        printTransList_T(sys.stdout)
            
        for syllIndex in xrange(0,SCount,256):
            syllCP = SBase + syllIndex
            syll = unichr(syllCP)
            L,V,T = decomposeHangulSyllableToJamo(syll)
            print codePointToCodePointString(syllCP),syll,hangulJamoToTrans(L),hangulJamoToTrans(V),hangulJamoToTrans(T)
                

    main()
     
'''
[Following C++ code from HarfBuzz project which was included in qt-verywhere project and
https://github.com/ufal/unilib/blob/master/gen/template/uninorms.cpp - it's very simple]

97./* Constants for algorithmic hangul syllable [de]composition. */

template <typename T> static inline bool
0800 hb_in_range (T u, T lo, T hi)
0801 {
0802   if ( ((lo^hi) & lo) == 0 &&
0803        ((lo^hi) & hi) == (lo^hi) &&
0804        ((lo^hi) & ((lo^hi) + 1)) == 0 )
0805     return (u & ~(lo^hi)) == lo;
0806   else
0807     return lo <= u && u <= hi;
0808 }

0810 template <typename T> static inline bool
0811 hb_in_ranges (T u, T lo1, T hi1, T lo2, T hi2, T lo3, T hi3)
0812 {
0813   return hb_in_range (u, lo1, hi1) || hb_in_range (u, lo2, hi2) || hb_in_range (u, lo3, hi3);
0814 }
0815 


98.#define LBase 0x1100u
99.#define VBase 0x1161u
100.#define TBase 0x11A7u
101.#define LCount 19u
102.#define VCount 21u
103.#define TCount 28u
104.#define SBase 0xAC00u
105.#define NCount (VCount * TCount)
106.#define SCount (LCount * NCount)
107. 
108.#define isCombiningL(u) (hb_in_range ((u), LBase, LBase+LCount-1))
109.#define isCombiningV(u) (hb_in_range ((u), VBase, VBase+VCount-1))
110.#define isCombiningT(u) (hb_in_range ((u), TBase+1, TBase+TCount-1))
111.#define isCombinedS(u) (hb_in_range ((u), SBase, SBase+SCount-1))
112. 
113.#define isL(u) (hb_in_ranges ((u), 0x1100u, 0x115Fu, 0xA960u, 0xA97Cu))
114.#define isV(u) (hb_in_ranges ((u), 0x1160u, 0x11A7u, 0xD7B0u, 0xD7C6u))
115.#define isT(u) (hb_in_ranges ((u), 0x11A8u, 0x11FFu, 0xD7CBu, 0xD7FBu))
116. 
117.#define isHangulTone(u) (hb_in_range ((u), 0x302Eu, 0x302Fu))

'''

