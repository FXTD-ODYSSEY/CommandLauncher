# coding:utf-8

__author__ =  'timmyliang'
__email__ =  '820472580@qq.com'
__date__ = '2019-12-11 17:37:29'


from . import utils
from .. import commands, pins
from maya import cmds
from maya import OpenMayaUI

import os
import locale
import webbrowser

DIR = os.path.dirname(os.path.dirname(__file__))
INSTRUNCTION_PATH = "file:///%s" % os.path.join(DIR,"instruction","README.html")

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
        
        # menu
        self.setObjectName("PinMenu")
        self.setMinimumWidth(140)
        
        # connect
        self.aboutToShow.connect(self.aboutToShow_)
        
        self.setting = SettingWindow(self)
        self.setStyleSheet('font-family: Microsoft YaHei UI;')
        self.populate()
        
        
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
        if num:
            buttons = self.group.buttons()
            if len(buttons) >= num:
                btn = buttons[num-1]
            else:
                return
        else:
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
        

class SettingWindow_UI(object):

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(379, 120)
        self.gridLayout = utils.QGridLayout(Form)
        self.gridLayout.setContentsMargins(9,20,9,9)
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
        self.Display_SP.setMaximum(9999)
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
        self.comboBox.setItemText(0, "English")
        self.comboBox.setItemText(1, u"中文")

class SettingWindow(utils.QWidget,SettingWindow_UI):
    
    def __init__(self,menu):
        super(SettingWindow,self).__init__()
        self.setupUi(self)
        
        self.menu = menu
        self.search = menu.parent.search
        self.setupMenu()
        
        # NOTE 获取当前系统的语言
        self.translateText(-1)
        self.comboBox.currentIndexChanged.connect(self.translateText)
        
        # NOTE 获取当前设置
        scroll_start = self.search.scroll_start
        self.Scroll_Start_SP.setValue(scroll_start)
        scroll_locked = self.search.scroll_locked
        self.Scroll_Lock_SP.setValue(scroll_locked)
    
        shortcut_num = self.search.shortcut_num
        self.Shortcut_SP.setValue(shortcut_num)
        display_num = self.search.display_num
        self.Display_SP.setValue(display_num)
        
        self.Scroll_Lock_SP.valueChanged.connect(self.scrollLock)
        self.Scroll_Start_SP.valueChanged.connect(self.scrollStart)
        self.Display_SP.valueChanged.connect(self.display)
        self.Shortcut_SP.valueChanged.connect(self.shortcut)
        

        self.setStyleSheet('font-family: Microsoft YaHei UI;')
      
    def setupMenu(self):
        self.menuBar = utils.QMenuBar(self)
        self.edit_menu = utils.QMenu(u'编辑',self)
        self.menuBar.addMenu(self.edit_menu)
        self.import_json_action = utils.QAction(u'导入设置', self)    
        self.export_json_action = utils.QAction(u'导出设置', self)  
        self.reset_json_action  = utils.QAction(u'重置设置', self)    
        self.close_action       = utils.QAction(u'关闭', self)    

        self.edit_menu.addAction(self.import_json_action)
        self.edit_menu.addAction(self.export_json_action)
        self.edit_menu.addAction(self.reset_json_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.close_action)

        # NOTE 添加下拉菜单的功能触发
        self.import_json_action.triggered.connect(self.importJsonSetting)
        self.export_json_action.triggered.connect(self.exportJsonSetting)
        self.reset_json_action.triggered.connect(self.resetJsonSetting)
        self.close_action.triggered.connect(self.window().deleteLater)
        
        self.help_menu = utils.QMenu(u'帮助',self)
        self.menuBar.addMenu(self.help_menu)
        self.help_action = utils.QAction(u'使用说明', self)    
        self.help_menu.addAction(self.help_action)
        
        
        self.help_action.triggered.connect(lambda:webbrowser.open_new_tab(INSTRUNCTION_PATH))


    def translateText(self,index):
        lang = ""
        if index == -1:
            lang,_ = locale.getdefaultlocale()
        elif index == 0:
            lang = "en_US"
        elif index == 1:
            lang = "zh_CN"

        if lang == "zh_CN":
            self.comboBox.setCurrentIndex(1)
            self.edit_menu_text  = u'编辑'
            self.import_text     = u'导入设置'
            self.export_text     = u'导出设置'
            self.reset_text      = u'重置设置'
            self.close_text      = u'关闭'
            self.help_menu_text  = u'帮助'
            self.help_text       = u'使用说明'

            self.Scroll_Lock     = u"滚动锁定行"
            self.Languge         = u"语言模式"
            self.Display         = u"命令显示数量"
            self.Scroll_Start    = u"开始滚动行"
            self.Shortcut        = u"快捷键显示数量"
            self.Title           = u"命令启动器 - 设定窗口"
            
            self.pins_div        = u"固定"
            self.sets_div        = u"置顶集"
            self.sets_add        = u"添加"
            self.sets_clear      = u"清空"
            self.sets_delete     = u"删除"
            self.command_div     = u"命令"
            self.command_refresh = u"刷新"
            self.command_setting = u"设置"
            self.command_help    = u"帮助"
        else:
            self.comboBox.setCurrentIndex(0)
            self.edit_menu_text  = u'Edit'
            self.import_text     = u'Import'
            self.export_text     = u'Export'
            self.reset_text      = u'Reset'
            self.close_text      = u'Close'
            self.help_menu_text  = u'Help'
            self.help_text       = u'Documentation'
            
            self.Scroll_Lock     = u"scroll lock line"
            self.Languge         = u"Language Mode"
            self.Display         = u"item display num"
            self.Scroll_Start    = u"scroll start line"
            self.Shortcut        = u"shortcut number"
            self.Title           = u"CommandLauncher - SettingWindow"
            
            self.pins_div        = u"Pins"
            self.sets_div        = u"Sets"
            self.sets_add        = u"Add"
            self.sets_clear      = u"Clear"
            self.sets_delete     = u"Delete"
            self.command_div     = u"Commands"
            self.command_refresh = u"Refresh"
            self.command_setting = u"Setting"
            self.command_help    = u"Help"
        
        self.edit_menu.setTitle             ( self.edit_menu_text   )
        self.import_json_action.setText     ( self.import_text      )
        self.export_json_action.setText     ( self.export_text      )
        self.reset_json_action.setText      ( self.reset_text       )
        self.close_action.setText           ( self.close_text       )
        self.help_menu.setTitle             ( self.help_menu_text   )
        self.help_action.setText            ( self.help_text        )

        self.Scroll_Lock_Label.setText      ( self.Scroll_Lock      )
        self.Languge_Label.setText          ( self.Languge          )
        self.Display_Label.setText          ( self.Display          )
        self.Scroll_Start_Label.setText     ( self.Scroll_Start     )
        self.Shortcut_Label.setText         ( self.Shortcut         )
        self.window().setWindowTitle        ( self.Title            )

        self.menu.pins_div_text        = self.pins_div         
            
        self.menu.sets_div_text        = self.sets_div         
        self.menu.sets_add_text        = self.sets_add         
        self.menu.sets_clear_text      = self.sets_clear       
        self.menu.sets_delete_text     = self.sets_delete      

        self.menu.command_div_text     = self.command_div      
        self.menu.command_refresh_text = self.command_refresh  
        self.menu.command_setting_text = self.command_setting  
        self.menu.command_help_text    = self.command_help  
        
    def mayaShow(self):
        # NOTE 如果变量存在 就检查窗口多开
        if cmds.window("CMDLauncher_SettingWindow",q=1,ex=1):
            cmds.deleteUI('CMDLauncher_SettingWindow')
        window = cmds.window("CMDLauncher_SettingWindow",title=self.Title)
        cmds.showWindow(window)
        # NOTE 将Maya窗口转换成 Qt 组件
        ptr = self.mayaToQT(window)
        ptr.setLayout(utils.QVBoxLayout())
        ptr.layout().setContentsMargins(0,0,0,0)
        ptr.layout().addWidget(self)
        ptr.destroyed.connect(self._close)
        ptr.resize(0,0)
        
    def _close(self):
        # NOTE 脱离要删除的窗口 | 由于自身依附在 ManagerMenu 上 因此不会被垃圾回收
        self.setParent(utils.mayaWindow())

    def mayaToQT( self,name ):
        # Maya -> QWidget
        ptr = OpenMayaUI.MQtUtil.findControl( name )
        if ptr is None:     ptr = OpenMayaUI.MQtUtil.findLayout( name )
        if ptr is None:     ptr = OpenMayaUI.MQtUtil.findMenuItem( name )
        if ptr is not None: return utils.shiboken.wrapInstance( long( ptr ), utils.QWidget )
    
    def importJsonSetting(self):
        pass
    
    def exportJsonSetting(self):
        pass
 
    def resetJsonSetting(self):
        self.translateText(-1)
        self.Scroll_Start_SP.setValue(3)
        self.Scroll_Lock_SP.setValue(4)
        self.Shortcut_SP.setValue(8)
        self.Display_SP.setValue(100)
 
    def scrollLock(self,value):
        self.search.scroll_locked = value
    
    def scrollStart(self,value):
        self.search.scroll_start = value
    
    def display(self,value):
        self.search.display_num = value
    
    def shortcut(self,value):
        self.search.shortcut_num = value