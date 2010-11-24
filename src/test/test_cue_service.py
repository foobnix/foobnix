from foobnix.cue.cue_reader import CueReader
import unittest

""" TODO if possible to implament all cases with all different CUE files"""
class TestGoogleService(unittest.TestCase):
    def test_correct_cue(self):
        class FakeNormalReader(CueReader):
            def __init__(self, cue_file, duration_min):
                CueReader.__init__(self, cue_file)
                self.duration_min = duration_min
                
            def get_full_duration(self, cue_file):
                return 60 * self.duration_min

        cue = FakeNormalReader("cue/normal/Portishead - Dummy.cue", 45)
        common_beans = cue.get_common_beans()        
        result = [
                    ('Portishead', 'Mysterons', 0, 303, '05:03'),
                    ('Portishead', 'Sour Times', 303, 251, '04:11'),
                    ('Portishead', 'Strangers', 554, 237, '03:57'),
                    ('Portishead', 'It Could Be Sweet', 791, 256, '04:16'),
                    ('Portishead', 'Wandering Star', 1047, 293, '04:53'),
                    ('Portishead', "It's a Fire", 1340, 225, '03:45'),
                    ('Portishead', 'Numb', 1565, 234, '03:54'),
                    ('Portishead', 'Roads', 1799, 303, '05:03'),
                    ('Portishead', 'Pedestal', 2102, 219, '03:39'),
                    ('Portishead', 'Biscuit', 2321, 301, '05:01'),
                    ('Portishead', 'Glory Box', 2622, 78, '01:18')
                   ]
        
        self.assertTrue(common_beans)
        
        for i, bean in enumerate(common_beans):
            line = bean.artist, bean.title, bean.start_sec, bean.duration_sec, bean.time
            self.assertEquals(result[i], line)
            
    def test_splited_cue(self):
        class FakeSplitReader(CueReader):
            def __init__(self, cue_file, duration_min):
                CueReader.__init__(self, cue_file)
                self.duration_min = duration_min
                
            def get_full_duration(self, cue_file):
                if "01 - Pray for Rain.flac" in cue_file:
                    return 60 * self.duration_min
                if "02 - Babel.flac" in cue_file:
                    return 60 * self.duration_min
                if "10 - Atlas Air.flac" in cue_file:
                    return 60 * self.duration_min
                
                return 60 * self.duration_min
        
        cue = FakeSplitReader("cue/split/Heligoland.cue", 45)
                
        common_beans = cue.get_common_beans() 
        result = [
                 ('01 - Pray for Rain', 0, 0, '00:00'),
                 ('02 - Babel', 0, 0, '00:00'),
                 ('10 - Atlas Air', 0, 0, '00:00')
                 ]
        
        self.assertTrue(common_beans)
        
        for i in [0, 1, 9]:
            bean = common_beans[i]
            line = bean.text, bean.start_sec, bean.duration_sec, bean.time
            self.assertEquals(result[i], line)  
    
    
if __name__ == '__main__':
    unittest.main()    
