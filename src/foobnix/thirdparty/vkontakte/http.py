#coding: utf-8
from __future__ import with_statement
from contextlib import closing
import httplib

# urllib2 doesn't support timeouts for python 2.5 so
# custom function is used for making http requests

def post(url, data, headers, timeout):
    host_port = url.split('/')[2]
    timeout_set = False
    try:
        connection = httplib.HTTPConnection(host_port, timeout = timeout)
        timeout_set = True
    except TypeError:
        connection = httplib.HTTPConnection(host_port)

    with closing(connection):
        if not timeout_set:
            connection.connect()
            connection.sock.settimeout(timeout)
            timeout_set = True

        connection.request("POST", url, data, headers)
        response = connection.getresponse()
        return (response.status, response.read())
