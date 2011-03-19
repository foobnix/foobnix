
import unittest
from foobnix.util.version import compare_versions
class TestNormalizeFunctions(unittest.TestCase):
    def test_normalize_function(self):
        self.assertEquals(0, compare_versions("","0.2.5-10"))
        self.assertEquals(0, compare_versions("",None))
        self.assertEquals(0, compare_versions("12312",""))
        self.assertEquals(0, compare_versions("0.2.5-10","0.2.5-10"))
        self.assertEquals(-1, compare_versions("0.2.5-10","0.2.5-1"))
        self.assertEquals(-1, compare_versions("0.2.5-10","0.2.5"))
        self.assertEquals(1, compare_versions("0.2.5-10","0.2.5-11"))
        self.assertEquals(-1, compare_versions("0.2.5-11","0.2.5-1"))
        self.assertEquals(-1, compare_versions("0.2.5-10","0.2.5-9"))
        self.assertEquals(1, compare_versions("0.2.5-9","0.2.5-10"))
        self.assertEquals(0, compare_versions("0.2.5","0.2.5-0"))
        self.assertEquals(1, compare_versions("0.2.3-9","0.2.5-0"))
        
        
        

if __name__ == '__main__':
    unittest.main()