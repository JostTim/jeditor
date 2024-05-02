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
Created on Wed Mar  8 12:07:45 2023
@author: Timothe
</div>
"""

from PyQt5.QtWidgets import (QMainWindow,
                             QApplication,
                             QStyleFactory,
                             QWidget, 
                             QMenu,
                             QMessageBox,
                             QCheckBox, 
                             QPushButton,
                             QLineEdit,
                             QPlainTextEdit,
                             QLabel,
                             QFrame,
                             QDialog,
                             QTabWidget,
                             #QGridLayout,
                             QHBoxLayout,
                             QVBoxLayout,
                             QGraphicsOpacityEffect,
                             QFileDialog,
                             QScrollArea,
                             QUndoStack,
                             QSizePolicy,
                             QComboBox)


from qtwidgets import PasswordEdit as QPasswordEdit #pip install qtwidgets
from pyqtspinner import WaitingSpinner as QWaitingSpinner #pip install pyqtspinner
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread#, QSize
from queue import Queue
from PyQt5.QtGui import QIcon, QColor,  QKeySequence, QFontDatabase, QPalette #,QPainter, QPixmap
from qt_material import apply_stylesheet

from .core import JsonRoot
from .file_io import FileBasedJsonRoot
import os, logging

refresh_icon_path = os.path.join( os.path.dirname(__file__),"assets", r"refresh_button.svg")
app_icon_path = os.path.join( os.path.dirname(__file__),"assets", r"app_icon.svg")

class QHSeparationLine(QtWidgets.QFrame):
  '''
  a horizontal separation line\n
  '''
  def __init__(self):
    super().__init__()
    self.setMinimumWidth(1)
    self.setFixedHeight(1)
    self.setFrameShape(QFrame.HLine)
    self.setFrameShadow(QFrame.Sunken)
    self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

class QTitledComboBox(QComboBox):
    
    def __init__(self, title = "", parent=None):
        super().__init__(parent = parent)
        self.parent = parent

        self.addItem(title)
        item = self.model().item(0,0)
        item.setSelectable(False)

class QNewItemCheckBox(QTitledComboBox):
    open_param = pyqtSignal()
    open_category = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(title = "+",parent = parent)

        self.addItem("New category")
        self.addItem("New parameter")
        
        self.currentIndexChanged.connect(self.handle_item_pressed)
        self.setFixedWidth(50)
        #self.setModel(QStandardItemModel(self))
    
    def handle_item_pressed(self, index):
 
        # getting which item is pressed
        if index == 0 :
            return
        if index == 1 :
            self.open_category.emit()
        if index == 2 :
            self.open_param.emit()

class QDescriptionEditor(QDialog):

    # This is a much better way to extend __init__
    def __init__(self, parent = None, *args, **kwargs):            
        super().__init__(*args, **kwargs)
        self.parent = parent
        self.setWindowTitle(f"Edit '{self.parent.json_element.name}' description")
        self.button = QPushButton("Ok")
        self.button.clicked.connect(self.close)
        self.text_edit = QLineEdit(self.parent.json_element.description)
        self.text_edit.returnPressed.connect(self.close)
        
        l = QVBoxLayout()
        l.addWidget(self.text_edit)
        l.addWidget(self.button)
        self.setLayout(l)
        
    def get_text(self):
        return self.text_edit.text()
    
class QTypeEditor(QDialog):

    # This is a much better way to extend __init__
    def __init__(self, parent = None, *args, **kwargs):            
        super().__init__(*args, **kwargs)
        self.parent = parent
        self.setWindowTitle(f"Set '{self.parent.json_element.name}' variable type")
        self.button = QPushButton("Set")
        self.button.clicked.connect(self.close)
        self.text_edit = QLineEdit(self.parent.json_element.dtype)
        self.text_edit.returnPressed.connect(self.close)
        
        l = QVBoxLayout()
        l.addWidget(self.text_edit)
        l.addWidget(self.button)
        self.setLayout(l)
        
    def get_text(self):
        return self.text_edit.text()

class QDescriptionLabel(QLabel):
    double_clicked = pyqtSignal()
    pressed = pyqtSignal()
    released = pyqtSignal()
    
    def __init__(self, parent = None):
        self.parent = parent
        self.name =  parent.json_element.name
        self.description =  parent.json_element.description
        
        super().__init__(self.name , parent = parent)
        
        self.setToolTip(self.description)
        
        self.double_clicked.connect(self.description_edit_popup)
        
    def mousePressEvent(self, event):
        self.pressed.emit()
        
    def mouseReleaseEvent(self, event):
        self.released.emit()

    def mouseDoubleClickEvent(self, event):
        self.double_clicked.emit()

    def description_edit_popup(self):
    
        msgbox = QDescriptionEditor(parent = self.parent)
        _ = msgbox.exec()
        description = msgbox.get_text()
        self.parent.json_element["description"] = description
        self.parent.refresh_layout()
        
class QResetButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
        self.setIcon(QIcon(refresh_icon_path))
        self.setStyleSheet("disabled { background-color: gray ; color : gray}")
        self.opacity_effect = QGraphicsOpacityEffect()
        self.opacity_effect.setOpacity(1)
        self.setGraphicsEffect(self.opacity_effect)
        self.setMaximumWidth(45)
        
    def setEnabled(self,state):
        opacity = 1 if state else 0.3
        self.opacity_effect.setOpacity(opacity)
        super().setEnabled(state)

class QJsonParamEnabler(QWidget):
    
    def __init__(self, json_element, parent=None):
        super(QWidget, self).__init__(parent)
            
        self.json_element = json_element
        self.parent = parent
        
        name_label = QDescriptionLabel(parent = self)
        font = QFontDatabase().font("arial","bold", 9)
        name_label.setFont(font)
        
        self.showed_checkbox = QCheckBox("show",parent = self)
        self.showed_checkbox.setChecked(json_element.is_shown)
        self.showed_checkbox.stateChanged.connect(lambda : self.change_display_state())
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete)
        self.delete_button.setFixedHeight(35)
        
        self.edit_type_button = QPushButton("Edit Type")
        self.edit_type_button.clicked.connect(self.change_type)
        self.edit_type_button.setFixedHeight(35)
        
        l = QHBoxLayout()
        l.setSpacing(3)
        l.setContentsMargins(0, 0, 0, 0)
        l.addWidget(name_label, alignment = Qt.AlignLeft)
        #l.addStretch(1)
        l.addWidget(QHSeparationLine())
        
        sl = QHBoxLayout()
        sl.setContentsMargins(0,0,0,0)
        sl.setSpacing(3)
        sl.addWidget(self.showed_checkbox, alignment = Qt.AlignRight)
        sl.addWidget(self.edit_type_button, alignment = Qt.AlignRight)
        sl.addWidget(self.delete_button, alignment = Qt.AlignRight)
        l.addLayout(sl, stretch = 0 )

        self.setLayout(l)
        
    def delete(self):
        mb = QDeleteMessage(name = self.json_element.name, type = "parameter")
        delete = mb.execute()
        if delete :
            try :#if parent is JsonRoot(list)
                index = self.parent.json_element.index(self.json_element)
                self.parent.json_element.pop(index)
            except :#if parent is JsonCategory(dict)
                index = self.parent.json_element["content"].index(self.json_element)
                self.parent.json_element["content"].pop(index)
            self.parent.refresh_layout()
            self.parent.modified()
        
    def change_display_state(self):
        if self.showed_checkbox.isChecked():
            self.json_element.show()
        else :
            self.json_element.hide()
            
    def change_type(self):
        box = QTypeEditor(self)
        box.exec()
        dtype = box.get_text()
        self.json_element.set_type(dtype)

    def refresh_layout(self):
        self.parent.refresh_layout()    

class QJsonParamEditor(QWidget):
    
    def __init__(self, json_element, parent=None):
        super().__init__(parent)
        
        self.json_element = json_element
        self.parent = parent
        
        name_label = QDescriptionLabel(parent = self)
        font = QFontDatabase().font("arial","bold", 9)
        name_label.setFont(font)
        
        self.reset_to_default = QResetButton(parent = self)
        self.reset_to_default.clicked.connect(self.set_value_to_default)
        self.reset_to_default.setEnabled(not self.json_element.is_default)

        self.value_edit = QLineEdit(parent = self)
        self.value_edit.returnPressed.connect(self.update_value)
        self.value_edit.setText(str(self.json_element.value))
        self.value_edit.setFixedWidth(250)
        
        l = QHBoxLayout()
        l.setSpacing(3)
        l.setContentsMargins(0, 0, 0, 0)
        l.addWidget(name_label, alignment = Qt.AlignLeft)
        #l.addStretch(1)
        
        l.addWidget(QHSeparationLine())
        
        sl = QHBoxLayout()
        sl.setContentsMargins(0,0,0,0)
        sl.setSpacing(3)
        sl.addWidget(self.reset_to_default, alignment = Qt.AlignRight)
        sl.addWidget(self.value_edit, alignment = Qt.AlignRight)
        l.addLayout(sl, stretch = 0 )
        
        #self.setFixedHeight(50)
        self.setLayout(l)
        
    def set_value_to_default(self):
        #self.reset_to_default.setVisible(False)
        self.reset_to_default.setEnabled(False)
        self.json_element.reset_value()
        self.value_edit.setText(str(self.json_element.value))
        self.parent.modified()
        
    def update_value(self):
        import json
        value = self.value_edit.text()
        try :
            value = json.loads()
        except :
            pass
        self.json_element.set_value(value)
        self.value_edit.setText(str(self.json_element.value))

        if self.json_element.value != self.json_element.default :
            self.reset_to_default.setEnabled(True)
        else :
            self.reset_to_default.setEnabled(False)
        self.parent.modified()  
        
    def refresh_layout(self):
        self.parent.refresh_layout()
        
class QJsonAdder(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
        self.label = QLabel("Add Element")
        
        font = QFontDatabase().font("arial","bold", 9)
        self.label.setFont(font)
        
        self.value_label = QLabel("Value : ")
        self.value_label.setVisible(False)
        
        self.add_button = QNewItemCheckBox()
        self.add_button.open_param.connect(self.edit_param)
        self.add_button.open_category.connect(self.edit_category)
        self.add_button.setFixedHeight(35)
        
        self.name_edit = QLineEdit(parent = self)
        self.value_edit = QLineEdit(parent = self)
        self.name_edit.setVisible(False)
        self.value_edit.setVisible(False)
        self.name_edit.setMaximumHeight(45)
        self.value_edit.setMaximumHeight(45)
        
        self.valid_button = QPushButton("Done")
        self.valid_button.setVisible(False)
        self.add_button.setFixedHeight(35)
        
        self.setMaximumHeight(50)
        
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(2, 0, 2, 0)
        self.layout.setSpacing(3)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.add_button)
        self.layout.addWidget(self.name_edit)
        self.layout.addWidget(self.value_label)
        self.layout.addWidget(self.value_edit)
        self.layout.addWidget(self.valid_button)
        
        self.setLayout(self.layout)
        
    def edit_category(self):
        self.label.setText("Add Category")
        self.layout.insertWidget(1,QLabel("Name : "))
        self.add_button.setVisible(False)
        self.name_edit.setVisible(True)
        self.valid_button.setVisible(True)
        self.valid_button.clicked.connect(self.finish_category)
        self.name_edit.returnPressed.connect(self.finish_category)
        
    def edit_param(self):
        self.label.setText("Add Parameter")
        self.layout.insertWidget(1,QLabel("Name : "))
        self.add_button.setVisible(False)
        self.name_edit.setVisible(True)
        self.value_edit.setVisible(True)
        self.valid_button.setVisible(True)
        self.value_label.setVisible(True)
        self.valid_button.clicked.connect(self.finish_param)
        
    def get_name(self):
        return self.name_edit.text()
    
    def get_value(self):
        import json
        value = self.value_edit.text()
        try :
            value = json.loads()
        except :
            pass
        return value
    
    def finish_param(self):
        self.parent.json_element.add_param(name = self.get_name(), value = self.get_value())
        self.parent.refresh_layout()
        self.parent.modified()
    
    def finish_category(self):
        self.parent.json_element.add_category(name = self.get_name(), content = [], is_shown = True)
        self.parent.refresh_layout()
        self.parent.modified()

class QJsonCategory(QFrame):
    
    def __init__(self, json_element, parent = None):
        
        super().__init__(parent)
        self.parent = parent
        self.json_element = json_element
        
        self.layout = QVBoxLayout()
        self.build_layout()
        self.setLayout(self.layout)
        self.sizePolicy().setVerticalPolicy(QSizePolicy.Fixed)
        self.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.layout.setSpacing(3)
        
    def select_items(self, require_shown = False):
        
        #require_show = False to get all the items (even the ones hidden)
        #not shown = False to get only the ones that are shown
        not_shown = not require_shown 
        
        self.categories_holders = []
        self.params_holders = []
        
        for item in self.json_element.params :
            if not_shown or item.is_shown:
                if self.layout_mode == "editor" :    
                    self.params_holders.append(QJsonParamEditor(item, parent = self))
                elif self.layout_mode == "enabler" : 
                    self.params_holders.append(QJsonParamEnabler(item, parent = self))
        
        for item in self.json_element.categories :
            if not_shown or item.is_shown:
                self.categories_holders.append(QJsonCategory(item, parent = self))
        
    def build_layout(self):
    
        try :
            name_label = QDescriptionLabel(parent = self)  
            font = QFontDatabase().font("arial","black", 14)
            name_label.setFont(font)
            name_label.setFixedHeight(20)
            
            sl = QHBoxLayout()
            sl.addWidget(name_label, alignment = Qt.AlignLeft)
            self.layout.addLayout(sl)
            self.layout.addWidget(QHSeparationLine())

            self.layout.setContentsMargins(5, 5, 5, 5)
            self.setStyleSheet("QFrame {border-width: 1;}")
            
        except AttributeError: # not able to do this on json root (no name nor decription)
            self.setStyleSheet("QFrame {border-width: 0;}")
            self.layout.setContentsMargins(0,0,0,0)
        
        if self.layout_mode == "editor" :
            require_shown = True 
            
        elif self.layout_mode == "enabler" :
            require_shown = False 
            try :
                QChek_map = {True: Qt.Checked,False : Qt.Unchecked ,None : Qt.PartiallyChecked}
                checkstate = QChek_map[self.json_element["is_shown"]]
                
                self.showed_checkbox = QCheckBox("show",parent = self)
                self.showed_checkbox.setTristate( True )
                self.showed_checkbox.setCheckState(checkstate)
                self.showed_checkbox.stateChanged.connect(lambda : self.change_display_state())
                
                self.delete_button = QPushButton("Delete")
                self.delete_button.clicked.connect(self.delete)
                
                ssl = QHBoxLayout()
                ssl.addWidget(self.showed_checkbox)
                ssl.addWidget(self.delete_button)
                
                sl.addStretch(1)
                sl.addLayout(ssl)
            except TypeError: # not able to do this on json root (no keys so no is_shown)
                pass
            
        else :
            raise ValueError(f"layout build with app layout_mode set to {self.layout_mode}")
        
        self.select_items(require_shown)
        
        
        for item in self.categories_holders + self.params_holders :
            self.layout.addWidget(item,alignment = Qt.AlignTop )
        
        if self.layout_mode == "enabler" :
            self.build_add_option()
            
        self.layout.addStretch(1)
    
    def build_add_option(self):
        
        self.add_button = QJsonAdder(parent = self)
        self.layout.addWidget(self.add_button, alignment = Qt.AlignTop)
        
    def clear_layout(self):
        
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
    def refresh_layout(self):
        self.clear_layout()
        self.build_layout()
        
    def change_display_state(self):
        QChek_map = {Qt.Checked : True ,Qt.Unchecked : False, Qt.PartiallyChecked : None}
        self.json_element["is_shown"] = QChek_map[ self.showed_checkbox.checkState() ]
        
    @property
    def layout_mode(self):
        return self.parent.layout_mode
    
    def delete(self):
        mb = QDeleteMessage(name = self.json_element.name, type = "category")
        delete = mb.execute()
        if delete :
            try :#if parent is JsonRoot(list)
                index = self.parent.json_element.index(self.json_element)
                self.parent.json_element.pop(index)
            except :#if parent is JsonCategory(dict)
                index = self.parent.json_element["content"].index(self.json_element)
                self.parent.json_element["content"].pop(index)
            self.parent.refresh_layout()
            self.parent.modified()
        
    def modified(self):
        self.parent.modified()

class QDeleteMessage(QMessageBox):

    # This is a much better way to extend __init__
    def __init__(self, name, type, *args, **kwargs):            
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Delete ?")
        self.setText(f"Are you sure you want to delete {type} {name}")
        self.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
        self.setIcon(QMessageBox.Warning)
        
    def execute(self):
        self.exec_()
        if self.clickedButton() is self.button(QMessageBox.Yes):
            return True
        elif self.clickedButton() is self.button(QMessageBox.No):
            return False
        return False#"not button clicked probably closed the button box"

class JsonResultDialog(QDialog):

    # This is a much better way to extend __init__
    def __init__(self, text, *args, **kwargs):            
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Json Result")
        self.button = QPushButton("Copy to clipboard")
        self.button.clicked.connect(self.copy_to_clipboard)
        self.text_edit = QPlainTextEdit(text)
        
        l = QVBoxLayout()
        l.addWidget(self.button)
        l.addWidget(self.text_edit)
        self.setLayout(l)
        
    def copy_to_clipboard(self):
        cb = QApplication.clipboard()
        cb.clear(mode = cb.Clipboard)
        cb.setText(self.text_edit.toPlainText(), mode = cb.Clipboard)
        self.button.setText("Copied")

class JsonParamEditorPannel(QWidget):
    
    def __init__(self, parent = None):
        super().__init__(parent = parent)
        self.parent = parent
        
        self.build_central_widget()
        self.build_toolbar()
        self.build_title_bar()

        v = QVBoxLayout()
        v.setContentsMargins(5, 5, 5, 5)
        v.setSpacing(5)
        v.addWidget(self.title_bar)
        v.addWidget(self.toolbar)
        v.addWidget(self.scroll_area)
        self.setLayout(v)
        
        self.initialize_working_vars()
        self.build_non_initialized_layout()
        self.build_polymenu()
        
    def close_pannel(self):
        self.parent.layout.deleteLater(self)    
    
    def initialize_working_vars(self):        
        
        self.saved = True
        self.json_root = None
        self.layout_mode = None
        
    def modified(self):
        self.saved = False    
    
    def handle_unsaved_changes(self):
        if not self.saved :
            result = QMessageBox.question(self,
                                        "Save File ?",
                                        """Unsaved modifications have been detected, do you want to save file before closing ?
Press ignore to close anyway, or abort to continue editing the file.""",
                                        QMessageBox.Save | QMessageBox.Ignore | QMessageBox.Abort)
            if result == QMessageBox.Save:
                self.save()
            elif result == QMessageBox.Ignore:
                pass
            elif result == QMessageBox.Abort:# QMessageBox.Cancel
                return False
        return True
    
    def digest_direct_to_clipboard(self):
        if self.json_root is None :
            return
        cb = QApplication.clipboard()
        cb.clear(mode = cb.Clipboard)
        cb.setText(self.json_root.get_json_string(), mode = cb.Clipboard)
    
    def show_json(self):
        if self.json_root is not None :
            msg = JsonResultDialog(self.json_root.get_json_string()) 
            _ = msg.exec_()
    
    def show_full_json(self):
        if self.json_root is not None :
            msg = JsonResultDialog(self.json_root.get_jsondb_string())   
            _ = msg.exec_()
            
    
    # def update_display(self):
    #     return
    #     #TODO : make widgets searchable.
    #     # this example below may be usefull to set widgets lightlighted / active looking
    #     color = (QPalette.Active, QPalette.Highlight, QColor("black"))
    #     self.found_widget.setPalette(self.found_widget.palette().setColor(*color))
    
    #### LAYOUT MANAGEMENT
    
    def build_central_widget(self):
        self.central_widget = QWidget()
        
        self.layout = QHBoxLayout()
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.central_widget.setLayout(self.layout)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.central_widget)
        
        self.scroll_area.setFrameStyle(QFrame.NoFrame)
        
    def build_title_bar(self):
        self.title_bar = QWidget()

        self.title_bar.title = QLabel()
        font = QFontDatabase().font("arial","black", 14)
        self.title_bar.title.setFont(font)

        h = QHBoxLayout()
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(5)

        label = QLabel("Currentely Editing :")
        font = QFontDatabase().font("arial","normal", 14)
        label.setFont(font)

        h.addWidget(label)
        h.addWidget(self.title_bar.title)
        h.addStretch(0)

        self.title_bar.setLayout(h)
    def build_toolbar(self):
        
        self.toolbar = QWidget()
        
        self.switch_layout_button = QPushButton("Switch")
        self.switch_layout_button.clicked.connect(self.switch_layout_mode)
        
        self.searchbar = QLineEdit()        
        #self.searchbar.textChanged.connect(self.update_display)
        #TODO : make searchbar working
        
        h = QHBoxLayout()
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(5)
        
        h.addWidget(self.switch_layout_button,alignment = Qt.AlignLeft)
        h.addStretch(0)
        h.addWidget(QLabel("Search :"))
        h.addWidget(self.searchbar)
        
        self.toolbar.setLayout(h)
        
    def build_enabler_layout(self):        
        if self.json_root is None :
            QMessageBox.warning(self,"Warning","You must open or create a file first")
            return     
        self.clear_layout()
        self.layout_mode = "enabler"
        self.json_widget = QJsonCategory(self.json_root, parent = self)
        self.layout.addWidget(self.json_widget)
        self.toolbar.setVisible(True)
        self.setMinimumWidth(500)
        self.switch_layout_button.setText("Edit mode")
        
    def build_editor_layout(self):
        if self.json_root is None :
            QMessageBox.warning(self,"Warning","You must open or create a file first")
            return 
        self.clear_layout()
        self.layout_mode = "editor"
        self.json_widget = QJsonCategory(self.json_root, parent = self)
        self.toolbar.setVisible(True)
        self.title_bar.setVisible(True)
        self.setMinimumWidth(500)
        self.switch_layout_button.setText("Settings mode")
        self.build_edit_menu()

    def build_non_initialized_layout(self):
        self.clear_layout()
        self.layout_mode = None
        self.toolbar.setVisible(False)
        self.title_bar.setVisible(False)
        
    def build_current_layout(self):
        if self.layout_mode == "editor":
            self.build_editor_layout()  
        elif self.layout_mode == "enabler":
            self.build_enabler_layout()  
        else  :
            self.build_non_initialized_layout()
        
    def switch_layout_mode(self):
        if self.layout_mode == "editor":
            self.build_enabler_layout()  
        elif self.layout_mode == "enabler":
            self.build_editor_layout()  
        else  :
            return
        
    def clear_layout(self):

        def recursive_layout_clearing(layout):
            if layout is None :
                return
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
                else :
                    recursive_layout_clearing(child.layout())

        recursive_layout_clearing(self.layout)

    def build_polymenu(self):

        self.parent.polymenu.addAction('&Edit from file', self.morph_into_FilePannel) 
        self.parent.polymenu.addAction('&Edit from alyx', self.morph_into_AlyxPannel)

    def build_edit_menu(self):

        edmenu = self.parent.editmenu
        edmenu.clear()
        # TODO : ADD UNDO REDO ABILITY
        
        # self.undo_stack = QUndoStack(self)
        # #undo, redo = self.undo_stack.undo, self.undo_stack.redo
        # undoAction = self.undo_stack.createUndoAction(self, "Undo")
        # undoAction.setShortcuts(QKeySequence.Undo)
        # redoAction = self.undo_stack.createRedoAction(self, "Redo")
        # redoAction.setShortcuts(QKeySequence.Redo)
        
        #editMenu.addAction('&Undo',self.undo_stack.undo, Qt.CTRL + Qt.Key_Z)
        #editMenu.addAction('&Redo',self.undo_stack.redo, Qt.CTRL + Qt.Key_Y)
        #self.file_menu.addSeparator()
        edmenu.addAction('&Variable editor',self.build_editor_layout)
        edmenu.addAction('&Variable enabler',self.build_enabler_layout)
        edmenu.addSeparator()
        
        edmenu.addAction('&Json Result to clipboard',self.digest_direct_to_clipboard, Qt.CTRL + Qt.SHIFT + Qt.Key_C)
        edmenu.addAction('&Show Json Result',self.show_json, Qt.CTRL + Qt.Key_R)
        edmenu.addAction('&Show Full Json Result',self.show_full_json)


    def morph_into_FilePannel(self):
        if not self.handle_unsaved_changes() :
            return 
        FilePannel = JsonParamFilePannel(parent = self.parent)
        
        self.parent.modification_pannel = FilePannel
        self.parent.setCentralWidget(FilePannel)
        self.clear_layout()
        self.deleteLater()
        
    def morph_into_AlyxPannel(self):
        if not self.handle_unsaved_changes() :
            return 
        AlyxPannel = JsonParamAlyxPannel(parent = self.parent)
        
        self.parent.modification_pannel = AlyxPannel
        self.parent.setCentralWidget(AlyxPannel)
        self.clear_layout()
        self.deleteLater()        

class ConnexionWorker(QObject):
    from one.api import OneAlyx
    from requests import HTTPError

    succeded = pyqtSignal()
    failed = pyqtSignal(str)

    def __init__(self,base_url,username,password, queue):
        super().__init__()
        self.password = password
        self.username = username
        self.base_url = base_url
        self.queue = queue

    def run(self):
        """Long-running task."""
        try :
            connector = self.OneAlyx.__wrapped__(base_url=self.base_url, 
                                mode = "remote", 
                                username = self.username, 
                                password = self.password, 
                                silent = True)
            self.queue.put(connector)
            self.succeded.emit()
        except (ConnectionError, self.HTTPError) as e :
            #either adress does not exist or unreachable (ConnectionError)
            #or password / username parameters are wrong (HTTPError)
            self.failed.emit("Could not connect to alyx database.\nReason evoked :\n"+e.__str__())
        except Exception as e :
            self.failed.emit("Unknown error :"+e.__str__())

#region: EDITOR PANNELS

class JsonParamAlyxPannel(JsonParamEditorPannel):
          
    def initialize_working_vars(self):
        super().initialize_working_vars()
        self.connector = None
        self.project = None
        self.session_id = None
    
    def manage_connexion_error(self,error):
        logging.warning('ERROR')
        QMessageBox.warning(self,"Warning",error)
        self.thread.quit()
        self.thread.deleteLater()
        self.worker.deleteLater()
        self.connexion_waiter.stop()

    def manage_connexion_success(self):
        logging.info('SUCESS')
        self.connector = self.queue.get(False)
        self.worker.deleteLater()
        self.thread.quit()
        self.thread.deleteLater()
        self.connexion_waiter.stop()
        self.build_edit_selection_layout()

    def connect_to_alyx(self):
        
        from one.api import OneAlyx
        from requests import HTTPError

        url = self.alyx_adress_field.text()
          
        password = self.password_field.text()
        username = self.user_field.text()

        self.connexion_waiter.start()

        self.queue = Queue()

        self.thread = QThread()
        self.worker = ConnexionWorker(url,username,password,self.queue)
        self.worker.moveToThread(self.thread)
        self.worker.succeded.connect(self.manage_connexion_success)
        self.worker.failed.connect(self.manage_connexion_error)
        self.thread.started.connect(self.worker.run)
        self.thread.start()
        
    def load_jsondb_from_defaultparams(self):
        
        json_content = self.connector.alyx.rest("projects","read","DefaultParameterProject")["json"]
        return JsonRoot.from_jsonbd_list(json_content)
         
    #### LAYOUT BUILDING
    
    def build_polymenu(self):
        
        dbmenu = self.parent.polymenu
        dbmenu.clear()
        dbmenu.addAction('&Open', self.build_edit_selection_layout, Qt.CTRL + Qt.Key_O) 
        dbmenu.addAction('&Save', self.save_selection, Qt.CTRL + Qt.Key_S) 
        dbmenu.addSeparator()
        dbmenu.addAction('&File editor', self.morph_into_FilePannel) 

    def build_edit_selection_layout(self):
        if not self.handle_unsaved_changes() :
            return
        self.connector.alyx.delete_cache()
        self.json_root = None

        if not self.handle_unsaved_changes():
            return

        super().build_non_initialized_layout()
        
        project_select_container = self.create_project_select_container()
        session_select_container = self.create_session_select_container()

        plabel = QLabel("Edit a project parameters")
        slabel = QLabel("Edit a session parameters")
        font = QFontDatabase().font("arial","black", 12)
        plabel.setFont(font)
        slabel.setFont(font)

        hc = QVBoxLayout()
        
        hc.addWidget(slabel)
        hc.addWidget(session_select_container)

        hc.addStretch(1)

        hc.addWidget(plabel)
        hc.addWidget(project_select_container)

        self.layout.addLayout(hc)

    def create_session_select_container(self):

        self.session_id_field = QLineEdit()
        open_session_button = QPushButton("Open")
        open_session_button.clicked.connect(self.open_session)
        label = QLabel("Session label :")
        ToolTip = """Either :
        - an unique name (ex : wm25/2022-08-05/003)
        - an unique id (ex : 3eb05bbe-effd-4e0f-943e-a87234e9cfff)
        - or an url (ex : http://157.99.138.172:8080/admin/actions/session/3eb05bbe-effd-4e0f-943e-a87234e9cfff)"""
        label.setToolTip(ToolTip)
        self.session_id_field.setToolTip(ToolTip)

        label.setBuddy(self.session_id_field)
        ha = QVBoxLayout()
        ha.addWidget(label)
        ha.addWidget(self.session_id_field)
        ha.addWidget(open_session_button)

        session_select_container = QFrame()
        session_select_container.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        session_select_container.setLayout(ha)
        return session_select_container
    
    def create_project_select_container(self):
        
        projects_names = [item["name"] for item in self.connector.alyx.rest("projects","list")]
        
        combo = QTitledComboBox("Select :")
        for item in projects_names:
            combo.addItem(item)
            
        combo.textActivated.connect(self.open_project)
        combo.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

        label = QLabel("Project's template :")
        label.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        label.setBuddy(combo)
        
        ha = QVBoxLayout()
        ha.addWidget(label,Qt.AlignCenter)
        ha.addWidget(combo,Qt.AlignTop)

        project_select_container = QFrame()
        project_select_container.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        project_select_container.setLayout(ha)

        return project_select_container

    def open_session(self,session_id):
        def fix_url(url_input):
            import re
            return re.sub(r"^(https?:\/\/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5})(\/)(session)(s)(.*)$",r"\g<1>/admin/actions/\g<3>\g<5>",url_input)

        session_id = self.session_id_field.text().replace(" ","")
        if session_id == "":
            return
        session_id = session_id.split("/change")[0] #in case it is an url, we remove things after change
        
        try :
            session_id = self.connector.to_eid(session_id)
        except ValueError as e:
            QMessageBox.warning(self,"Warning","Impossible to open session : " + e.__str__())
            return
        s_results = self.connector.alyx.rest("sessions","read",id = session_id)
        self.session_id = session_id

        self.json_root = self.load_jsondb_from_defaultparams()
        jsondb_list = self.connector.alyx.rest("projects","read",s_results["projects"][0])["json"]
        json_instance = JsonRoot.from_jsonbd_list(jsondb_list)
        self.json_root.set_elements_from_instance(json_instance,["is_shown","default"])
        session_json = s_results["json"]
        json_instance = JsonRoot.from_json_dict(session_json)
        self.json_root.set_elements_from_instance(json_instance,["value"])

        session_text = f"Session : {s_results['subject']}\{s_results['start_time'][:10]}\{str(s_results['number']).zfill(3)}"
        self.title_bar.title.setText(f'<a href="{fix_url(s_results["url"])}">{session_text}</a>')
        self.title_bar.title.setOpenExternalLinks(True)
        self.project = None

        self.build_session_layout()

    def build_session_layout(self):
        
        self.build_editor_layout()
        self.toolbar.setVisible(False)
        
    def open_project(self,project):
        
        self.json_root = self.load_jsondb_from_defaultparams()
        self.project = project
        
        if self.project != "DefaultParameterProject":           
        
            jsondb_list = self.connector.alyx.rest("projects","read",self.project)["json"]
            json_instance = JsonRoot.from_jsonbd_list(jsondb_list)

            self.json_root.set_elements_from_instance(json_instance,["value","is_shown","default"])

        self.build_editor_layout()
        self.title_bar.title.setText("Project : "+self.project)
        self.title_bar.title.setOpenExternalLinks(False)

        self.session_id = None

    def build_non_initialized_layout(self):
        super().build_non_initialized_layout()
        self.json_root = None

        open_button = QPushButton("Connect to Alyx")
        open_button.clicked.connect(self.connect_to_alyx)
        open_button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        connexion_waiter_parent = QWidget()

        self.connexion_waiter = QWaitingSpinner(
                                    parent = connexion_waiter_parent,
                                    roundness=0.0,
                                    fade=90.0,
                                    radius=10,
                                    lines=60,
                                    line_length=5,
                                    line_width=2,
                                    speed=0.6,
                                    color= QColor(0, 85, 255)
                                )
        
        self.connexion_waiter.setMinimumHeight(50)
        self.connexion_waiter.start()
        self.connexion_waiter.stop()

        self.alyx_adress_field = QLineEdit('http://157.99.138.172:8080')
        self.password_field = QPasswordEdit()
        self.user_field = QLineEdit('tjostmou')
        self.password_field.setEchoMode(QLineEdit.Password)
        
        ha = QHBoxLayout()
        ha.addWidget(self.user_field)
        ha.addWidget(self.password_field)
        
        va = QVBoxLayout()
        va.addWidget(self.alyx_adress_field)
        va.addLayout(ha)
        
        v = QVBoxLayout()
        v.addWidget(open_button)
        v.addWidget(self.connexion_waiter)
        v.addLayout(va)
        
        self.layout.addLayout(v)

    def save_selection(self):
        if self.project is None :
            self.save_to_session()
        elif self.session_id is None :
            self.save_to_project()
        else :
            QMessageBox.warning(self,"Warning","Cannot save, neither session or project are currentely being edited")

    def save_to_project(self):
        if self.json_root is None :
            return  
        if self.project is None :
            QMessageBox.warning(self,"Warning","Cannot save to project, not currentely editing a project.")
            return
        
        if self.project != "DefaultParameterProject" :
            default_project_params = self.load_jsondb_from_defaultparams()
            #TODO : add a chekup to verify that the number of element is eigther same or increasing before partial updating
            default_project_params.add_elements_from_instance(self.json_root)
            self.connector.alyx.rest("projects",
                                     "partial_update", 
                                     id = "DefaultParameterProject",
                                     data = {"json":default_project_params.get_rooted()})
        
        self.connector.alyx.rest("projects",
                                 "partial_update", 
                                 id = self.project,
                                 data = {"json":self.json_root.get_rooted()})
        self.saved = True
        
    def save_to_session(self):
        if self.session_id is None :
            QMessageBox.warning(self,"Warning","Cannot save to session, not currentely editing a session.")
            return
        self.connector.alyx.rest("sessions",
                                 "partial_update", 
                                 id = self.session_id,
                                 data = {"json":self.json_root.get_digest()})
        self.saved = True

class JsonParamFilePannel(JsonParamEditorPannel):
        
    def initialize_working_vars(self):
        super().initialize_working_vars()
        self.file_name = ""
        
    #### LAYOUT BUILDING
    
    def build_non_initialized_layout(self):
        super().build_non_initialized_layout()
        open_button = QPushButton("Open File")
        open_button.clicked.connect(self.open_file_dialog)
        open_button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        
        self.layout.addWidget(open_button)
    
    def build_polymenu(self):
        fmenu = self.parent.polymenu
        
        fmenu.clear()

        fmenu.addAction('&Open', self.open_file_dialog)
        fmenu.addAction('&New', self.create_new_instance, Qt.CTRL + Qt.Key_N) 
        fmenu.addAction('&Save', self.save, Qt.CTRL + Qt.Key_S)
        fmenu.addAction('&Save as', self.save_as_dialog , Qt.CTRL + Qt.SHIFT + Qt.Key_S)
        
        fmenu.addSeparator()
        fmenu.addAction('&Import values from file', self.import_values_from_json_file)
        fmenu.addAction('&Export digest', self.export_digest, Qt.CTRL + Qt.SHIFT + Qt.Key_E)
        
        fmenu.addSeparator()
        fmenu.addAction('&Close File', self.close_file)
    
        fmenu.addSeparator()
        
        fmenu.addAction('&Alyx editor', self.morph_into_AlyxPannel) 
    
    #### FILE HANDLING
    
    def open_file_dialog(self):
        
        options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Open a json file", "","Json Parameters Files (*.jsondb);;Json Files (*.json);;All Files (*)", options=options)
        if fileName :
            extension = os.path.splitext(fileName)[1]
            if  extension == ".json" :
                self.import_json_file(fileName)
            elif extension == ".jsondb" :
                self.open_jsondb_file(fileName)
            else :
                raise NotImplementedError()
            
    def open_jsondb_file(self,file):
        if not os.path.isfile(file):
            return
        self.file_name = file
        self.json_root = FileBasedJsonRoot.from_jsondb_file(self.file_name)
        self.build_editor_layout()
    
    def import_json_file(self,file):
        if not os.path.isfile(file):
            return
        self.json_root = FileBasedJsonRoot.from_json_file(file)
        self.build_editor_layout()
        
    def import_values_from_json_file(self):
        if self.json_root is None :
            QMessageBox.warning(self,"Warning","You must open or create a .jsondb file before importing previous values from a .json digest")
            return 
        options = QFileDialog.Options()
        file, _ = QFileDialog.getOpenFileName(self,"Open a json file", "","Json Files (*.json);;All Files (*)", options=options)
        if not os.path.isfile(file):
            return
        imported_json_root = FileBasedJsonRoot.from_json_file(file)
        self.json_root.set_values_from_instance(imported_json_root)
        self.build_current_layout()
        
    def save(self):
        if self.json_root is None :
            QMessageBox.warning(self,"Warning","Impossible to save : no file is being edited.")
            return
        if self.file_name == "":
            self.save_as_dialog()
            return
        self.json_root.to_file(self.file_name)
        self.saved = True
       
    def save_as_dialog(self):
        if self.json_root is None :
            QMessageBox.warning(self,"Warning","Impossible to save : no file is being edited.")
            return 
        
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self,"Save json file to","","Json Files (*.jsondb);;All Files (*)", options=options)
        if fileName:
            self.file_name = fileName
            self.save()
            
    def export_digest(self):
        if self.json_root is None :
            QMessageBox.warning(self,"Warning","Impossible to save : no file is being edited.")
            return 
        
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self,"Export digest json file to","","Json Files (*.json);;All Files (*)", options=options)
        if file_name:
            self.json_root.to_file(file_name, self.json_root.get_json_string())
            
    def create_new_instance(self):
        if self.close_file():
            self.json_root = FileBasedJsonRoot([])
            self.build_enabler_layout()        
    
    def close_file(self):
        if self.handle_unsaved_changes() :
            self.build_non_initialized_layout()
            self.initialize_working_vars()
            return True
        return False
        
class JsonParamEditorApp(QMainWindow):
    
    def __init__(self,title= None, application = None):
        
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        if title is None :
            title = "Application main window"
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(app_icon_path))
        
        self.polymenu = QMenu('&Json Params', self)
        self.editmenu = QMenu('&Edit', self)
        self.menuBar().addMenu(self.polymenu)
        self.menuBar().addMenu(self.editmenu)
        
        self.modification_pannel = JsonParamEditorPannel(parent = self)
        
        self.build_help_menu()
                
        self.setCentralWidget(self.modification_pannel)  

        self.setGeometry(500, 500, 300, 250)
        apply_stylesheet(application, theme='light_blue.xml')

        self.show()
        
    def closeEvent(self, event):
        if self.modification_pannel.handle_unsaved_changes() :
            event.accept()
        else :
            event.ignore()

    def about(self):
        QMessageBox.about(self, "About", """JEditor is a Json nested parameters editor.\n
It's principle is insipred by the neatly built and user friendly yet totally parametrable options of 
the software CURA, developped by Ultimaker. Here the goal is to make values of Json parameters
easily modifiable, while keeping a base of parameters names consistant, and still keeping a digest
view as the base grows and not all parameters are used at the same time (by being able to hide them).
This in turn can be used to add flexible yet consistant parameters to striclty built SQL databases.
It is developped by Timothé Jost-Mousseau and is openly accessible on Github and Gitlab. 
Link : https://gitlab.pasteur.fr/haisslab/data-management/jeditor""")
            
    def build_help_menu(self):
        from .__init__ import __version__
        help_menu = QMenu('&Help', self)
        help_menu.addAction('&Quit App', self.close)
        help_menu.addAction('&About', self.about)
        help_menu.addAction('&Version', lambda : QMessageBox.about(self, "Version", "Current version is : " + __version__))
        self.menuBar().addMenu(help_menu)

#endregion

def JEditor():
    import sys
    from.__init__ import __version__
    qApp = QApplication(sys.argv)
    _ = JsonParamEditorApp("JEditor",qApp)
    try:
        from ctypes import windll  # Only exists on Windows.
        myappid = 'Pasteur.HaissLab.JEditor.'+__version__
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except ImportError:
        pass
    sys.exit(qApp.exec_())
    