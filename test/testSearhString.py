from unittest import TestCase
class TestStringSearch(TestCase):
    
    def testFind(self):
        input = "Changed in version 2.2.3: The chars parameter was added."
        search = "ver"
        print input.find(search)
        self.assertTrue(input.find(search))
        
        
