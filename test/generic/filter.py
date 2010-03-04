import gtk
import gobject

# Prepare the window and other Gtk stuff 
window = gtk.Window(gtk.WINDOW_TOPLEVEL)
window.set_default_size(100, 200)
window.connect("destroy", gtk.main_quit)
vbox = gtk.VBox()
window.add(vbox)

# Creation of the actual model
text = ["This", "is", "an", "example", "of", "hiding", "rows"]
store = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING,gobject.TYPE_BOOLEAN)
for i in text:
   store.append((i, i +"1", True))

# Creation of the filter, from the model
filter = store.filter_new()
filter.set_visible_column(2)

# The TreeView gets the filter as model
view = gtk.TreeView(filter)

# Some other gtk stuff
renderer = gtk.CellRendererText()
view.insert_column_with_attributes(-1,"Test",renderer,text=0)
view.insert_column_with_attributes(-1,"Test1",renderer,text=1)
view.insert_column_with_attributes(-1,"isTrue",renderer,text=2)
vbox.pack_start(view)
hide_button = gtk.Button("Hide Selected")
vbox.pack_start(hide_button)

# The hiding function
def hide_row(widget, *args):
   # Get the selected row
   filter_iter = view.get_selection().get_selected()[1]
   # Translate it into a useful iterator
   store_iter = filter.convert_iter_to_child_iter(filter_iter)
   # Use it to hide the row
   store[store_iter][2] = False

hide_button.connect("clicked", hide_row)

# That's it
window.show_all()
gtk.main()
