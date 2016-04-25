#-*- coding: utf-8 -*-
'''
Created on Sep 8, 2010

@author: ivan
'''

from gi.repository import Gtk
import copy
import logging

from foobnix.fc.fc import FC
from foobnix.helpers.menu import Popup
from foobnix.gui.model.signal import FControl
from foobnix.gui.model.eq_model import EqModel
from foobnix.helpers.window import ChildTopWindow
from foobnix.helpers.my_widgets import ImageButton
from foobnix.util.mouse_utils import is_rigth_click
from foobnix.util.const import EQUALIZER_LABLES, STATE_PLAY


def label():
    label = Gtk.Label.new("–")
    label.show()
    return label

def empty():
    label = Gtk.Label.new(" ")
    label.show()
    return label

def text(text):
    label = Gtk.Label.new(text)
    label.show()
    return label

class EqWindow(ChildTopWindow, FControl):

    def __init__(self, controls, callback):
        self.callback = callback
        FControl.__init__(self, controls)
        ChildTopWindow.__init__(self, _("Equalizer"))

        self.combo = Gtk.ComboBoxText.new_with_entry()
        self.combo.connect("changed", self.on_combo_change)

        self.eq_lines = []
        for label in EQUALIZER_LABLES:
            self.eq_lines.append(EqLine(label, self.on_callback))

        lbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        lbox.show()

        lbox.pack_start(self.top_row(), False, False, 0)
        lbox.pack_start(self.middle_lines_box(), False, False, 0)

        self.add(lbox)

        self.models = []
        self.default_models = []

    def on_restore_defaults(self, *a):
        self.models = []
        num = self.combo.get_active()
        self.combo.get_model().clear()
        self.append_all_models(copy.deepcopy(self.default_models))
        self.combo.set_active(num)
        self.on_combo_change()

    def on_button_press(self, w, e):
        if is_rigth_click(e):
            menu = Popup()
            menu.add_item('Restore Defaults', "view-refresh", None)
            menu.show(e)

    def on_callback(self):
        pre = self.eq_lines[0].get_value()
        if float(pre) >= 0:
            pre = "+" + pre

        self.db_text.set_text(pre + "db")
        self.callback()

    def set_custom_title_and_button_label(self):
        status = _("Disabled")
        self.on.set_label(_("Enable EQ"))
        if FC().is_eq_enable:
            status = _("Enabled")
            self.on.set_label(_("Disable EQ"))
        self.set_title(_("Equalizer %s") % status)

    def on_enable_eq(self, w):
        FC().is_eq_enable = w.get_active()
        self.set_custom_title_and_button_label()
        self.controls.media_engine.realign_eq()
        #if self.controls.media_engine.get_state() == STATE_PLAY:
        #    self.controls.state_stop(remember_position=True)
        #    self.controls.state_play(under_pointer_icon=True)

    def on_save(self, *args):
        text = self.combo.get_active_text()

        logging.debug("text %s "%text)

        find = False
        text_id = None
        for model in self.models:
            if model.name == text:
                values = self.get_active_values()[1:]
                logging.debug("values %s " % values)
                model.set_values(values)
                model.set_preamp(self.get_active_values()[0])
                find = True
                text_id = model.id
                logging.debug("find %s "%model.id)
                break

        if not find:
            self.models.append(EqModel(text, text, self.get_active_values()[0], self.get_active_values()[1:]))
            self.combo.append_text(text)
            text_id = text
            logging.debug("not find %s "%text)

        FC().eq_presets_default =  text_id
        FC().eq_presets =  self.models
        logging.debug("SAVE %s "%text_id)
        FC().save()

    def get_active_values(self):
        result = []
        for line in self.eq_lines:
            result.append(float(line.get_value()))

        return result

    def notify_chage_eq_line(self):
        self.get_active_values()

    def append_all_models(self, models):
        self.models = models
        self.populate(models)

    def set_active(self, model_id):
        for i, c_model in enumerate(self.models):
            if c_model.id == model_id:
                self.combo.set_active(i)
                return

    def on_combo_change(self, *a):
        num = self.combo.get_active()
        if num >= 0:
            model = self.models[num]
            self.set_all_eq_span_values([model.preamp] + model.values)
            self.callback()

    def populate(self, models):
        for model in models:
            self.combo.append_text(model.name)

    def set_active_preset(self, name):
        self.presets_cache[name]

    def top_row(self):

        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        box.show()

        self.on = Gtk.ToggleButton.new_with_label(_("Enable EQ"))
        self.on.set_tooltip_text(_("To enable EQ set ON"))
        self.on.connect("toggled", self.on_enable_eq)
        self.on.show()

        auto = Gtk.ToggleButton.new_with_label(_("Auto"))
        auto.show()

        empt = empty()
        empt.set_size_request(65, -1)
        auto.show()
        self.combo.show()

        save = Gtk.Button.new_with_label(_("Save"))
        save.connect("clicked", self.on_save)

        save.show()

        resButton = ImageButton("view-refresh")
        resButton.connect("clicked", self.on_restore_defaults)
        resButton.set_tooltip_text(_("Restore defaults presets"))

        box.pack_start(self.on, False, False, 0)
        box.pack_start(empt, False, True, 0)
        box.pack_start(self.combo, False, True, 0)
        box.pack_start(save, False, True, 0)
        box.pack_start(Gtk.Label.new(None), True, True, 0)
        box.pack_start(resButton, False, True, 0)

        return box

    def dash_line(self):
        lables = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        lables.show()
        lables.pack_start(label(), False, False, 0)
        lables.pack_start(label(), True, False, 0)
        lables.pack_start(label(), False, False, 0)
        lables.pack_start(empty(), False, False, 0)
        return lables

    def db_line(self):
        lables = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        lables.show()
        lables.pack_start(text("+12db"), False, False, 0)

        self.db_text = text("0db")

        lables.pack_start(self.db_text, True, False, 0)
        lables.pack_start(text("-12db"), False, False, 0)
        lables.pack_start(empty(), False, False, 0)
        return lables

    def empty_line(self):
        lables = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        lables.show()
        lables.pack_start(empty(), False, False, 0)
        lables.pack_start(empty(), True, False, 0)
        lables.pack_start(empty(), False, False, 0)
        lables.pack_start(empty(), False, False, 0)
        return lables

    def middle_lines_box(self):
        lines_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        lines_box.show()

        eq_iter = iter(self.eq_lines)

        lines_box.pack_start(self.dash_line(), False, False, 0)
        lines_box.pack_start(eq_iter.next(), False, False, 0)
        lines_box.pack_start(self.dash_line(), False, False, 0)

        lines_box.pack_start(self.empty_line(), False, False, 0)
        lines_box.pack_start(self.db_line(), False, False, 0)
        lines_box.pack_start(self.empty_line(), False, False, 0)
        lines_box.pack_start(self.dash_line(), False, False, 0)

        lines_box.pack_start(eq_iter.next(), False, False, 0)
        lines_box.pack_start(self.dash_line(), False, False, 0)
        lines_box.pack_start(eq_iter.next(), False, False, 0)
        lines_box.pack_start(self.dash_line(), False, False, 0)
        lines_box.pack_start(eq_iter.next(), False, False, 0)
        lines_box.pack_start(self.dash_line(), False, False, 0)
        lines_box.pack_start(eq_iter.next(), False, False, 0)
        lines_box.pack_start(self.dash_line(), False, False, 0)
        lines_box.pack_start(eq_iter.next(), False, False, 0)
        lines_box.pack_start(self.dash_line(), False, False, 0)
        lines_box.pack_start(eq_iter.next(), False, False, 0)
        lines_box.pack_start(self.dash_line(), False, False, 0)
        lines_box.pack_start(eq_iter.next(), False, False, 0)
        lines_box.pack_start(self.dash_line(), False, False, 0)
        lines_box.pack_start(eq_iter.next(), False, False, 0)
        lines_box.pack_start(self.dash_line(), False, False, 0)
        lines_box.pack_start(eq_iter.next(), False, False, 0)
        lines_box.pack_start(self.dash_line(), False, False, 0)
        lines_box.pack_start(eq_iter.next(), False, False, 0)
        lines_box.pack_start(self.dash_line(), False, False, 0)
        lines_box.pack_start(self.empty_line(), False, False, 0)

        return lines_box

    def set_all_eq_span_values(self, values):
        for i, eq_scale in enumerate(self.eq_lines):
            eq_scale.set_value(values[i])

    def on_load(self):
        self.on.set_active(FC().is_eq_enable)
        if FC().is_eq_enable:
            self.on.set_label(_("Disable EQ"))

class EqLine(Gtk.Box):
        def __init__(self, text, callback, def_value=0):
            self.callback = callback
            self.text = text
            Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL, spacing=0)
            self.show()

            adjustment = Gtk.Adjustment(value=def_value, lower= -12, upper=12, step_incr=1, page_incr=2, page_size=0)
            self.scale = Gtk.VScale(adjustment=adjustment)
            self.scale.connect("change-value", self.on_change_value)
            self.scale.set_size_request(-1, 140)
            self.scale.set_draw_value(False)
            self.scale.set_inverted(True)
            self.scale.show()

            """text under"""
            text = Gtk.Label.new(text)
            text.show()

            self.pack_start(self.scale, False, False, 0)
            self.pack_start(text, False, False, 0)

        def on_change_value(self, *args):
            self.callback()

        def set_value(self, value):
            self.scale.set_value(value)

        def get_value(self):
            return "%.1f" % self.scale.get_value()
