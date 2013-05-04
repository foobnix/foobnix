import unittest

from foobnix.util.time_utils import size2text, convert_seconds_to_text

class TestSize2Text(unittest.TestCase):
    def test_gigabyte(self):
        self.assertEquals('2.00 Gb', size2text(2*1024*1024*1024))
        self.assertEquals('2.20 Gb', size2text(2.2*1024*1024*1024))
    def test_megabyte(self):
        self.assertEquals('3.00 Mb', size2text(3*1024*1024))
        self.assertEquals('3.30 Mb', size2text(3.3*1024*1024))
    def test_kilobyte(self):
        self.assertEquals('4.00 Kb', size2text(4*1024))
        self.assertEquals('4.40 Kb', size2text(4.4*1024))

class TestConvertSecondsToText(unittest.TestCase):
    def check(self, expected, argument):
        self.assertEquals(expected, convert_seconds_to_text(argument))
    def test_zero(self):
        self.check('00:00', 0)
    def test_less_than_10_seconds(self):
        self.check('00:05', 5)
    def test_less_than_a_minute(self):
        self.check('00:55', 55)
    def test_less_than_10_minutes(self):
        self.check('05:45', 5*60+45)
    def test_less_than_an_hour(self):
        self.check('35:42', 35*60+42)
    def test_more_than_an_hour(self):
        self.check('3:35:42', 3*60*60+35*60+42)
