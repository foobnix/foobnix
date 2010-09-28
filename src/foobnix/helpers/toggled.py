'''
Created on Sep 23, 2010

@author: ivan
'''
class OneActiveToggledButton():
    def __init__(self, buttons):
        for button in buttons:
            button.connect("toggled", self.one_button_selected, buttons) 
    
    def one_button_selected(self, clicked_button, buttons):
        # so, the button becomes checked. Uncheck all other buttons
        for button in buttons:
            if button != clicked_button:
                button.set_active(False)    

        if all([not button.get_active() for button in buttons]):
            clicked_button.set_active(True)
            
        # if the button should become unchecked, then do nothing
        if not clicked_button.get_active():
            return
    

