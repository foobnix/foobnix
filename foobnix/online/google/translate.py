import re
import sys
import urllib
import simplejson

baseUrl = "http://ajax.googleapis.com/ajax/services/language/translate"

def getSplits(text,splitLength=4500):
    '''
    Translate Api has a limit on length of text(4500 characters) that can be translated at once, 
    '''
    return (text[index:index+splitLength] for index in xrange(0,len(text),splitLength))


def translate(text,src='en', to='ru'):    
    '''
    A Python Wrapper for Google AJAX Language API:
    * Uses Google Language Detection, in cases source language is not provided with the source text
    * Splits up text if it's longer then 4500 characters, as a limit put up by the API
    '''

    params = ({'langpair': '%s|%s' % (src, to),
             'v': '1.0'
             })
    retText=''
    for text in getSplits(text):
            params['q'] = text
            resp = simplejson.load(urllib.urlopen('%s' % (baseUrl), data = urllib.urlencode(params)))
            try:
                    retText += resp['responseData']['translatedText']
            except:
                    raise
    return retText
    