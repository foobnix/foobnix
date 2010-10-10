#-*- coding: utf-8 -*-
import gtk
#import gobject
from foobnix.regui.treeview.scanner import DirectoryScanner
from foobnix.regui.model import FTreeModel, FModel
from foobnix.util import LOG
import uuid
from foobnix.regui.model.signal import FControl
import copy

class TreeViewControl(gtk.TreeView, FTreeModel, FControl):

    def __init__(self, controls):
        gtk.TreeView.__init__(self)
        FTreeModel.__init__(self)
        FControl.__init__(self, controls)

        self.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.set_enable_tree_lines(True)

        """model config"""
        print "types", FTreeModel().types()
        self.model = gtk.TreeStore(*FTreeModel().types())

        """filter config"""
        self.filter_model = self.model.filter_new()
        print "visible", self.visible[0]
        self.filter_model.set_visible_column(self.visible[0])
        self.set_model(self.filter_model)

        """connectors"""
        self.connect("button-press-event", self.on_button_press)
        self.connect("key-release-event", self.on_key_release)

        self.connect("drag-drop", self.on_drag_drop)

        self.enable_model_drag_source(gtk.gdk.BUTTON1_MASK, [("example1", 0, 0)], gtk.gdk.ACTION_COPY)
        self.enable_model_drag_dest([("example1", 0, 0)], gtk.gdk.ACTION_COPY)


        self.count_index = 0

        self.set_reorderable(False)
        self.set_headers_visible(False)

        self.prev_iter_play_icon = None

        self.init_data_tree()

    def init_data_tree(self):
        self.get_model().get_model().clear()
        """ Madonna """
        list = []
        list.append(FModel("Madonna").add_is_file(False))
        list.append(FModel("Madonna - Song1").add_parent("Madonna").add_is_file(True))
        list.append(FModel("Madonna - Song2").add_parent("Madonna").add_is_file(True))
        for line in list:
            self.append(line)

        bean = FModel('TEXT').add_font("bold")
        parent = self.append(bean)
        self.append(FModel('TEXT1').add_font("normal").add_level(parent))
        self.append(FModel('TEXT2').add_font("normal").add_level(parent))
        self.append(FModel('TEXT2').add_font("normal").add_level(parent))
        self.append(FModel('TEXT').add_font("bold"))
        self.append(FModel('TEXT').add_font("bold"))


    def iter_copy(self, from_model, from_iter, to_model, to_iter, pos):

        #row = [from_model.get_value(from_iter, 0), from_model.get_value(from_iter, 1), True]
        row = self.get_row_from_model_iter(from_model, from_iter)

        if (pos == gtk.TREE_VIEW_DROP_INTO_OR_BEFORE) or (pos == gtk.TREE_VIEW_DROP_INTO_OR_AFTER):
            new_iter = to_model.prepend(to_iter, row)
        elif pos == gtk.TREE_VIEW_DROP_BEFORE:
            new_iter = to_model.insert_before(None, to_iter, row)
        elif pos == gtk.TREE_VIEW_DROP_AFTER:
            new_iter = to_model.insert_after(None, to_iter, row)
        else:
            new_iter = to_model.append(None, row)

        if from_model.iter_has_child(from_iter):
            for i in range(0, from_model.iter_n_children(from_iter)):
                next_iter_to_copy = from_model.iter_nth_child(from_iter, i)
                self.iter_copy(from_model, next_iter_to_copy, to_model, new_iter, gtk.TREE_VIEW_DROP_INTO_OR_BEFORE)

    def on_drag_drop(self, to_tree, drag_context, x, y, selection):
        to_filter_model = to_tree.get_model()
        to_model = to_filter_model.get_model()
        if to_tree.get_dest_row_at_pos(x, y):
            to_path, to_pos = to_tree.get_dest_row_at_pos(x, y)
            to_path = to_filter_model.convert_path_to_child_path(to_path)
            to_iter = to_model.get_iter(to_path)
        else:
            to_path = None
            to_pos = None
            to_iter = None


        from_tree = drag_context.get_source_widget()
        from_filter_model, from_paths = from_tree.get_selection().get_selected_rows()
        from_model = from_filter_model.get_model()
        from_path = from_filter_model.convert_path_to_child_path(from_paths[0])
        from_iter = from_model.get_iter(from_path)

        self.iter_copy(from_model, from_iter, to_model, to_iter, to_pos)

        if to_tree == from_tree:
            """move element in the save tree"""
            drag_context.finish(True, True)

        if to_path:
            to_tree.expand_to_path(to_path)


    def set_scrolled(self, policy_horizontal, policy_vertical):
        self.scroll = gtk.ScrolledWindow()
        self.scroll.set_policy(policy_horizontal, policy_vertical)
        self.scroll.add_with_viewport(self)
        self.scroll.show_all()
        return self

    def populate(self, beans):
        self.clear()
        for bean in beans:
            bean.level = None
            self.append(bean)

    def append(self, bean):
        bean.visible = True
        if bean.is_file == True:
            bean.font = "normal"
        else:
            bean.font = "bold"
        #bean.text = bean.text + " !" + str(bean.start_sec) + "=" + str(bean.duration_sec)

        bean.index = self.count_index
        self.count_index += 1

        row = self.get_row_from_bean(bean)

        if isinstance(bean.level, gtk.TreeIter):
            value = self.model.append(bean.level, row)
        else:
            value = self.model.append(None, row)
        return value

    def get_bean_from_row(self, row):
        bean = FModel()
        id_dict = FTreeModel().cut().__dict__
        for key in id_dict.keys():
            num = id_dict[key]
            setattr(bean, key, row[num])
        return bean


    def get_row_from_bean(self, bean):
        attributes = []
        m_dict = FTreeModel().cut().__dict__
        new_dict = dict (zip(m_dict.values(), m_dict.keys()))

        for key in new_dict.values():
            value = getattr(bean, key)
            attributes.append(value)
        return attributes

    def get_row_from_model_iter(self, model, iter):
        attributes = []
        size = len(FTreeModel().__dict__)
        for i in xrange(size):
            value = model.get_value(iter, i)
            attributes.append(value)
        return attributes

    def append_from_scanner(self, all):
        """copy beans"""
        beans = copy.deepcopy(all)

        hash = {None:None}
        for bean in beans:
            if bean is None:
                continue
            bean.visible = True
            if hash.has_key(bean.level):
                level = hash[bean.level]
            else:
                level = None

            if bean.is_file:
                child_level = self.append(bean.add_font("normal").add_level(level))
            else:
                child_level = self.append(bean.add_font("bold").add_level(level))

            hash[bean.path] = child_level

    def populate_from_scanner(self, beans):
        self.clear()
        self.append_from_scanner(beans)

    def clear(self):
        self.count_index = 0
        self.model.clear()

    def on_button_press(self, w, e):
        pass

    def on_key_release(self, w, e):
        pass

    def delete_selected(self):
        selection = self.get_selection()
        fm, paths = selection.get_selected_rows()
        path = paths[0]
        path = self.filter_model.convert_path_to_child_path(path)
        iter = self.model.get_iter(path)
        self.model.remove(iter)

    def get_selected_bean(self):
        selection = self.get_selection()
        model, paths = selection.get_selected_rows()
        if not paths:
            return None
        return self._get_bean_by_path(paths[0])

    def set_play_icon_to_selected_bean(self):
        selection = self.get_selection()
        filter_model, paths = selection.get_selected_rows()
        if not paths:
            return None
        path = filter_model.convert_path_to_child_path(paths[0])
        model = filter_model.get_model()
        iter = model.get_iter(path)
        model.set_value(iter, self.play_icon[0], gtk.STOCK_MEDIA_PLAY)
        if self.prev_iter_play_icon:
            model.set_value(self.prev_iter_play_icon, self.play_icon[0], None)
        self.prev_iter_play_icon = iter

    def get_children_beans_by_selected(self):
        selection = self.get_selection()
        model, paths = selection.get_selected_rows()
        selected = model.get_iter(paths[0])
        n = model.iter_n_children(selected)
        iterch = model.iter_children(selected)

        results = []

        for i in xrange(n):
            path = model.get_path(iterch)
            bean = self._get_bean_by_path(path)
            results.append(bean)
            iterch = model.iter_next(iterch)

        return results

    def _get_bean_by_path(self, path):
        model = self.model
        LOG.info("Selecte bean path", path)

        path = self.filter_model.convert_path_to_child_path(path)
        LOG.info("Selecte bean path", path)
        iter = model.get_iter(path)

        if iter:
            bean = FModel()
            dt = FTreeModel().__dict__
            for key in dt.keys():
                setattr(bean, key, model.get_value(iter, dt[key][0]))
            return bean
        return None

    def get_bean_by_position(self, position):
        bean = FModel()
        dt = FTreeModel().__dict__
        for key in dt.keys():
            setattr(bean, key, self.model[position][dt[key][0]])

        return bean

    def get_all_beans(self):
        beans = []
        for i in xrange(len(self.model)):
            beans.append(self.get_bean_by_position(i))
        return beans

    def get_all_selected_beans(self):
        selection = self.get_selection()
        model, paths = selection.get_selected_rows()
        if not paths:
            return None
        beans = []
        for path in paths:
            selection.select_path(path)
            bean = self._get_bean_by_path(path)
            beans.append(bean)
        return beans

    def filter(self, query):
        if len(query.strip()) > 0:
            query = query.strip().decode("utf-8").lower()

            for line in self.model:
                name = line[self.text[0]].lower()

                if name.find(query) >= 0:
                    #LOG.info("FIND PARENT:", name, query)
                    line[self.visible[0]] = True
                else:
                    find = False
                    child_count = 0;
                    for child in line.iterchildren():
                        name = str(child[self.text[0]]).decode("utf-8").lower()
                        #name = child[self.text[0]]
                        if name.find(query) >= 0:
                            child_count += 1
                            #LOG.info("FIND CHILD :", name, query)
                            child[self.visible[0]] = True
                            line[self.visible[0]] = True
                            #line[self.POS_FILTER_CHILD_COUNT] = child_count
                            find = True
                        else:
                            child[self.visible[0]] = False
                    if not find:
                        line[self.visible[0]] = False
                    else:
                        self.expand_all()
        else:
            self.collapse_all()
            for line in self.model:
                line[self.visible[0]] = True
                for child in line.iterchildren():
                    child[self.visible[0]] = True
