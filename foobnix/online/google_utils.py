'''
Created on Jun 10, 2010

@author: ivan
'''
from foobnix.online.google.search import GoogleSearch
from foobnix.util import LOG
"""Get search result titles from google"""
def google_search_resutls(query, results_count=10):
    results = []
    try:
        LOG.debug("Start google search", query)
        ask = query.encode('utf-8')        
        gs = GoogleSearch(ask)
        gs.results_per_page = results_count
        returns = gs.get_results()
        for res in returns:
            result = res.title.encode('utf8')            
            results.append(str(result))
    except :
        LOG.error("Google Search Result Error")
    return results