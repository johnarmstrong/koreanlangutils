# -*- coding: utf-8 -*-
'''
Created on May 14, 2016

@author: John
'''

# This module is a shim between the koreanlangutils library and whatever POS system you are using

# normalizePredicatePos - Currently used only to get irr for determining how to add endings to predicate (verb, adjective or copula)
#
# Should return one of:
#    <pos>.<irr>
#    pos
#    irr
#    None of empty string
#
# pos can be anything (it's currently not used)
#
# irr must be one of the items in the following dict defined in koreanmorphutils.py:
#
#_irrEndingAdderDict = {
#    'irrb' : IrrBEndingAdder,
#    'irrb2' : IrrB2EndingAdder,
#    'irrs' : IrrSEndingAdder,
#    'irrd' : IrrDEndingAdder,
#    'irrh' : IrrHEndingAdder,
#    'irrlu' : IrrLUEndingAdder,
#    'irrle' : IrrLEEndingAdder,
#    'cop' : CopulaEndingAdder
#    }

def normalizePredicatePos(rawPos):
    return rawPos

# normalizePredicatePos - Currently used to distinguish homonymous endings which differ in how they are added to some stems (particulatly the copula)
# 
# The endings involved, in their normalized form, are the following:
#
#    E-s-ender - 아~어 intimate sentence-ender, 다 plain adjective sentence-ender
#    E-conjunctive - 아~어 infinitive
#    E-quote - 다 quotation form

def normalizeEndingPos(rawPos):
    if rawPos in ('E-s-ender',):
        return 'E-s-ender'
    if rawPos in ('E-conjunctive',):
        return 'E-conjunctive'
    if rawPos in ('E-quote',):
        return 'E-quote'
  
    return rawPos



if __name__ == '__main__':
    pass