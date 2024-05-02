# -*- coding: utf-8 -*-
"""
Created on Wed Mar 29 13:56:21 2023

@author: tjostmou
"""

import os
from .core import JsonRoot

class FileBasedJsonRoot(JsonRoot):
    
    #### INSTANCIATION HELPERS
    
    @classmethod
    def from_jsondb_file(cls,filepath):
        filepath = os.path.abspath(filepath)
        with open(filepath,"r", encoding='utf8') as f :
            content_string = f.read()
        return  cls.from_jsondb_string(content_string)
    
    @classmethod
    def from_json_file(cls,filepath):
        filepath = os.path.abspath(filepath)
        with open(filepath,"r", encoding='utf8') as f :
            content_string = f.read()
        return  cls.from_json_string(content_string)
    
    #### OUTPUT METHODS
    
    def to_file(self,filepath, item = None):
        if item is None :
            item = self
        if not isinstance(item,str) :
            item  = self.__as_str__(item)
        filepath = os.path.abspath(filepath)
        with open(filepath,"w+", encoding='utf8') as f:
            f.write(item)