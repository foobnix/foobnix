#-*- coding: utf-8 -*-
'''
Created on 7 нояб. 2010

@author: ivan
'''

from foobnix.regui.model import FTreeModel
from foobnix.regui.treeview.dragdrop_tree import DragDropTree

class FilterTreeControls(DragDropTree):
    def __init__(self, controls):
        DragDropTree.__init__(self, controls)
    
    def show_all_lines(self):
        def req(line):
                for child in line.iterchildren():
                    child[self.visible[0]] = True
                    req(child)
                    
        for line in self.model:
            line[self.visible[0]] = True
            req(line)
    
    def is_query_in_file_line(self, query, parent, column_num):
        find = False
        
        for child in parent.iterchildren():
            
            column_text = child[column_num].decode().lower().strip()
        
            if not child[self.is_file[0]]:
                """folder"""                                            
                if self.is_query_in_file_line(query, child, column_num):
                    find = True                    
            else:
                """file"""
                if query in column_text:
                    child[self.visible[0]] = True
                    find = True
                else:
                    child[self.visible[0]] = False
        
        if not parent[self.is_file[0]]:
            parent[self.visible[0]] = find
                    
        return find
    
    def is_query_in_folder_line(self, query, parent, column_num):
        find = False
        
        for child in parent.iterchildren():
            
            column_text = child[column_num].decode().lower().strip()
        
            if not child[self.is_file[0]]:
                if query in column_text:                    
                    find = True
                elif self.is_query_in_folder_line(query, child, column_num): 
                    find = True
            else:
                """file"""                    
                if query in column_text:                                        
                    find = True
        
        parent[self.visible[0]] = find
                    
        return find    
    
    def file_filter(self, query, column_num):
        for parent in self.model:  
            if parent[self.is_file[0]]:
                column_text = parent[column_num].decode().lower().strip()
                if query not in column_text:
                    parent[self.visible[0]] = False
            else:
                self.is_query_in_file_line(query, parent, column_num)                
            
    def folder_filter(self, query, column_num):
        for parent in self.model:  
            if not parent[self.is_file[0]]:
                column_text = parent[column_num].decode().lower().strip()
                if query not in column_text:                    
                    self.is_query_in_folder_line(query, parent, column_num)
    
    def filter_by_file(self, query, column_num=FTreeModel().text[0]):        
        self.show_all_lines()
        
        if query and len(query.strip()) > 0:
            query = query.decode().strip().lower()
            self.file_filter(query, column_num)
            self.expand_all()
        else:
            self.collapse_all()
    
    def filter_by_folder(self, query, column_num=FTreeModel().text[0]):        
        self.show_all_lines()
        
        if query and len(query.strip()) > 0:
            query = query.decode().strip().lower()
            self.folder_filter(query, column_num)
            self.expand_all()
        else:
            self.collapse_all()
