#-*- coding: utf-8 -*-
'''
Created on 24 окт. 2010

@author: ivan
'''

import logging

from foobnix.fc.fc import FC
from foobnix.util import analytics
from foobnix.eq.eq_gui import EqWindow
from foobnix.gui.state import LoadSave
from foobnix.gui.model.signal import FControl
from foobnix.gui.model.eq_model import EqModel


class EqController(FControl, LoadSave):
    def __init__(self, controls):
        FControl.__init__(self, controls)
        LoadSave.__init__(self)

        self.eq_view = EqWindow(controls, self.on_eq_chaged)
        self.eq_view.hide()

    def show(self):
        self.eq_view.show_all()
        analytics.action("EqController")

    def hide(self):
        self.eq_view.hide()

    def get_preamp(self):
        return self.eq_view.get_active_values()[0]

    def get_bands(self):
        return self.eq_view.get_active_values()[1:]

    def on_eq_chaged(self):
        pre = self.eq_view.get_active_values()[0]
        self.controls.media_engine.set_all_bands(pre, self.eq_view.get_active_values()[1:])

    def on_load(self):
        logging.debug("FC().eq_presets %s" % FC().eq_presets)
        if FC().eq_presets:
            self.eq_view.append_all_models(FC().eq_presets)
        else:
            self.eq_view.append_all_models(self.default_models())

        self.eq_view.default_models = self.default_models()
        self.eq_view.set_active(FC().eq_presets_default)

        logging.debug("default_models %s" % self.default_models())
        logging.debug("FC().eq_presets_default %s" % FC().eq_presets_default)

        self.eq_view.on_load()

    def on_save(self):
        pass

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

