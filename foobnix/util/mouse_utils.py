
from gi.repository import Gtk
from gi.repository import Gdk

def is_left_click(event):
    if event.button == 1 and event.type == Gdk.EventType.BUTTON_PRESS: #@UndefinedVariable
        return True
    else:
        return False

def is_double_left_click(event):
    if event.button == 1 and event.type == Gdk.EventType._2BUTTON_PRESS: #@UndefinedVariable
        return True
    else:
        return False

def is_middle_click(event):
    if event.button == 2 and event.type == Gdk.EventType.BUTTON_PRESS: #@UndefinedVariable
        return True
    else:
        return False

def is_double_middle_click(event):
    if event.button == 2 and event.type == Gdk.EventType._2BUTTON_PRESS: #@UndefinedVariable
        return True
    else:
        return False

def is_rigth_click(event):
    if event.button == 3 and event.type == Gdk.EventType.BUTTON_PRESS: #@UndefinedVariable
        return True
    else:
        return False

def is_double_rigth_click(event):
    if event.button == 3 and event.type == Gdk.EventType._2BUTTON_PRESS: #@UndefinedVariable
        return True
    else:
        return False

def is_middle_click_release(event):
    if event.button == 2 and event.type == Gdk.EventType.BUTTON_RELEASE: #@UndefinedVariable
        return True
    else:
        return False

def is_rigth_click_release(event):
    if event.button == 3 and event.type == Gdk.EventType.BUTTON_RELEASE: #@UndefinedVariable
        return True
    else:
        return False
    
def is_left_click_release(event):
    if event.button == 1 and event.type == Gdk.EventType.BUTTON_RELEASE: #@UndefinedVariable
        return True
    else:
        return False
    
def right_click_optimization_for_trees(treeview, event):
    try:
        path, col, cellx, celly = treeview.get_path_at_pos(int(event.x), int(event.y))
        # just in case the view doesn't already have focus
        treeview.grab_focus()
        treeview.stop_emission('button-press-event')
        selection = treeview.get_selection()
                 
        # if this row isn't already selected, then select it before popup
        if not selection.path_is_selected(path):
            selection.unselect_all()                                                
            selection.select_path(path)
    except TypeError:
        treeview.get_selection().unselect_all()
    
def is_empty_click(treeview, event):
    try:
        path, col, cellx, celly = treeview.get_path_at_pos(int(event.x), int(event.y))
        return False
    except TypeError:
        return True