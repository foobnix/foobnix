'''
Created on Oct 25, 2010

@author: ivan
'''
import logging
from foobnix.thirdparty.google.search import GoogleSearch
def google_search_results(query, results_count=10):
    results = []
    try:
        logging.debug("Start google search"+ query)
        ask = query.encode('utf-8')        
        gs = GoogleSearch(ask)
        gs.results_per_page = results_count
        returns = gs.get_results()
        for res in returns:
            result = res.title.encode('utf8')            
            results.append(str(result))
    except :
        logging.error("Google Search Result Error")
    return results
