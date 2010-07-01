'''
Created on 01.06.2010

@author: ivan
'''
from foobnix.online.google.search import GoogleSearch
import time
def googleHelp(query):
    print "Not Found, wait for results from google ..."
    results = []
    ask = query.encode('utf-8')
    print ask

    gs = GoogleSearch(ask, True, True)
    print gs
    gs.results_per_page = 10
    results = gs.get_results()
    print results
    for res in results:
        result = res.title.encode('utf8')
        time.sleep(0.05)
        results.append(str(result))
    
#print googleHelp("madoonna 1")
def search():
    print "Begin"
    gs = GoogleSearch("quick and dirty")
    gs.results_per_page = 5
    results = gs.get_results()
    print results
    for res in results:
        print res.title.encode("utf8")
        print res.desc.encode("utf8")
        print res.url.encode("utf8")

search()
        
        
