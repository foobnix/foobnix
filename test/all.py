#-*- coding: utf-8 -*-
'''
Created on 20 нояб. 2010

@author: ivan
'''
import glob
import unittest

def run_all_tests(ignore="@"):
    test_file_strings = glob.glob('test/test_*.py')
    if not test_file_strings:
        test_file_strings = glob.glob('test_*.py')
    module_strings = [str[0:len(str) - 3].replace("/", ".") for str in test_file_strings if ignore not in str]
    suites = [unittest.defaultTestLoader.loadTestsFromName(str) for str
              in module_strings]
    testSuite = unittest.TestSuite(suites)
    result = unittest.TextTestRunner().run(testSuite)
    return result.wasSuccessful()
