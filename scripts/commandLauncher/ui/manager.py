# coding:utf-8

__author__ =  'timmyliang'
__email__ =  '820472580@qq.com'
__date__ = '2019-12-11 17:37:29'


from . import utils
from .setting import SettingWindow
from .. import commands, pins

from maya import cmds
from maya import OpenMayaUI

import os
import json
import locale
import webbrowser

DIR = os.path.dirname(__file__)
INSTRUNCTION_PATH = "file:///%s" % os.path.join(os.path.dirname(DIR),"instruction","README.html")

class ManagerMenu(utils.QMenu):
    """
    Manager Menu 
    
    Used to create / edit and delete different pin sets and be able to switch 
    between them, it also features the functionality to refresh the command 
    list.
    
    :param QWidget parent:
    """
    def __init__(self, parent=None):
        utils.QMenu.__init__(self, parent)
        self.RB_dict = {}
        
        self.pins_div_text        = ""
        self.sets_div_text        = ""
        self.sets_add_text        = ""
        self.sets_clear_text      = ""
        self.sets_delete_text     = ""
        self.command_div_text     = ""
        self.command_refresh_text = ""
        self.command_setting_text = ""
        self.command_help_text    = ""
        
        # variable
        self.parent = parent
        self.active = None
        
        self.setting = SettingWindow(self)
        
    def initialize(self):
        # menu
        self.setObjectName("PinMenu")
        self.setMinimumWidth(140)
        
        # connect
        self.aboutToShow.connect(self.aboutToShow_)
        self.setStyleSheet('font-family: Microsoft YaHei UI;')
        self.populate()
        self.pins =  pins.read()
        
    # ------------------------------------------------------------------------
                
    def aboutToShow_(self):
        """
        Before the menu is shown, the pin set are read, the menu is populated 
        with the read pin set data and the menu is positioned.
        """
        # get pins
        self.pins =  pins.read()
        
        # populate
        self.populate()
        self.position()

        self.search.setFocus()
        
    # ------------------------------------------------------------------------
    
    def add(self, widget):
        """
        Add widget to a QWidgetAction and add it to the menu.
        
        :param QWidget widget: widget to be added to the menu
        """
        action = utils.QWidgetAction(self)
        action.setDefaultWidget(widget)
        self.addAction(action)
        
    # ------------------------------------------------------------------------

    def populate(self):
        """
        Populate the menu, clears the menu first, then adds the pins, set 
        manager and finally the command refresh option.
        """
        # clear menu
        self.clear()
        
        # pins
        self.populatePins()
        self.populateSets()
        self.populateCommands()
  
    # ------------------------------------------------------------------------
    
    def populatePins(self):
        """
        Read pin set data and create radio buttons so the user can switch
        between the different sets available.
        """ 
        # get pin names
        names = pins.get().keys()
        if not names:
            return
            
        # add pins group
        self.group = utils.QButtonGroup(self)
        self.group.setExclusive(False)
        self.group.buttonReleased.connect(self.setActive)
        
        self.pins_div = utils.Divider(self, self.pins_div_text)
        self.add(self.pins_div)
        
        # add pins
        for name in names:
            # create pin
            radio = utils.QRadioButton(name)
            
            # set active
            if name == self.active:
                radio.setChecked(True)
            
            # add pin
            self.add(radio)
            self.group.addButton(radio)
            
            self.RB_dict[name] = radio
                
    def populateSets(self):
        """
        Create set manager buttons.
        """ 
        self.sets_div = utils.Divider(self, self.sets_div_text)  
        self.add(self.sets_div)        
        
        self.search = utils.QLineEdit()
        self.add(self.search)    

        self.sets_add = utils.QAction(self.sets_add_text,self)
        self.sets_add.triggered.connect(self.pinAdd)
        
        self.sets_clear = utils.QAction(self.sets_clear_text,self)
        self.sets_clear.triggered.connect(self.pinClear)
        
        self.sets_delete = utils.QAction(self.sets_delete_text,self)
        self.sets_delete.triggered.connect(self.pinDelete)
        
        self.addAction(self.sets_add)
        self.addAction(self.sets_clear)
        self.addAction(self.sets_delete)
        
    def populateCommands(self):
        """
        Create command refresh button.
        """ 
        self.command_div = utils.Divider(self, self.command_div_text)  
        self.add(self.command_div)
        
        self.command_refresh = utils.QAction(self.command_refresh_text,self)
        self.command_refresh.triggered.connect(self.refresh)
        
        self.command_setting = utils.QAction(self.command_setting_text,self)
        self.command_setting.triggered.connect(self.setting.mayaShow)
        
        self.command_help = utils.QAction(self.command_help_text,self)
        self.command_help.triggered.connect(lambda:webbrowser.open_new_tab(INSTRUNCTION_PATH))
        
        self.addAction(self.command_refresh)
        self.addAction(self.command_setting)
        self.addAction(self.command_help)
        
    # ------------------------------------------------------------------------
                
    def position(self):
        """
        Position the menu underneath its parent.
        """
        pos = self.parent.parentWidget().mapToGlobal(self.parent.pos())
        posX = pos.x()
        posY = pos.y()
        height = self.parent.height()
        
        posY += height
        self.move(posX + 8, posY) 
        
    # ------------------------------------------------------------------------
        
    def setActive(self,num=0):
        """
        Switch active pin set to checked radio button.
        """
        names = pins.get().keys()
        if not names:
            return
        
        if num:
            buttons = self.group.buttons()
            if len(buttons) >= num:
                btn = buttons[num-1]
            else:
                return
        else:
            btn = self.group.checkedButton()
            
        if not btn or self.active == btn.text():
            self.active = None
            for _, v in commands.get().iteritems():
                v["pin"] = False
            return
        else:
            # set active
            for button in self.group.buttons():
                if button != btn:
                    button.setChecked(False)

            self.active = btn.text()
            
            # get pins
            return self.getActive()

    def getActive(self):
        pins_list = []
        pinned = pins.get().get(self.active) or []
        for _, v in commands.get().iteritems():
            if v.get("hierarchy") in pinned:           
                v["pin"] = True
                pins_list.append(v)
            else:                                             
                v["pin"] = False
        return pins_list
                    
    # --------------------------------------------------------------------
    
    @property    
    def pinName(self):
        """
        Get text from QLineEdit
        """
        return self.search.text().lower()
        
    def pinAdd(self):
        """
        Add pin set, store all if the currently pinned commands and store
        then under the provided pin set name.
        
        :raises ValueError: if name is invalid or no pins are found
        """
        # get pin name
        if not self.pinName:
            raise ValueError("Search Commands: invalid name")
            return
        
        # get pinned name
        pinned = []
        for k, v in commands.get().iteritems():
            if not v.get("pin"):
                continue
                
            pinned.append(v.get("hierarchy"))
        
        if not pinned:
            raise ValueError("Search Commands: no pinned commands")
            return
        
        # set active
        self.active = self.pinName
        pins.get()[self.pinName] = pinned
        
        # write to file
        pins.write()
       
        self.populate()

    def pinClear(self):
        """
        Clear all pins and clear set selection.
        """
        # clear all pins
        for k, v in commands.get().iteritems():
            v["pin"] = False
        
        self.active = None


    def pinDelete(self):
        """
        Delete pin set, check if the provided name exists in the pin sets.
        If it does remove it from the data set and save.
        
        :raises ValueError: if name is invalid
        """

        if not self.pinName in pins.get().keys():
            raise ValueError("Search Commands: invalid name")
            return
        
        # pop from list
        pins.get().pop(self.pinName, None)
        self.pinClear()
        
        # write to file
        pins.write()
        
        self.RB_dict[self.pinName].setParent(None)

    # --------------------------------------------------------------------

    def refresh( self ):
        """
        Refresh command list and clear the pin set selection.
        """
        commands.store()
        self.pinClear()