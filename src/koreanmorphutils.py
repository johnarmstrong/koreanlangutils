# -*- coding: utf-8 -*-
'''
Created on Jan 23, 2016

@author: John
'''

from collections import namedtuple

from koreancharutils import *
from koreanposutils import *

# For referring to specific combining jamo (used in decomposing and composing syllables)
# Note that all unicode u'<char>' jamo literals in source code are compatibility jamo (what Korean keyboard + IME naturally produces)

jamo_T_L = hangulCompatibilityJamoToJamo_T(u'ㄹ')
jamo_T_M = hangulCompatibilityJamoToJamo_T(u'ㅁ')

jamo_V_A = hangulCompatibilityJamoToJamo_V(u'ㅏ')
jamo_V_O = hangulCompatibilityJamoToJamo_V(u'ㅗ')
jamo_V_EO = hangulCompatibilityJamoToJamo_V(u'ㅓ')
jamo_V_E = hangulCompatibilityJamoToJamo_V(u'ㅔ')

jamo_V_YA = hangulCompatibilityJamoToJamo_V(u'ㅑ')
jamo_V_YO = hangulCompatibilityJamoToJamo_V(u'ㅛ')

jamo_V_WA = hangulCompatibilityJamoToJamo_V(u'ㅘ')

jamo_V_EU = hangulCompatibilityJamoToJamo_V(u'ㅡ')
jamo_V_I = hangulCompatibilityJamoToJamo_V(u'ㅣ')

jamo_L_D = hangulCompatibilityJamoToJamo_L(u'ㄷ')

def isAJamo(jamo):
    if not isHangulJamo(jamo):
        raise Exception('Not a combining jamo V:' + jamo)
    return jamo in (jamo_V_A,jamo_V_YA,jamo_V_WA)

def isOJamo(jamo):
    if not isHangulJamo(jamo):
        raise Exception('Not a combining jamo V:' + jamo)
    return jamo in (jamo_V_O,jamo_V_YO)

def isAOrOJamo(jamo):
    if not isHangulJamo(jamo):
        raise Exception('Not a combining jamo V:' + jamo)
    return jamo in (jamo_V_A,jamo_V_YA,jamo_V_WA,jamo_V_O,jamo_V_YO)

# ==============================================================
#
#                    Adding endings
#
# ==============================================================

ONE_SHAPE = 'ONE_SHAPE'
ONE_SHAPE_DROP_L = 'ONE_SHAPE_DROP_L'
TWO_SHAPE_REG = 'TWO_SHAPE_REG'
TWO_SHAPE_IRR = 'TWO_SHAPE_IRR'
INF_BASED = 'INF_BASED'
UNKNOWN = 'UNKNOWN'

def determineEndingType(postC,postVOrNone): # return (endingType,postV)
    postCFirstSyll_L,postCFirstSyll_V,_ = decomposeHangulSyllableToJamo(postC[0])
    
    if not isEmptyHangulJamo_L(postCFirstSyll_L): # starts with C - is either one-shape or irregular two-shape
        if not postVOrNone or postVOrNone == postC:
            postV = postC
            if hangulJamoToCompatibility_L(postCFirstSyll_L) in [u'ㄴ',u'ㅅ']:
                endingType = ONE_SHAPE_DROP_L
            else:
                endingType = ONE_SHAPE
        else:
            endingType = TWO_SHAPE_IRR
            postV = postVOrNone
    elif hangulJamoToCompatibility_V(postCFirstSyll_V) == u'ㅡ': # starts with eu - should be regular two-shape
        expectedPostV = removeInitialVIfPresent(postC)
        if not postVOrNone or postVOrNone == expectedPostV:
            endingType = TWO_SHAPE_REG
            postV = expectedPostV
        else:
            endingType = UNKNOWN
            postV = postVOrNone
    elif len(postC) > 2 and '~' in postC and hangulJamoToCompatibility_V(postCFirstSyll_V) == u'ㅏ': # starts with a- and contains ~ - assume inf-based
        if not postVOrNone or postVOrNone == postC:
            endingType = INF_BASED
            postV = postC
        else:
            endingType = UNKNOWN
            postV = postVOrNone
    else:
        endingType = UNKNOWN
        postV = postVOrNone
        
    return endingType,postV

def addEnding(stem,rawPos,rawPostCAndPos,rawPostVOrNone,maxVariants=False): # pos may be full pos or just irr
    basePos,irr = getBasePosAndIrr(rawPos)
    rawPostC,endingPos = getPostCAndEndingPos(rawPostCAndPos)
    endingAdderClass = getEndingAdderForStem(stem,irr)
    endingAdder = endingAdderClass()
    rawEndingType,rawPostV = determineEndingType(rawPostC,rawPostVOrNone)
    
    endingAdjustments = endingAdder.adjustEndings(stem,rawPos,rawPostC,rawPostV,endingPos,rawEndingType)
    stemPlusEndings = []
    for postC,postV,endingType in endingAdjustments:
        if endingType == ONE_SHAPE:
            stemPlusEndings.append(endingAdder.addOneShapeEnding(stem,rawPos,postC,False,endingPos))
        elif endingType == ONE_SHAPE_DROP_L:
            stemPlusEndings.append(endingAdder.addOneShapeEnding(stem,rawPos,postC,True,endingPos))
        elif endingType == TWO_SHAPE_REG:
            stemPlusEndings.append(endingAdder.addRegularTwoShapeEnding(stem,rawPos,postC,postV,endingPos))
        elif endingType == TWO_SHAPE_IRR:
            stemPlusEndings.append(endingAdder.addIrregularTwoShapeEnding(stem,rawPos,postC,postV,endingPos))
        elif endingType == INF_BASED:
            stemPlusEndings.append(endingAdder.addInfinitiveBasedEnding(stem,rawPos,postC,endingPos,maxVariants=maxVariants)) 
        else:
            raise Exception('Unknown ending type: ' + endingType)
        return ';'.join(stemPlusEndings)

def getPostCAndEndingPos(itemAndPos): # Delete when no longer used
    if '/' in itemAndPos:
        parts = itemAndPos.split('/')
        if len(parts) != 2:
            raise Exception('Bad itemAndPos: ' + itemAndPos)
        return parts[0],parts[1]
    else:
        return itemAndPos,None
    
def getBasePosAndIrr(rawPos):
    if not rawPos:
        return None,None
    
    normPos = normalizePredicatePos(rawPos)
    
    if rawPos.startswith('irr') or rawPos == 'cop': # no pos, just irr as in test cases
        return None,rawPos
    else:
        #basePos,_,_ = parsePos(rawPos,True) # parsePos not included in project
        basePos = rawPos
        if '.' in basePos:
            parts = basePos.split('.')
            if len(parts) != 2:
                raise Exception('Bad itemAndPos: ' + rawPos)
            return parts[0],parts[1]
        else:
            return basePos,None
    
# =====================================
# EndingAdder - base class
# =====================================

EndingAdjustment = namedtuple('NamedAdjustment','postC,postV,endingType')   
             
class EndingAdder(object):
    def __init__(self,
                 stemEndsInC,
                 modifyStemBeforeRegularTwoShapeEnding,
                 modifyStemBeforeIrregularTwoShapeEnding):
        self._stemEndsInC = stemEndsInC
        self.modifyStemBeforeRegularTwoShapeEnding = modifyStemBeforeRegularTwoShapeEnding
        self.modifyStemBeforeIrregularTwoShapeEnding = modifyStemBeforeIrregularTwoShapeEnding
        self.infAAfterA = True # True for all except irrb
        
    def getName(self):
        return self.__class__.__name__
        
    def stemEndsInC(self,stem):
        return self._stemEndsInC
        
    def adjustEndings(self,stem,stemPos,rawPostC,rawPostV,endingPos,rawEndingType):
        return [EndingAdjustment(rawPostC,rawPostV,rawEndingType)]
                
    def makePreTwoShapeStem(self,stem): # NB returns pair, modified stem and whether it should be treated as ending in a cons
        return (stem,self.stemEndsInC(stem))
    
    def makePreInfinitiveStem(self,stem): # return stem and whether it should be treated as ending in consonant (no contraction or deletio) same as postC from makePreTwoShapeEnding
        return self.makePreTwoShapeStem(stem)  # This def should do the right thing for most classes

    def addOneShapeEnding(self,stem,stemPos,postAll,dropL,endingPos):
        return stem + postAll
    
    def addTwoShapeEnding(self,stem,stemPos,postC,postV,modifyStem,endingPos):
        if self.stemEndsInC(stem):
            if modifyStem:
                modifiedStem,addPostC = self.makePreTwoShapeStem(stem)
                if addPostC:
                    return modifiedStem + postC
                else:
                    return normalizeHangul(modifiedStem + postV)
            else:
                return stem + postC
        else:
            return normalizeHangul(stem + postV)
 
    def addRegularTwoShapeEnding(self,stem,stemPos,postC,postV,endingPos):
        return self.addTwoShapeEnding(stem,stemPos,postC,postV,self.modifyStemBeforeRegularTwoShapeEnding,endingPos)
    
    def addIrregularTwoShapeEnding(self,stem,stemPos,postC,postV,endingPos):
        return self.addTwoShapeEnding(stem,stemPos,postC,postV,self.modifyStemBeforeIrregularTwoShapeEnding,endingPos)
        
    def addInfinitiveBasedEnding(self,stem,stemPos,ending,endingPos,maxVariants=False):
        aEnding,eoEnding = ending.split('~')
        if not maxVariants and ((aEnding == u'아' and endingPos== 'E-s-ender') or aEnding == u'아요'):
            preferContracted = True
        else:
            preferContracted = False
        
        preInfinitiveStem,addPostC = self.makePreInfinitiveStem(stem)
                
        stemFinalSyll =preInfinitiveStem[-1]
        stemFinalSyllJamo_L,stemFinalSyllJamo_V,_ = decomposeHangulSyllableToJamo(stemFinalSyll)
        stemFinalVowel = hangulJamoToCompatibility_V(stemFinalSyllJamo_V)
        
        if addPostC: # stem ends in consonant or behaves like it does (irrs)
            infEndings = self.chooseInfEndings(stemFinalSyllJamo_V,aEnding,eoEnding,maxVariants=maxVariants)
            stemPlusEndings = []
            for infEnding in infEndings:
                stemPlusEndings.append(preInfinitiveStem + infEnding)
            return joinForms(*stemPlusEndings) 
               
        elif stemFinalVowel == u'ㅡ' and len(preInfinitiveStem) >= 2: # stem is polysyllabic and ends in eu
            stemPrefinalSyll = preInfinitiveStem[-2]
            _,stemPrefinalSyllJamo_V,_ = decomposeHangulSyllableToJamo(stemPrefinalSyll)
            infEndings = self.chooseInfEndings(stemPrefinalSyllJamo_V,aEnding,eoEnding,maxVariants=maxVariants)
            stemPlusEndings = []
            for infEnding in infEndings:
                stemPlusEndings.append(normalizeHangul(preInfinitiveStem[:-1] + stemFinalSyllJamo_L + infEnding))
            return joinForms(*stemPlusEndings)
        
        elif stemFinalSyll == u'우' and len(preInfinitiveStem) >= 2: # polysyllabic stem ends in u with no syllable-initial consonant
            stemPrefinalSyll = preInfinitiveStem[-2]
            _,stemPrefinalSyllJamo_V,_ = decomposeHangulSyllableToJamo(stemPrefinalSyll)
            infEndings = self.chooseInfEndings(stemPrefinalSyllJamo_V,aEnding,eoEnding,maxVariants=maxVariants)
            stemPlusEndings = []
            for infEnding in infEndings:
                stemPlusEndings.append(contractVowelFinalStemAndAndInfinitiveBasedEnding(preInfinitiveStem,stemPos,infEnding,preferContracted,maxVariants=maxVariants))
            return joinForms(*stemPlusEndings)
        else: # stems ends in vowel other than eu or u with no leading consonant
            infEndings = self.chooseInfEndings(stemFinalSyllJamo_V,aEnding,eoEnding,maxVariants=maxVariants)
            stemPlusEndings = []
            for infEnding in infEndings:
                stemPlusEndings.append(contractVowelFinalStemAndAndInfinitiveBasedEnding(preInfinitiveStem,stemPos,infEnding,preferContracted,maxVariants=maxVariants))
            return joinForms(*stemPlusEndings)
    
    def chooseInfEndings(self,jamo_V,aEnding,eoEnding,maxVariants=False):
        if maxVariants and self.isAOrEoInfVowel(jamo_V):
            return (aEnding,eoEnding)
        elif self.isAInfVowel(jamo_V):
            return (aEnding,)
        else:
            return (eoEnding,)
    
    def isAInfVowel(self,jamo_V):
        if self.infAAfterA:
            return isAOrOJamo(jamo_V)
        else:
            return isOJamo(jamo_V)
    def isAOrEoInfVowel(self,jamo_V):
        return isAJamo(jamo_V)

            
def contractVowelFinalStemAndAndInfinitiveBasedEnding(stem,stemPos,ending,preferContracted,maxVariants=False): # Note a few rare verb types that are irregular only in inf-based forms are handled inline in this funcㅅion

    stemFinalSyll = stem[-1]
    stemFinalSyll_L,stemFinalSyll_V,stemFinalSyll_T = decomposeHangulSyllableToJamo(stemFinalSyll)
    if not isEmptyHangulJamo_T(stemFinalSyll_T):
        raise Exception('Stem not vowel-final: ' + stem)
    stemFinalVowel = hangulJamoToCompatibility_V(stemFinalSyll_V) 
    
    endingInitialSyll = ending[0]
    endingInitialSyll_L,endingInitialSyll_V,endingInitialSyll_T = decomposeHangulSyllableToJamo(endingInitialSyll)
    if not isEmptyHangulJamo_L(endingInitialSyll_L) or '~' in ending: # sanity check for bad args, not a full validation
        raise Exception('Bad infinitive ending: ' + ending)
    postVEnding = removeInitialVIfPresent(ending)
    
    if stemFinalSyll == u'하':      
        contractedStemPlusEnding = contract(stem,u'ㅐ',ending)
         
        irregUncontractedStemPlusEnding = contract(stem + u'여',u'ㅕ',ending) # trick to get what we want without decomposing anything

        if preferContracted:
            return contractedStemPlusEnding
        else:
            return joinForms(contractedStemPlusEnding,irregUncontractedStemPlusEnding)

    elif stemPos and 'irrh' in stemPos: # map be a pos with both mapped and kaist
        contractedStemPlusEnding = contract(stem,u'ㅐ',ending)
        
        return contractedStemPlusEnding
        
                
    elif stemFinalSyll == u'우':
        if endingInitialSyll_V == jamo_V_A:
            contractedJamo_V = u'ㅘ'
        elif endingInitialSyll_V == jamo_V_EO:
            contractedJamo_V = u'ㅝ'
        else:
            raise Exception('Unexpected vowel in infinitive ending: ' + ending)
        
        contractedStemPlusEnding = contract(stem,contractedJamo_V,ending)
        return contractedStemPlusEnding
    
    elif stemFinalVowel == u'ㅡ'  or stem == u'푸': # following code occurs multiple times, should refactor?
        contractedStemPlusEnding = contract(stem,endingInitialSyll_V,ending)
        return contractedStemPlusEnding
    
    elif stem.endswith('='): # irrh adjectives - inf in -ae, contracted only (?)
        contractedStemPlusEnding = contract(stem[:-1],u'ㅐ',ending)
        return contractedStemPlusEnding 
    
    elif stem in [u'어쩌',u'그러',u'이러','저러']: # verbs paired with iueeh adjectives - inf in -ae, contracted only (?)
        contractedStemPlusEnding = contract(stem,u'ㅐ',ending)
        return contractedStemPlusEnding 
         
    elif stemFinalVowel in [u'ㅏ',u'ㅔ',u'ㅓ',u'ㅕ']:
        return normalizeHangul(stem + postVEnding) # no uncontracted forms
    
    elif stemFinalVowel == u'ㅐ':
        contractedStemPlusEnding = normalizeHangul(stem + postVEnding)
        if preferContracted:
            return contractedStemPlusEnding
        else:
            return joinForms(contractedStemPlusEnding,stem + ending) # contracted forms normal but uncontracted occur (at least in compounds)
        
    elif stemFinalVowel in [u'ㅗ']: # contracted and uncontracted forms both occur
        contractedStemPlusEnding = contract(stem,u'ㅘ',ending)
        if preferContracted:
            return contractedStemPlusEnding
        else:
            return joinForms(contractedStemPlusEnding,stem + ending)
    
    elif stemFinalVowel == u'ㅣ' and stem != u'비': # contracted and uncontracted forms both occur
        contractedStemPlusEnding = contract(stem,u'ㅕ',ending)
        
        if len(stem) == 1 or maxVariants:
            return joinForms(contractedStemPlusEnding,stem + ending)
        else:
            return contractedStemPlusEnding # polysyllabic i stems seem to always contract - but are there exceptions for cpd verbs with final monosyllabic stem? 
             
    elif stemFinalVowel in [u'ㅜ']: # contracted and uncontracted forms both occur:
        contractedStemPlusEnding = contract(stem,u'ㅝ',ending)
        
        if (len(stem) == 1 and not preferContracted) or maxVariants:
            return joinForms(contractedStemPlusEnding,stem + ending)
        else:
            return contractedStemPlusEnding  
          
    elif stemFinalVowel in [u'ㅚ']: # contracted and uncontracted forms both occur:
        contractedStemPlusEnding = contract(stem,u'ㅙ',ending)
 
        if preferContracted:
            return contractedStemPlusEnding
        else:
            return joinForms(contractedStemPlusEnding,stem + ending)
                
    elif stemFinalVowel in [u'ㅟ',u'ㅢ',u'ㅣ']: # don't contract - note that most i stems will be handled above
        return stem + ending
    
    else:
        return stem + '+' + ending # placeholder 
    
def contract(stem,contractedJamo_V,ending):
    if len(stem) > 1:
        stemFinalSyll = stem[-1]
        stemBeforeFinalSyll = stem[:-1]
        stemFinalSyll_L,_,_ = decomposeHangulSyllableToJamo(stemFinalSyll)
    else:
        stemFinalSyll = stem
        stemBeforeFinalSyll = ''
        stemFinalSyll_L,_,_ = decomposeHangulSyllableToJamo(stemFinalSyll)

    endingInitialSyll = ending[0]
    _,_,endingInitialSyll_T = decomposeHangulSyllableToJamo(endingInitialSyll)

    contractedSyll = composeHangulJamoToSyllable(stemFinalSyll_L,contractedJamo_V,endingInitialSyll_T)

    endingAfterInitialSyll = ending[1:]
    contractedStemPlusEnding = stemBeforeFinalSyll + contractedSyll + endingAfterInitialSyll
    return contractedStemPlusEnding

def joinForms(*joinedForms):
    # remove possible duplicates without reordering
    dedupedForms = []
    for joinedForm in joinedForms:
        forms = joinedForm.split(',')
        for form in forms:
            if not form in dedupedForms:
                dedupedForms.append(form)
    return ','.join(dedupedForms)

# =====================================
# EndingAdder - copula - rawStem is noun or other item to add copula to, rawPostC,rawPostV are endings used for verbs and adjectives 
# =====================================

class CopulaEndingAdder(EndingAdder):
    def __init__(self):
        super(CopulaEndingAdder,self).__init__(None,False,False) # stemEndsInC,modifyStemBeforeRegularTwoShapeEnding,modifyStemBeforeIrregularTwoShapeEnding
        
    def stemEndsInC(self,stem):
        stemFinalSyll = stem[-1]
        _,_,stemFinalSyll_T = decomposeHangulSyllableToJamo(stemFinalSyll)
        return stemFinalSyll_T != None
     
    def adjustEndings(self,stem,stemPos,rawPostC,rawPostV,rawEndingPos,rawEndingType):
        endingPos = normalizeEndingPos(rawEndingPos)
        endingAdjustments = []
        if rawEndingType == ONE_SHAPE:
            if endingPos == 'E-quote':
                endingInitialSyll = rawPostC[0]
                endingInitialSyll_L,endingInitialSyll_V,endingInitialSyll_T = decomposeHangulSyllableToJamo(endingInitialSyll)
                if endingInitialSyll_L == jamo_L_D:
                    postCFirstSyll = composeHangulJamoToSyllable(u'ㄹ',endingInitialSyll_V,endingInitialSyll_T)
                    postC = postCFirstSyll + rawPostC[1:]
                else:
                    postC = rawPostC
            else:
                postC = rawPostC
            endingAdjustments.append(EndingAdjustment(normalizeHangul(u'이' + postC),postC,TWO_SHAPE_REG))
        elif rawEndingType == TWO_SHAPE_IRR and rawPostC.startswith(u'습'):
            if stem in [u'아니',u'거']:
                postC = normalizeHangul(u'이' + rawPostV)
                postV = rawPostV
                endingAdjustments.append(EndingAdjustment(postC,postV,TWO_SHAPE_REG))
            else:
                postAll = normalizeHangul(u'이' + rawPostV)
                endingAdjustments.append(EndingAdjustment(postAll,postAll,ONE_SHAPE))
        elif rawEndingType in [TWO_SHAPE_REG,ONE_SHAPE_DROP_L,TWO_SHAPE_IRR]:
            endingAdjustments.append(EndingAdjustment(normalizeHangul(u'이' + rawPostV),rawPostV,TWO_SHAPE_REG))
        elif rawEndingType == INF_BASED:
            # postC - i + eo form
            rawPostAll_EO = rawPostC.split('~')[1]
            rawPostAll_EO_rest = rawPostAll_EO[1:]
            includeRegular = True
            if endingPos == 'E-s-ender':
                if rawPostAll_EO == u'어': # non-polite s-ender
                    postC = u'이야'
                    postV = u'야'    
                elif rawPostAll_EO == u'어요': # non-polite s-ender
                    postC = u'이에요'
                    postV = u'예요'
                includeRegular = False
                endingAdjustments.append(EndingAdjustment(postC,postV,TWO_SHAPE_REG))
            elif endingPos == 'E-conjunctive': 
                postC = u'이라' + rawPostAll_EO[1:]
                postV = u'라' + rawPostAll_EO[1:]
                includeRegular = True
                endingAdjustments.append(EndingAdjustment(postC,postV,TWO_SHAPE_REG))
               
            if includeRegular: 
                # postC - i + eo form  
                postC = normalizeHangul(u'이' + rawPostAll_EO)
                # postV - eo form with eo changed to yeo
                rawPostAllFirstSyll = rawPostAll_EO[0]
                rawPostAllFirstSyll_L,rawPostAllFirstSyll_V,rawPostAllFirstSyll_T = decomposeHangulSyllableToJamo(rawPostAllFirstSyll)
                postVFirstSyll = composeHangulJamoToSyllable(rawPostAllFirstSyll_L,u'ㅕ',rawPostAllFirstSyll_T)                
                postV = postVFirstSyll + rawPostAll_EO_rest
                endingAdjustments.append(EndingAdjustment(postC,postV,TWO_SHAPE_REG))     
        else:
            endingAdjustments.append(EndingAdjustment(rawPostC,rawPostV,rawEndingType)) # XXX need to deal with other ending types (?)
        
        return endingAdjustments   

                  
# =====================================
# EndingAdder - regular verb classes
# =====================================
                
class RegVEndingAdder(EndingAdder):
    def __init__(self):
        super(RegVEndingAdder,self).__init__(False,False,False) # stemEndsInC,modifyStemBeforeRegularTwoShapeEnding,modifyStemBeforeIrregularTwoShapeEnding
        
        
class RegCEndingAdder(EndingAdder):
    def __init__(self):
        super(RegCEndingAdder,self).__init__(True,False,False) # stemEndsInC,modifyStemBeforeRegularTwoShapeEnding,modifyStemBeforeIrregularTwoShapeEnding
        

class RegLEndingAdder(EndingAdder):
    def __init__(self):
        super(RegLEndingAdder,self).__init__(True,'N/A',True) # stemEndsInC,modifyStemBeforeRegularTwoShapeEnding,modifyStemBeforeIrregularTwoShapeEnding

    def addOneShapeEnding(self,stem,stemPos,postAll,dropL,endingPos):
        if dropL:
            stemLessL = removeFinalCIfPresent(stem)
            return stemLessL + postAll
        else:
            return stem + postAll
    
    def addRegularTwoShapeEnding(self,stem,stemPos,postC,postV,endingPos): # deal with special treatment before L and M
        endingInitialJamo,isConsonant = getInitialCompatibilityJamo(postV)
        if not isConsonant:
            raise Exception('Unexpected: regular two shape postV ending does not begin with consonant: ' + postV)
        
        if endingInitialJamo == u'ㅁ' or (endingInitialJamo == u'ㄹ' and isHangulSyllable(postV[0])):
            return normalizeHangul(stem + postV)
        else:
            modifiedStem = removeFinalCIfPresent(stem)
            return normalizeHangul(modifiedStem + postV)


    def makePreTwoShapeStem(self,stem):
        modifiedStem = removeFinalCIfPresent(stem)
        return modifiedStem,False
    
    def makePreInfinitiveStem(self,stem):
        return stem,True # keep l for infinitive

# =====================================
# EndingAdder - irrregular verb classes
# =====================================
                
class IrrBEndingAdder(EndingAdder):
    def __init__(self):
        super(IrrBEndingAdder,self).__init__(True,True,False) # stemEndsInC,modifyStemBeforeRegularTwoShapeEnding,modifyStemBeforeIrregularTwoShapeEnding
        self.infAAfterA = False
        
    def makePreTwoShapeStem(self,stem): 
        modifiedStem = removeFinalCIfPresent(stem)
        modifiedStem += u'우'
        return modifiedStem,False # False -> add postV instead of postC

class IrrB2EndingAdder(EndingAdder): # for boeptta
    def __init__(self):
        super(IrrB2EndingAdder,self).__init__(True,True,False) # stemEndsInC,modifyStemBeforeRegularTwoShapeEnding,modifyStemBeforeIrregularTwoShapeEnding
        
    def makePreTwoShapeStem(self,stem): 
        modifiedStem = removeFinalCIfPresent(stem)
        return modifiedStem,False # False -> add postV instead of postC


class IrrDEndingAdder(EndingAdder):
    def __init__(self):
        super(IrrDEndingAdder,self).__init__(True,True,False) # stemEndsInC,modifyStemBeforeRegularTwoShapeEnding,modifyStemBeforeIrregularTwoShapeEnding
    
    def makePreTwoShapeStem(self,stem): 
        lastSyll_L,lastSyll_V,lastSyll_T = decomposeHangulSyllableToJamo(stem[-1])
        modifiedLastSyll = composeHangulJamoToSyllable(lastSyll_L,lastSyll_V,jamo_T_L)
        modifiedStem = stem[:-1] + modifiedLastSyll
        return modifiedStem,True

    
class IrrHEndingAdder(EndingAdder): # Adjectives only
    def __init__(self):
        super(IrrHEndingAdder,self).__init__(True,True,False) # stemEndsInC,modifyStemBeforeRegularTwoShapeEnding,modifyStemBeforeIrregularTwoShapeEnding
        
    def makePreTwoShapeStem(self,stem):
        modifiedStem = removeFinalCIfPresent(stem)
        return modifiedStem,False
        
class IrrLUEndingAdder(EndingAdder):
    def __init__(self):
        super(IrrLUEndingAdder,self).__init__(False,False,False) # stemEndsInC,modifyStemBeforeRegularTwoShapeEnding,modifyStemBeforeIrregularTwoShapeEnding
        
    def makePreInfinitiveStem(self,stem): # TODO remove eu and add leu
        if stem[-1] != u'르' or len(stem) < 2:
            raise Exception('Bad irrlu stem: ' + stem)
        nextToLastSyll = stem[-2]
        nextToLastSyll_L,nextToLastSyll_V,nextToLastSyll_T = decomposeHangulSyllableToJamo(nextToLastSyll)
        if nextToLastSyll_T:
            raise Exception('Bad irrlu stem: ' + stem)
        
        nextToLastSyllPlusL = composeHangulJamoToSyllable(nextToLastSyll_L,nextToLastSyll_V,jamo_T_L)
        preInfinitiveStem = stem[:-2] + nextToLastSyllPlusL + u'르'
        return preInfinitiveStem,False


class IrrLEEndingAdder(EndingAdder):
    def __init__(self):
        super(IrrLEEndingAdder,self).__init__(False,False,False) # stemEndsInC,modifyStemBeforeRegularTwoShapeEnding,modifyStemBeforeIrregularTwoShapeEnding
        
    def makePreInfinitiveStem(self,stem):
        if stem[-1] != u'르':
            raise Exception('Bad irrlu stem: ' + stem)

        return stem + u'르',False

class IrrSEndingAdder(EndingAdder):
    def __init__(self):
        super(IrrSEndingAdder,self).__init__(True,True,False) # stemEndsInC,modifyStemBeforeRegularTwoShapeEnding,modifyStemBeforeIrregularTwoShapeEnding

    def makePreTwoShapeStem(self,stem):
        modifiedStem = removeFinalCIfPresent(stem)
        return modifiedStem,True

# =====================================
# Helper functions
# =====================================


_irrEndingAdderDict = {
    'irrb' : IrrBEndingAdder,
    'irrb2' : IrrB2EndingAdder,
    'irrs' : IrrSEndingAdder,
    'irrd' : IrrDEndingAdder,
    'irrh' : IrrHEndingAdder,
    'irrlu' : IrrLUEndingAdder,
    'irrle' : IrrLEEndingAdder,
    'cop' : CopulaEndingAdder
    }

def getEndingAdderForStem(stem,irr):
    if not irr and stem == u'뵙':
        irr = 'irrb2'
    if irr: # get adder from irr dict
        endingAdder = _irrEndingAdderDict[irr.lower()] # raise exception if not in dict
    else:  # choose reg adder based on stem
        lastSyll = stem[-1]
        lastSyll_L,lastSyll_V,lastSyll_T = decomposeHangulSyllableToJamo(lastSyll)
        if not lastSyll_T:
            endingAdder = RegVEndingAdder 
        elif lastSyll_T == jamo_T_L:
            endingAdder = RegLEndingAdder
        else:
            endingAdder = RegCEndingAdder
    return endingAdder 

# ==============================================================
#
#                    Special-purpose add ending functions
#
# ==============================================================

def makeInfinitive(stemAndPos,irr,maxVariants=False):
    return addEnding(stemAndPos,irr,u'아~어',None,maxVariants=maxVariants)
     
# ==============================================================
#
#                    Adding particles
#
# ==============================================================


def addParticle(word,postC,postV): # TODO - rename to addParticle, remove ending-specific args and logic
    lastSyll = word[-1]
    _,_,lastSyll_T = decomposeHangulSyllableToJamo(lastSyll)
    if not postV:
        postV = removeInitialVIfPresent(postC,vowelsToRemove=[jamo_V_EU,jamo_V_I])
        
    if not lastSyll_T: # word ends in vowel
        return normalizeHangul(word + postV)
    elif  lastSyll_T == jamo_T_L: # word ends in consonant L
        isRegularTwoShapeEnding = (postC == u'으' + postV)
        if isRegularTwoShapeEnding:
            postCInitialJamo,_ = getInitialCompatibilityJamo(postC)
            postVInitialJamo,_= getInitialCompatibilityJamo(postV)
            if postCInitialJamo == u'ㅡ' and postVInitialJamo == u'ㄹ':
                return normalizeHangul(word + postV)
            else:
                return word + postC
        else:
            return word + postC
            
    else: # word ends in consonant other than L
        return word + postC


# ==============================================================
#
#                    General helper functions
#
# ==============================================================
    
            
def removeFinalCIfPresent(stem,consonantsToRemove=None): # optional arg is list of combining jamo_Ls
    lastSyll = stem[-1]
    lastSyll_L,lastSyll_V,lastSyll_T = decomposeHangulSyllableToJamo(lastSyll)
    if not lastSyll_T or (consonantsToRemove and not lastSyll_T in consonantsToRemove): # XXX needs testing
        return stem
    else:
        return stem[:-1] + composeHangulJamoToSyllable(lastSyll_L,lastSyll_V)
       
def removeInitialVIfPresent(clitic,vowelsToRemove=None): # optional arg is list of combining jamo_Vs
    firstSyllOrJamo = clitic[0]
    if isHangulSyllable(firstSyllOrJamo):
        firstSyll_L,firstSyll_V,firstSyll_T = decomposeHangulSyllableToJamo(firstSyllOrJamo)
        if isEmptyHangulJamo_L(firstSyll_L) and (vowelsToRemove == None or firstSyll_V in vowelsToRemove): # starts with vowel - either V or VT
            if firstSyll_T:
                return hangulJamoToCompatibility_T(firstSyll_T) + clitic[1:]
            else:
                return clitic[1:]  
        else: # starts with consonant - return as is
            return clitic
    else:
        if isHangulJamoOrCompatibilityJamo_L(firstSyllOrJamo) or isHangulJamoOrCompatibilityJamo_T(firstSyllOrJamo): # most likely T but L is possible (single cons endings are ambiguous)
            return clitic
        elif isHangulJamoOrCompatibilityJamo_V(firstSyllOrJamo):  # unlikely but possible
            return clitic[1:]
        else:
            raise Exception('Clitic does not begin with hangul syllable or jamo: ' + clitic)

def getInitialCompatibilityJamo(hangul): # returns jamo,isConsonant
    initialChar = hangul[0]
    if isHangulSyllable(initialChar):
        initialSyll_L,initialSyll_V,_ = decomposeHangulSyllableToJamo(initialChar)
        if not isEmptyHangulJamo_L(initialSyll_L):
            return hangulJamoToCompatibility_X(initialSyll_L),True
        else:
            return hangulJamoToCompatibility_X(initialSyll_V),False
    elif isHangulCompatibilityJamo(initialChar):
        if isHangulJamoOrCompatibilityJamo_V(initialChar):
            return initialChar,False
        else:
            return initialChar,True
    elif isHangulJamoOrCompatibilityJamo_L(initialChar) or isHangulJamoOrCompatibilityJamo_T(initialChar):
        return hangulJamoToCompatibility_X(initialChar),True
    elif isHangulJamoOrCompatibilityJamo_V(initialChar):
        return hangulJamoToCompatibility_X(initialChar),False
    else:
        raise Exception('String ending does not start with hangul character: ' + hangul)
    
   

# ==============================================================
#
#                    Main routine (for testing)
#
# ==============================================================


if __name__ == '__main__':
    def main():
        pass
    
    main()
