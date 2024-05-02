# -*- coding: utf-8 -*-
"""

Boilerplate:
A one line summary of the module or program, terminated by a period.

Rest of the description. Multiliner

<div id = "exclude_from_mkds">
Excluded doc
</div>

<div id = "content_index">

<div id = "contributors">
Created on Mon Mar  6 10:01:02 2023
@author: Timothe
</div>
"""

import json
import os


class UNDEFINED:
    pass


class JsonCategory(dict):

    allowed_keys = ["name", "content", "description", "is_shown"]

    def __init__(self, name, content, is_shown=None, description=""):

        self["name"] = name
        self["content"] = content
        self["description"] = description
        self["is_shown"] = is_shown

    @property
    def name(self):
        return self["name"]

    @property
    def description(self):
        return self["description"]

    @property
    def params(self):
        return [item for item in self.content if hasattr(item, "value")]

    @property
    def categories(self):
        return [item for item in self.content if hasattr(item, "content")]

    @property
    def content(self):
        return self["content"]

    @property
    def is_shown(self):
        if self["is_shown"] is None:
            if not len(self.content):
                return False
            return max([item.is_shown for item in self.content])
        else:
            return self["is_shown"]

    def show(self):
        self["is_shown"] = True

    def hide(self):
        self["is_shown"] = False

    def weak_show(self):
        self["is_shown"] = None

    def set_is_shown(self,is_shown):
        if is_shown is None :
            self.weak_show()
        elif is_shown :
            self.show()
        else :
            self.hide()

    def add_param(self, name, value):
        self["content"].append(JsonParam(name=name, value=value))

    def add_category(self, name, content=[], is_shown=None):
        self["content"].append(JsonCategory(
            name=name, content=content, is_shown=is_shown))

    def __getattr__(self, name):
        names = [item.name for item in self["content"]]
        if name in names:
            index = names.index(name)
            return self["content"][index]
        else:
            raise AttributeError(f"JsonCategory has no attribute {name}")

    def __setitem__(self, key, value):
        if not key in self.allowed_keys:
            raise KeyError(f"{key} key is not allowed in JsonCategory")
        super().__setitem__(key, value)

    @classmethod
    def from_dict(cls, dico):
        instanciated_content = []
        if not isinstance(dico["content"], list):
            dico["content"] = [dico["content"]]
        for item in dico["content"]:
            if "value" in item.keys():
                instanciated_item = JsonParam.from_dict(item)
            elif "content" in item.keys():
                instanciated_item = JsonCategory.from_dict(item)
            else:
                raise KeyError(
                    f"The item {item} does not have a value not a content key, and cannot be processed in a jsonparam file.")
            instanciated_content.append(instanciated_item)

        instanciated_content = sorted(
            instanciated_content, key=lambda item: item.name)
        dico["content"] = instanciated_content
        return cls(**dico)

    def get_digest(self):
        content = {}
        [content.update(c.get_digest()) for c in self.content if c.is_shown]
        return {self.name: content}


class JsonParam(dict):

    allowed_keys = ["name", "value", "default",
                    "is_default", "is_shown", "description", "dtype"]

    def __init__(self, *, name, value,
                 default=UNDEFINED,
                 description="",
                 dtype=UNDEFINED,
                 is_default=UNDEFINED,
                 is_shown=UNDEFINED):

        # if default nor is_default are defined, set them to current value
        if default == UNDEFINED and is_default == UNDEFINED:
            default = value

        if dtype == UNDEFINED:
            dtype = "auto"

        # sanitize is_default
        if default == value:
            is_default = True
        else:
            is_default = False

        # if is hown is currentely not defined, set it to true, for user to easily find it
        if is_shown == UNDEFINED:
            is_shown = True

        self["name"] = name
        self["value"] = value
        self["default"] = default
        self["dtype"] = dtype
        self["description"] = description
        self["is_default"] = is_default
        self["is_shown"] = is_shown

    @property
    def name(self):
        return self["name"]

    @property
    def default(self):
        return self["default"]

    @property
    def description(self):
        return self["description"]

    @property
    def dtype(self):
        return self["dtype"]

    @property
    def value(self):
        return self["value"]

    @property
    def is_default(self):
        return self["is_default"]

    def set_type(self, typestring):
        typestring = typestring.replace(" ", "").replace("\n", "")
        self["dtype"] = typestring

    @property
    def is_shown(self):
        return self["is_shown"]

    def set_value(self, value):
        value = self._get_value(value)
        self["value"] = value
        self["is_default"] = self["default"] == self["value"]
        

    def _get_value(self, value):
        if self.dtype != "str" and isinstance(value,str) :
            value = json.loads(value)
        if isinstance(value,dict):
            raise TypeError("""A value in a jsonparam cannot be a dictionnary. 
            Create a new json param in the parent json category instead. 
            If you want to use collections of values, use a standard list syntax.""")
        return value

    def reset_value(self):
        self.set_value(self["default"])

    def make_default(self, value=UNDEFINED):
        self["default"] = value
        self["is_default"] = True

    def set_default(self,value):
        self["default"] = self._get_value(value)
        self["is_default"] = self["default"] == self["value"]

    def set_is_shown(self,is_shown):
        if is_shown :
            self.show()
        else :
            self.hide()

    def show(self):
        self["is_shown"] = True

    def hide(self):
        self["is_shown"] = False

    def __setitem__(self, key, value):
        if not key in self.allowed_keys:
            raise KeyError(f"{key} key is not allowed in JsonParam")
        super().__setitem__(key, value)

    @classmethod
    def from_dict(cls, dico):
        # replace UNDEFINED string by UNDEFINED class
        for key in dico.keys():
            if dico[key] == "UNDEFINED":
                dico[key] = UNDEFINED
        return cls(**dico)

    def get_digest(self):
        return {self.name: self.value}


class JsonRoot(list):

    # def __init__(cls, content):
    #    super().__init__(content)

    def __getattr__(self, name):
        names = [item.name for item in self]
        if name in names:
            index = names.index(name)
            return self[index]
        else:
            raise AttributeError(f"JsonRoot has no attribute {name}")

    def add_param(self, name, value):
        self.append(JsonParam(name=name, value=value))

    def add_category(self, name, content=[], is_shown=None):
        self.append(JsonCategory(
            name=name, content=content, is_shown=is_shown))

    @property
    def is_shown(self):
        if not len(self.params):
            return False
        return max([item.is_shown for item in self.content])

    @property
    def params(self):
        return [item for item in self.content if hasattr(item, "value")]

    @property
    def categories(self):
        return [item for item in self.content if hasattr(item, "content")]

    @property
    def content(self):
        return self

    #region INPUT METHODS

    def add_elements_from_instance(self, json_root_instance):
        
        def get_list_as_dict(alist):
            return {item["name"]: item for item in alist}
        
        def recursive_element_assignation(original_list, imported_list):
            original = get_list_as_dict(original_list)
            imported = get_list_as_dict(imported_list)
            
            for key in imported.keys():
                
                if key in original.keys():
                    if hasattr(original[key],"value") :
                        continue
                    if hasattr(original[key],"content") and hasattr(imported[key],"content"):
                        recursive_element_assignation( original[key]["content"], imported[key]["content"] )
                else :
                    original_list.append(imported[key])
                    #regardless if it's a category or a parameter, we add all it's subcontent anyway as the root doesn't exist
            
        recursive_element_assignation(self, json_root_instance)
        

    def set_elements_from_instance(self, json_root_instance, elements=["value"]):

        allowed_elements = ["value","is_shown","default"]

        for element in elements :
            if not element in allowed_elements: 
                raise ValueError(f"allowed_elements are : {allowed_elements}")

        def get_list_as_dict(alist):
            return {item["name"]: item for item in alist}

        def recursive_value_assignation(original_list, imported_list):
            original = get_list_as_dict(original_list)
            imported = get_list_as_dict(imported_list)
            for key in original.keys():
                if not key in imported.keys():
                    continue
                # here we know that 'key' exists in both original and imported instances
                for element in elements:
                    try:
                        eval(f"original[key].set_{element}")(imported[key][element])
                    except AttributeError:
                        # if we get AttributeError, this element is not settable in this instance (JsonCategory trying to set value for example.
                        # we simply skip.
                        pass

                if hasattr(original[key], "content") and hasattr(imported[key], "content"):
                    
                    recursive_value_assignation(
                        original[key]["content"], imported[key]["content"])

        recursive_value_assignation(self, json_root_instance)

    # INSTANCIATION HELPERS

    @classmethod
    def from_json_dict(cls, dico):

        def list_to_dict(lis):
            content_instance = {}
            for item in lis:
                # if not hasattr(item,"keys"):
                #raise ValueError("Inside a list, all elements must be dictionnaries to not loose item name labelling")
                content_instance.update(item)
            return content_instance

        def recursive_instanciation(dico):
            content_instance = []
            for key, item in dico.items():
                if isinstance(item, list):
                    try:
                        item = list_to_dict(item)
                    except (TypeError, ValueError):  # the content is not a category but a list containing values
                        element = JsonParam(name=key, value=item)
                if hasattr(item, "keys"):
                    item = recursive_instanciation(item)
                    element = JsonCategory(name=key, content=item)
                else:
                    element = JsonParam(name=key, value=item)
                content_instance.append(element)
            return content_instance

        instanciated_content = recursive_instanciation(dico)
        return cls(instanciated_content)

    @classmethod
    def from_jsonbd_list(cls, content):
        if content is None :#for cases where content was null or None (identical)
            return cls(instanciated_content)
        if isinstance(content,dict):
            if len(content):#for cases where content was rooted by JsonRoot.get_rooted()
                content = content["parameters"]
            else :# for cases where content was {}
                content = []

        instanciated_content = []
        for item in content:
            if "value" in item.keys():
                instanciated_item = JsonParam.from_dict(item)
            elif "content" in item.keys():
                instanciated_item = JsonCategory.from_dict(item)
            else:
                raise KeyError(
                    f"The item {item} does not have a value not a content key, and cannot be processed in a jsonparam file.")
            instanciated_content.append(instanciated_item)

        instanciated_content = sorted(
            instanciated_content, key=lambda item: item.name)
        return cls(instanciated_content)

    @classmethod
    def from_json_string(cls, string):
        dico = json.loads(string)
        return cls.from_json_dict(dico)

    @classmethod
    def from_jsondb_string(cls, string):
        content = json.loads(string)
        return cls.from_jsonbd_list(content)
    #endregion

    # OUTPUT METHODS
    def __as_str__(self, item=None):
        if item is None:
            item = self
        return json.dumps(item, indent=2, ensure_ascii=False)

    def get_digest(self):
        digest = {}
        [digest.update(content.get_digest())
         for content in self if content.is_shown]
        return digest

    def get_jsondb_string(self):
        return self.__as_str__(self)

    def get_json_string(self):
        return self.__as_str__(self.get_digest())

    def get_rooted(self):
        return {"parameters":self}

if __name__ == "__main__":

    mijson = JsonRoot.from_file("toast.json")
