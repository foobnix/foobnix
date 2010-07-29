'''
Created on 01.06.2010

@author: ivan
'''
from foobnix.online.google.search import GoogleSearch
import time
from foobnix.util import LOG
def googleHelp(query):
    LOG.info("Not Found, wait for results from google ...")
    results = []
    ask = query.encode('utf-8')
    LOG.info(ask)

    gs = GoogleSearch(ask, True, True)
    LOG.info(gs)
    gs.results_per_page = 10
    results = gs.get_results()
    LOG.info(results)
    for res in results:
        result = res.title.encode('utf8')
        time.sleep(0.05)
        results.append(str(result))
    
#LOG.info(googleHelp("madoonna 1")
def search():
    LOG.info("Begin")
    gs = GoogleSearch("quick and dirty")
    gs.results_per_page = 5
    results = gs.get_results()
    LOG.info(results)
    for res in results:
        LOG.info(res.title.encode("utf8"))
        LOG.info(res.desc.encode("utf8"))
        LOG.info(res.url.encode("utf8"))

search()
        
        
