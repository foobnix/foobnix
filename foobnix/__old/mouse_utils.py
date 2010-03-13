import gtk
def is_double_click(event):
    if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS: #@UndefinedVariable
        return True
    else:
        return False