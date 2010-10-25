#-*- coding: utf-8 -*-
'''
Created on 24 окт. 2010

@author: ivan
'''
from foobnix.eq.eq_gui import EqWindow
from foobnix.regui.model.signal import FControl
from foobnix.regui.state import LoadSave
from foobnix.regui.model.eq_model import EqModel

class EqController(FControl, LoadSave):
    def __init__(self, controls):
        FControl.__init__(self, controls)
        LoadSave.__init__(self)
                
        self.eq_view = EqWindow(None, self.on_eq_chaged)
        self.eq_view.hide()
    
    def show(self):
        self.eq_view.show_all()
        
    def hide(self):
        self.eq_view.hide()
    
    def on_eq_chaged(self):
        self.controls.media_engine.set_all_bands(self.eq_view.get_active_values()[1:])
        print self.eq_view.get_active_values()[1:]
    
    def on_load(self):
        self.eq_view.append_all_models(self.default_models())
        self.eq_view.set_active("DANCE")
        self.eq_view.on_load()
    
    def on_save(self):
        self.eq_view.on_save()
    
    def default_models(self):
        models = []
        models.append(EqModel("CUSTOM", "Custom", 0, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]))
        models.append(EqModel("DEFAULT", "Default", 0, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]))
        models.append(EqModel("CLASSICAL", "Classical", 0, [0, 0, 0, 0, 0, 0, -7.2, -7.2, -7.2, -9.6]))
        models.append(EqModel("CLUB", "Club", 0, [ 0, 0, 8, 5.6, 5.6, 5.6, 3.2, 0, 0, 0]))
        models.append(EqModel("DANCE", "Dance", 0, [ 9.6, 7.2, 2.4, 0, 0, -5.6, -7.2, -7.2, 0, 0]))
        models.append(EqModel("FULL BASS", "Full Bass", 0, [ -8, 9.6, 9.6, 5.6, 1.6, -4, -8, -10.4, -11.2, -11.2]))
        models.append(EqModel("FULL BASS AND TREBLE", "Full Bass and Treble", 0, [ 7.2, 5.6, 0, -7.2, -4.8, 1.6, 8, 11.2, 12, 12]))
        models.append(EqModel("FULL TREBLE", "Full Treble", 0, [ -9.6, -9.6, -9.6, -4, 2.4, 11.2, 16, 16, 16, 16.8]))
        models.append(EqModel("LAPTOP SPEAKERS", "Laptop Speakers and Headphones", 0, [ 4.8, 11.2, 5.6, -3.2, -2.4, 1.6, 4.8, 9.6, 11.9, 11.9]))
        models.append(EqModel("LARGE HALL", "Large Hall", 0, [ 10.4, 10.4, 5.6, 5.6, 0, -4.8, -4.8, -4.8, 0, 0]))
        models.append(EqModel("LIVE", "Live", 0, [ -4.8, 0, 4, 5.6, 5.6, 5.6, 4, 2.4, 2.4, 2.4]))
        models.append(EqModel("PARTY", "Party", 0, [ 7.2, 7.2, 0, 0, 0, 0, 0, 0, 7.2, 7.2]))
        models.append(EqModel("POP", "Pop", 0, [ -1.6, 4.8, 7.2, 8, 5.6, 0, -2.4, -2.4, -1.6, -1.6]))
        models.append(EqModel("REGGAE", "Reggae", 0, [ 0, 0, 0, -5.6, 0, 6.4, 6.4, 0, 0, 0]))
        models.append(EqModel("ROCK", "Rock", 0, [ 8, 4.8, -5.6, -8, -3.2, 4, 8.8, 11.2, 11.2, 11.2]))
        models.append(EqModel("SKA", "Ska", 0, [ -2.4, -4.8, -4, 0, 4, 5.6, 8.8, 9.6, 11.2, 9.6]))
        models.append(EqModel("SOFT", "Soft", 0, [ 4.8, 1.6, 0, -2.4, 0, 4, 8, 9.6, 11.2, 12]))
        models.append(EqModel("SOFT ROCK", "Soft Rock", 0, [ 4, 4, 2.4, 0, -4, -5.6, -3.2, 0, 2.4, 8.8]))
        models.append(EqModel("TECHNO", "Techno", 0, [ 8, 5.6, 0, -5.6, -4.8, 0, 8, 9.6, 9.6, 8.8]))
        return models

