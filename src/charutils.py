'''
Created on Jan 29, 2016

@author: John
'''

import unicodedata,codecs
from sys import maxunicode

# ==================================================================
#
#    Low-level codepoint-based constants and functions
#
# ==================================================================

# Following moved from koreancharutils, which see for source

def hb_in_range (u, lo, hi):
    return lo <= u <= hi

def hb_in_ranges(u, lo1, hi1, lo2, hi2):
    return hb_in_range (u, lo1, hi1) or hb_in_range (u, lo2, hi2)

def hb_in_ranges3(u, lo1, hi1, lo2, hi2, lo3, hi3):
    return hb_in_range (u, lo1, hi1) or hb_in_range (u, lo2, hi2) or hb_in_range (u, lo3, hi3)

# Following from Unicode FAQ http://www.unicode.org/faq//utf_bom.html
'''
// constants
const UTF32 LEAD_OFFSET = 0xD800 - (0x10000 >> 10);
const UTF32 SURROGATE_OFFSET = 0x10000 - (0xD800 << 10) - 0xDC00;

// computations
UTF16 lead = LEAD_OFFSET + (codepoint >> 10);
UTF16 trail = 0xDC00 + (codepoint & 0x3FF);

UTF32 codepoint = (lead << 10) + trail + SURROGATE_OFFSET;
'''

# constants
LEAD_OFFSET = 0xD800 - (0x10000 >> 10)
SURROGATE_OFFSET = 0x10000 - (0xD800 << 10) - 0xDC00

# computations
def lead(codepoint):
    return LEAD_OFFSET + (codepoint >> 10)

def trail(codepoint):
    return  0xDC00 + (codepoint & 0x3FF)

def codepoint32(lead,trail):
    return (lead << 10) + trail + SURROGATE_OFFSET


leadSurrogateLo = 0xD800 
leadSurrogateHi = 0xDBFF
trailingSurrogateLo = 0xDC00 
trailingSurrogateHi = 0xDFFF

# For codepoints - obtained by getting ord of individual chars of surrogate pair
def isLS(u):
    return hb_in_range(u,leadSurrogateLo,leadSurrogateHi)

def isTS(u):
    return hb_in_range(u,trailingSurrogateLo,trailingSurrogateHi)

def isS(u):
    return isLS(u) or isTS(u)

def isSurrogatePair(s):
    if not isUnicodeString(s):
        raise Exception('Not unicode string' + str(s))
    if len(s) != 2:
        return False
    cpLead = ord(s[0])
    cpTrail = ord(s[1])
    return (isLS(cpLead) and isTS(cpTrail))
    
# ==================================================================
#
#    surrogate pair detection and conversion functions
#
# ==================================================================

def surrogatePairToCodepoint(s):
    if not isSurrogatePair(s):
        raise Exception('Not surrogate pair: ' + str(s))
    cpLead = ord(s[0])
    cpTrail = ord(s[1])
    cp = codepoint32(cpLead,cpTrail)
    return cp

def codepointToSurrogatePair(cp32): # return as two-character string
    if cp32 < 0x10000:
        raise Exception('cp in BMP, not convertible to surrogate pair')
    cpLead = lead(cp32)
    cpTrail = trail(cp32)
    charLead = unichr(cpLead)
    charTrail = unichr(cpTrail)
    return charLead + charTrail

def findFirstSurrogatePair(s): # return offset of first surrogate pair of -1 for none
    if not isUnicodeString(s):
        raise Exception('Not unicode string')
    for i in xrange(len(s)):
        cpL = ord(s[i])
        if isLS(cpL):
            if i == len(s):
                raise Exception('Bad string: last char is lead surrogate: ' + s)
            cpT = ord(s[i+1])
            if not isTS(cpT):
                raise Exception('Bad string: s[%d] is lead surrogate but s[i+1] is not trailing surrogate: ' + s)
            return i
    
    return -1

def getSurrogatePairAtOffset(s,offset):
    if (0 <= offset < len(s) -1):
        charStr = s[offset:offset+2]
        if isSurrogatePair(charStr):
            return charStr
        
    raise Exception('Bad string or offset')
    

# ==================================================================
#
#    General purpose functions
#
# ==================================================================

def unicodeVersion():
    return unicodedata.unidata_version

def maxSupportedCodePoint():
    return maxunicode

def usesSurrogatePairs():
    return  maxSupportedCodePoint() < 0x10000

def isStrChar(obj):
    return isinstance(obj,str) and len(obj) == 1

def isAsciiChar(obj):
    try:
        return ord(obj) < 128
    except:
        return False
    
def isUnicodeString(obj):
    if not isinstance(obj,unicode):
        return False
    return True

def isUnicodeChar(obj):
    if not isinstance(obj,unicode):
        return False
    if len(obj) == 1:
        return True
    if isSurrogatePair(obj):
        return True
    return False

def codePointStringToCodePoint(cpStr):
    if (not cpStr.startswith('U+')):
        raise Exception('Only know how to convert strings of form U+xxxx: ' + str(cpStr))
    cpStr = cpStr[2:]
    cp = int(cpStr,16)
    return cp

def codePointToCodePointString(cp):
    cpStr = 'U+%04X' % (cp,)
    return cpStr

def codePointStringToCharacter(cpStr):
    cp = codePointStringToCodePoint(cpStr)
    return codePointToCharacter(cp)

def codePointInSupportedRange(cp):
    return (0 <= cp <= maxSupportedCodePoint())

def codePointExists(cp): 
    try:
        codePointToCharacter(cp)
        return True
    except Exception:
        return False

def characterToCodepoint(s): # wrapper for ord that can deal with surrogate pairs
    if isStrChar(s):
        return ord(s)
    if not isUnicodeChar(s): 
        raise Exception('Not str or unicode char: ' + str(s))
    try:
        return ord(s)
    except:
        return surrogatePairToCodepoint(s)    
               
def codePointToCharacter(cp):
    if cp <= maxSupportedCodePoint():
        char = unichr(cp)
        if cp > 0xFF: # unicodedata doesn't have names for control characters, so skip the name test on the ASCII ones at least
            try:
                unicodedata.name(char)
            except Exception,e:
                raise e
        return char
    else:
        #charStr = '\\U%08x' % cp
        #char = codecs.decode(charStr,'unicode-escape')
        char = codepointToSurrogatePair(cp)
        #unicodedata.name(char) # won't accept two character rep
        return char
        

def makePythonLiteralFromCodePoint(cp):
    pyLit = "u'\\x%04X'" % cp
    return pyLit

# ==================================================================
#
#    Chinese character functions
#
# ==================================================================

def hanjaCodePointRangeName(cp):
    if cp < 0x3400:
        return None
    
    if 0x4E00 <= cp <= 0x9FCC: # BMP
        return 'BASE' # CJK Unified Ideographs, Unicode 1.0 - Most hanja characters in modern Korean texts will be in this range
    
    if 0x3400 <= cp <= 0x4DBF:
        return 'EXTA' # CJK Unified Ideographs Extension A, added in Unicode 3.0
    if 0x20000 <= cp <= 0x2A6DF: # non-BMP
        return 'EXTB' # CJK Unified Ideographs Extension B, added in Unicode 3.1
    if 0x2A700 <= cp <= 0x2B73F: # non-BMP
        return 'EXTC' # CJK Unified Ideographs Extension C, added in Unicode 5.2
    if 0x2B740 <= cp <= 0x2B81F: # non-BMP
        return 'EXTD' # CJK Unified Ideographs Extension D, added in Unicode 6.0 (not included in Python 2.7)
    if 0x2B820 <= cp <= 0x2CEAF: # non-BMP
        return 'EXTE' # CJK Unified IdeographsExtension E, added in Unicode 8.0 (not included in Python 2.7)
    
    if 0xF900 <= cp <= 0xFAFF: # BMP
        return 'CMP' # CJK Compatibility Ideographs, # Unicode 1.0
    if 0x2F800 <= cp <= 0x2FA1F:  # non-BMP
        return 'CMPS' # CJK Compatibility Ideographs Supplement, added in Unicode 3.1
    
    return None

def isHanjaChar(obj):
    if not isUnicodeString(obj):
        return False
    if len(obj) == 1:
        cp = ord(obj)
    elif not isSurrogatePair(obj):
        return False
    else:
        cp = surrogatePairToCodepoint(obj)
    return hanjaCodePointRangeName(cp)
