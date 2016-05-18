koreanlangutils
===============
###A Python library for manipulating Korean language data

<br>

PURPOSE
-------
The purpose of this library is to facilitate manipulations of Korean language data at a character-by-character
level.  It focuses on Hangeul characters, both syllables (**음절 eumjeol**) and the consonant and vowel
letters (**자모 jamo**) that combine to make syllables, and limits support for other characters that can
occur in Korean text to identification of their types (currently ASCII and Chinese characters).  

It is not a Natural Language Processing (NLP) library, but can serve as a support library for an 
NLP library.  It should be especially useful in NLP processing that involves Korean morphology and 
morphophonology. By way of illustration, the library includes routines for adding particles and endings
to words and stems.  

LIMITATIONS
-----------
There are two limitations on the code this library that potential users should be aware of.

###Unicode

First, it expects unicode representation of the Hangeul characters, and cannot deal with other encodings
such as EUC-KR.  If you need to work with text in other encodings you must first convert them to unicode,
either UTF-8 or UTF-16 (BE or LE).

###Python 2.7
Second, the code currently targets Python 2.x (especially 2.7.x) and deals with characters in a Python 2.x way
with a clear distinction between **str** and **unicode** types.  The library may at some point be extended to 
Python 3.x, but Python 2.7 will continue to be supported.

INSTALLATION AND DEPENDENCIES
-----------------------------
This library does not depend on any other libraries nor does it include any C code that needs to be compiled.
All that needs to be done to install it is to copy it to an appropriate location.  There is no package structure.

koreancharutils.py
------------------

The core of the library is **koreancharutils.py**.  It contains a set of routines for manipulating 
Hangeul characters, including both syllables and jamo (constants and vowels). 

A key feature is full support for both combining jamo and compatibility jamo and conversions between the
two types.  

(Combining jamo participate in the algorithmic composition and decomposition of syllables and
fall into three separate codepoint ranges, syllable-initial consonants (**choseong**), syllable-medial vowels (**jungseong**), 
and syllable-final consonants (**jongseong**). Compatibility jamo are outside the algorithmic system and are
grouped in a single codepoint range in which consonants that can occur in both syllable-initial and
syllable-final position share a single codepoint.) 

In practice individual jamo are almost always represented in unicode documents as compatibility jamo. 
This is true in particular of computer language source files, as produced on a Korean OS or Western OS 
with an IME.

A common operation in source code is combining individual jamo into syllables, and very often the jamo in
question will be a mixture of combining jamo (obtained from the decomposition of a Hangeul syllable) and 
compatibility jamo (in a string literal or data item).  Conversions between the two jamo types are key
to coding this and similar operations. 

koreanmorphutils.py
-------------------

A second library component worth noting is **koreanmorphutils.py**.  Its focus is making the morphological 
changes that occur when a particle or ending is added to a word or stem.  

It covers only regular additions of particles to words (and thus does not deal with any of the irregular combinations
of pronouns and particles such as  **누구 nugu** + **이/가 i/ga** -> **누가 nuga**, **나 na** + **의 ui** -> **내 nae**, **거 geo** + **을/를 eul/reul** -> **걸 geol**, etc.).  

On the other hand it intends to be exhaustive in its coverage of adding endings to verbs and adjectives, including the
copula, and covers all stem types including minor and single-instance ones (**이르다 ireuda** 'arise' + 
**아~어 a~eo** -> **이르러 ireureo**, **푸다 puda** 'scoop' + **아~어 a~eo** -> **퍼 peo**, etc.).  

With a few special exceptions it operates on particles and endings based on their form and (very rarely)
their Part of Speech (POS), and can thus be used to add any particle or ending to any word or stem.

The code may or may not be useful for a given NLP application, but in any case it can serve as sample 
code that illustrates how the functions in **koreancharutils.py** can be used to do morphology-oriented manipulations.

koreanposutils.py
-----------------

While its name might suggest parity with the components already mentioned, **koreanposutils.py** is nothing
more than a shim layer for converting POS designators into ones that **koreanmorphutils.py** 
understands.  The inventory of POSes involved is currently very limited, but would
increase if **koreanmorphutils.py** were to be extended to deal with endings that take different forms for 
verbs and adjectives (for example verb **는다/ㄴ다 neunda/nda** vs. adjective **다 da**) - something it may do in the future.

charutils.py
------------


**charutils.py** contains a set of non-Korean-specific character functions.  The main thing to note about it is its
support for characters outside the Basic Multilingual Plane (BMP) which is to say, characters at codepoints > 0xFFFF.

The Python 2.x interpreter and builtins can be compiled to use either 16-bits or 32-bits for unicode 
characters.  If it is compiled to use 32-bits for unicode characters, characters outside the BMP can be 
represented directly. But if it is compiled to use 16-bits (as it is by default), it will have to represent 
characters outside the BMP with 16-bit escape sequences consisting of pairs of reserved codepoints called
**surrogates**.

For Korean text the only kind of character outside the BMP that is at all likely to occur (and the likelihood
is low) is a Chinese character in one of the non-BMP blocks that were added to successive versions of the Unicode
standard starting at version 3.1.  Users of this library can ignore the issue unless they encounter a problem - the
most likely being an exception resulting from an attempt to pass (what seems to be) a single non-BMP
character to the builtin **ord** (character to codepoint conversion) function, which expects a single character but
is being passed a two character string of surrogates. 

**charutils.py** contains a number of functions designed to facilite handling of surrogate pairs and reduce the need
to special-case them.  These include a number of special-purpose functions with **surrogatePair** in their names,
and the two general-purpose conversion functions **characterToCodepoint** and **codepointToCharacter** which work
with all characters including those represented by surrogates.  

The problem is that you have to use them to
benefit from them,and need to be constantly alert to the possibility of surrogate pairs in your data. If you
have to deal with non-BMP characters in a serious way you will probably do best to move to Python 3.4, which is
said to support non-BMP characters in a solid, transparent way.  (And it also presumably includes more non-BMP
Chinese character blocks than Python 2.7. See the comments to the function **hanjaCodePointRangeName** for details.) 

TESTS
-----

The library contains a set of standard-form Python unit tests.  Coverage is limited.  Moreover, most of the
tests involve iteration over lists of input and expected output data.  If they succeed, great.  If they fail, it
will be necessary to zero in on the specific input/expected set in the list and see what's going on.  A
simple first step is to move/copy the failing set to the top of the list.

The test for **koreanmorphutils.py** is more complicated.  It consists of two modules, a unit test module **test\_koreanmorphutils.py**
and a set of input/expected lists **test\_koreanmorphutils\_data.py** which is imported by the unit test module.
There is also a module, **write\_test\_koreanmorphutils\_data.py**, that will generate a new version of 
**test\_koreanmorphutils\_data.py**.  

You can add or subtract test cases for **koreanmorphutils.py** by modifying the input lists in
**write\_test\_koreanmorphutils\_data.py**.  (For example you can add another stem to the stems list and/or
add another ending to the endings list.)  When you run the program and generate a new **test\_koreanmorphutils\_data.py** 
the expected results will reflect what **koreanmorphutils.py** actually does, and if there are errors, the unit test
when rerun will be none the wiser.  

The recommended procedure is therefore:

1. Make sure the unit test passes with the pre-modified data.  
2. Add/subtract test cases.
3. Check that all the added test cases have correct expected results and, if they don't, edit the expected
results to be correct (knowing that running the unit test with the new data will fail). 
4. Run the test to verify that any tests that you expect to fail do fail.
5. Change the code being tested to do the right thing so the failing test cases will succeed.

DOCUMENTATION
-------------

As of now documentation of the library is limited to this README file and comments in the code.  More
systematic documentation will be added if/when there is demand for it.
   