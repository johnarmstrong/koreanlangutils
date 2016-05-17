# -*- coding: utf-8 -*-
'''
Created on May 12, 2016

@author: John
'''

import koreanmorphutils as mu

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

header = '''# -*- coding: utf-8 -*-

# This is an automatically generated file that uses cvurrent code to make expected results.
# You can edit the file (especially to change incorrect to correct expected results)
# but if you do the edits will be lost when you regenerate the file and will
# have to be reapplied.  For this reason It is recommended that you regenerate the file only
# when you believe that all the results will be correct.  
'''


stems = [ # Full set of test stems
    (u'가',None),
    (u'하',None),
    (u'말하',None),
    (u'내',None),
    (u'건네',None),
    (u'서',None),
    (u'그러',None), # inf in -ae
    (u'켜',None),
    (u'크',None),
    (u'바쁘',None),
    (u'모으',None),
    (u'보',None),
    (u'주',None),
    (u'푸',None), # inf peo
    (u'비',None), # doesn't contract
    (u'치',None),
    (u'벌이',None),
    (u'보이',None),
    (u'쉬',None),
    (u'희',None),
    (u'되',None), # inf dwae doeeo
    
    (u'받',None),
    (u'먹',None),
    
    (u'살',None),
    (u'걸',None),
                
    (u'돕','irrb'),
    (u'고맙','irrb'),
    (u'눕','irrb'),
    (u'뵙','irrb2'),
    (u'뵙',None), # irrb2 will be inferred
    
    (u'낫','irrs'),
    (u'깃','irrs'),
    
    (u'캐닫','irrd'),
    (u'걷','irrd'),   
    
    (u'노랗','irrh'),
    (u'그렇','irrh'),
    
    (u'오르','irrlu'),
    (u'부르','irrlu'),
    
    (u'이르','irrle'),
    
    (u'사람','cop'),
    (u'의사','cop'),
    (u'것','cop'),
    (u'거','cop'),
    (u'아니','cop'),

    ]

endings = [ # full set of test endings
     (u'다',None),
     (u'니',None), # plain interrrogative 
     (u'으니',None), # = 으니까
     (u'세',None),  
     (u'으면',None),
     (u'음',None),
     
     (u'으러',None),
     (u'을지',None),
     (u'을',None),
    
     (u'습니다',u'ㅂ니다'),
     (u'소',u'오'),
     
     (u'아~어/E-conjunctive',None),
     (u'아서~어서/E-conjunctive',None),
     (u'아~어/E-s-ender',None),
     (u'아요~어요/E-s-ender',None),
     (u'았어요~었어요',None),
     
     (u'다/E-quote',None), # this and following are for testing cop - endings are adjective-specific and results of adding to vernbs are spurious
     (u'대/E-quote',None),
     (u'으냐고/E-quote',None), # for comparison, no special logic

     #(u'으변',u'으변'), # should be UNKNOWN
 ]

words = [
     u'말',
     u'닭',
     u'개',
 ]
        
   
particles = [
    (u'으로',None),
    (u'이랑',None),
    (u'도',None),
    (u'에게',None),
    (u'이',u'가'),
    (u'과',u'와'),
    (u'을',u'를'),

]


def write_header():
    print header

def write_test_getEndingAdderForStem_data():
    print '''
    
test_getEndingAdderForStem_data = [
    #(stem,irr,expectedEndingAdderName)'''
    for stem,irr in stems:
        endingAdderClass = mu.getEndingAdderForStem(stem,irr)
        endingAdderName = endingAdderClass().getName()
        print  "    (u'%s',%s,'%s')," % (stem,quotedOrNone(irr),endingAdderName)
    print '    ]\n'


def write_test_determineEndingType_data():
    print '''
    
test_determineEndingType_data = [
    #(postC,postV,expectedEndingType,expectedPostV)'''
    for postC,postV in endings:
        endingType,derivedPostV = mu.determineEndingType(postC,postV) # returns (endingType,postV)                    
        print "    (u'%s',%s,'%s',u'%s')," %(postC,quotedOrNoneUni(postV),endingType,derivedPostV)
    print '    ]\n'
    
def write_test_addParticle_data():
    print '''test_addParticle_data = [
    #(word,postC,postV,expectedWordPlusParticle)'''
    for word in words:
        for postC,postV in particles:
            wordPlusParticle = mu.addParticle(word,postC,postV)
            print "    (u'%s',u'%s',%s,u'%s')," %(word,postC,quotedOrNoneUni(postV),wordPlusParticle)
    print '    ]\n'
    
def write_test_makeInfinitive_data():
    print '''test_makeInfinitive_data = [
    #(stem,irr,inf,infMaxVariants)'''
    for stem,irr in stems:
        stemPlusInfEnding = mu.makeInfinitive(stem,irr,False)
        stemPlusInfEndingMaxVariants = mu.makeInfinitive(stem,irr,True)
        print "    (u'%s',%s,u'%s',u'%s')," % (stem,quotedOrNone(irr),stemPlusInfEnding,stemPlusInfEndingMaxVariants)
    print '    ]\n'

        
def write_test_addEnding_data():
    print '''test_addEnding_data = [
    #(stem,irr,postC,postV,expectedStemPlusEnding)'''
    for stem,irr in stems:
        print ''
        for postC,postV in endings: 
            stemPlusEnding = mu.addEnding(stem,irr,postC,postV)
            print "    (u'%s',%s,u'%s',%s,u'%s')," %(stem,quotedOrNone(irr),postC,quotedOrNoneUni(postV),stemPlusEnding)
    print '    ]\n'

if __name__ == "__main__":
    write_header()
    write_test_getEndingAdderForStem_data()
    write_test_determineEndingType_data()
    write_test_addParticle_data()
    write_test_makeInfinitive_data()
    write_test_addEnding_data()
    
    