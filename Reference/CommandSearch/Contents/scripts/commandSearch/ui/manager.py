# coding:utf-8

__author__ =  'timmyliang'
__email__ =  '820472580@qq.com'
__date__ = '2019-12-11 17:37:29'


from . import utils
from .. import commands, pins
from maya import cmds
from maya import OpenMayaUI
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
        
        # variable
        self.parent = parent
        self.active = None
        
        # menu
        self.setObjectName("PinMenu")
        self.setMinimumWidth(140)
        
        # connect
        self.aboutToShow.connect(self.aboutToShow_)
        
        self.setting = SettingWindow()
        self.populate()
    # ------------------------------------------------------------------------
                
    def aboutToShow_(self):
        """
        Before the menu is shown, the pin set are read, the menu is populated 
        with the read pin set data and the menu is positioned.
        """
        # get pins
        pins.read()
        
        # populate
        self.position()

        self.edit.setFocus()
        
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
        
        g = utils.Divider(self, "Pins")
        self.add(g)
        
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
                
    def populateSets(self):
        """
        Create set manager buttons.
        """ 
        g = utils.Divider(self, "Sets")  
        self.add(g)        
        
        self.edit = utils.QLineEdit()
        self.add(self.edit)    

        self.addAction("Add", self.pinAdd)
        self.addAction("Clear", self.pinClear)
        self.addAction("Delete", self.pinDelete)
        
    def populateCommands(self):
        """
        Create command refresh button.
        """ 
        g = utils.Divider(self, "Commands")  
        self.add(g)
        self.addAction("Refresh", self.refresh)
        self.addAction("Setting", self.setting.show)
        
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
        
    def setActive(self):
        """
        Switch active pin set to checked radio button.
        """
        btn = self.group.checkedButton()
        if not btn:
            self.active = None
            for _, v in commands.get().iteritems():
                v["pin"] = False
        else :
            # set active
            for button in self.group.buttons():
                if button != btn:
                    button.setChecked(False)

            self.active = btn.text()
            
            # get pins
            pinned = pins.get().get(self.active) or []
            for _, v in commands.get().iteritems():
                if v.get("hierarchy") in pinned:           
                    v["pin"] = True
                else:                                             
                    v["pin"] = False
                
    # --------------------------------------------------------------------
    
    @property    
    def pinName(self):
        """
        Get text from QLineEdit
        """
        return self.edit.text().lower()
        
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
       
    def pinClear(self):
        """
        Clear all pins and clear set selection.
        """
        if not self.pinName in pins.get().keys():
            raise ValueError("Search Commands: invalid name")
            return

        # clear all pins
        for _, v in commands.get().iteritems():
            v["pin"] = False
        
        pins.get()[self.pinName] = []
        pins.write()

        # self.active = None

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

    # --------------------------------------------------------------------

    def refresh( self ):
        """
        Refresh command list and clear the pin set selection.
        """
        commands.store()
        self.pinClear()
        

class SettingWindow_UI(object):

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(379, 120)
        self.gridLayout = utils.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.Scroll_Lock_SP = utils.QSpinBox(Form)
        self.Scroll_Lock_SP.setObjectName("Scroll_Lock_SP")
        self.gridLayout.addWidget(self.Scroll_Lock_SP, 2, 3, 1, 1)
        self.Scroll_Lock_Label = utils.QLabel(Form)
        self.Scroll_Lock_Label.setObjectName("label_2")
        self.gridLayout.addWidget(self.Scroll_Lock_Label, 2, 2, 1, 1)
        self.Languge_Label = utils.QLabel(Form)
        self.Languge_Label.setObjectName("label_5")
        self.gridLayout.addWidget(self.Languge_Label, 0, 0, 1, 1)
        spacerItem = utils.QSpacerItem(20, 40, utils.QSizePolicy.Minimum, utils.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 0, 1, 1)
        self.Display_Label = utils.QLabel(Form)
        self.Display_Label.setObjectName("label_4")
        self.gridLayout.addWidget(self.Display_Label, 3, 2, 1, 1)
        self.Display_SP = utils.QSpinBox(Form)
        self.Display_SP.setMaximum(9)
        self.Display_SP.setObjectName("Display_SP")
        self.gridLayout.addWidget(self.Display_SP, 3, 3, 1, 1)
        self.Scroll_Start_SP = utils.QSpinBox(Form)
        self.Scroll_Start_SP.setObjectName("Scroll_Start_SP")
        self.gridLayout.addWidget(self.Scroll_Start_SP, 2, 1, 1, 1)
        self.Scroll_Start_Label = utils.QLabel(Form)
        sizePolicy = utils.QSizePolicy(utils.QSizePolicy.Preferred, utils.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Scroll_Start_Label.sizePolicy().hasHeightForWidth())
        self.Scroll_Start_Label.setSizePolicy(sizePolicy)
        self.Scroll_Start_Label.setObjectName("label")
        self.gridLayout.addWidget(self.Scroll_Start_Label, 2, 0, 1, 1)
        self.Shortcut_Label = utils.QLabel(Form)
        self.Shortcut_Label.setObjectName("label_3")
        self.gridLayout.addWidget(self.Shortcut_Label, 3, 0, 1, 1)
        self.Shortcut_SP = utils.QSpinBox(Form)
        self.Shortcut_SP.setMaximum(9)
        self.Shortcut_SP.setObjectName("Shortcut_SP")
        self.gridLayout.addWidget(self.Shortcut_SP, 3, 1, 1, 1)
        self.comboBox = utils.QComboBox(Form)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.gridLayout.addWidget(self.comboBox, 0, 1, 1, 3)

        self.retranslateUi(Form)
        utils.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle("Form")
        self.Scroll_Lock_Label.setText("scroll lock line")
        self.Languge_Label.setText("Language Mode")
        self.Display_Label.setText("item display num")
        self.Scroll_Start_Label.setText("scroll start line")
        self.Shortcut_Label.setText("shortcut number")
        self.comboBox.setItemText(0, "English")
        self.comboBox.setItemText(1, u"中文")

class SettingWindow(utils.QWidget,SettingWindow_UI):
    
    def __init__(self):
        super(SettingWindow,self).__init__()
        self.setupUi(self)
        # NOTE 如果变量存在 就检查窗口多开
        if cmds.window("CMDLauncher_SettingWindow",q=1,ex=1):
            cmds.deleteUI('CMDLauncher_SettingWindow')

        window = cmds.window("CMDLauncher_SettingWindow",title=u"CommandLauncher - SettingWindow")
        # NOTE 将Maya窗口转换成 Qt 组件
        self.ptr = self.mayaToQT(window)
        self.ptr.setLayout(utils.QVBoxLayout())
        self.ptr.layout().setContentsMargins(0,0,0,0)
        self.ptr.layout().addWidget(self)
        
    def show(self):
        self.ptr.show()

    def mayaToQT( self,name ):
            # Maya -> QWidget
            ptr = OpenMayaUI.MQtUtil.findControl( name )
            if ptr is None:         ptr = OpenMayaUI.MQtUtil.findLayout( name )
            if ptr is None:         ptr = OpenMayaUI.MQtUtil.findMenuItem( name )
            if ptr is not None:     return utils.shiboken.wrapInstance( long( ptr ), utils.QWidget )
