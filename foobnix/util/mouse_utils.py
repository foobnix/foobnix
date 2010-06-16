import gtk
def is_double_click(event):
    if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS: #@UndefinedVariable
        return True
    else:
        return False

def is_double_left_click(event):
    if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS: #@UndefinedVariable
        return True
    else:
        return False


def is_double_rigth_click(event):
    if event.button == 3 and event.type == gtk.gdk._2BUTTON_PRESS: #@UndefinedVariable
        return True
    else:
        return False


def is_rigth_click(event):
    if event.button == 3 and event.type == gtk.gdk.BUTTON_PRESS: #@UndefinedVariable
        return True
    else:
        return False

    