'''
Created on Sep 23, 2010

@author: ivan
'''
class OneActiveToggledButton():
    def __init__(self, buttons):
        self.buttons = buttons
        for button in buttons:
            button.connect("toggled", self.one_button_selected) 
    
    def one_button_selected(self, clicked_button):
        if all([not button.get_active() for button in self.buttons]):
            clicked_button.set_active(True)
    
        # if the button should become unchecked, then do nothing
        if not clicked_button.get_active():
            return
    
        # so, the button becomes checked. Uncheck all other buttons
        for button in self.buttons:
            if button != clicked_button:
                button.set_active(False)    