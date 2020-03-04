# coding:utf-8

__author__ =  'timmyliang'
__email__ =  '820472580@qq.com'
__date__ = '2019-12-11 17:37:29'


from . import utils
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
        
        # menu
        self.setObjectName("PinMenu")
        self.setMinimumWidth(140)
        
        # connect
        self.aboutToShow.connect(self.aboutToShow_)
        
        self.setting = SettingWindow(self)
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
        self.Lang_Combo = utils.QComboBox(Form)
        self.Lang_Combo.setObjectName("Lang_Combo")
        self.gridLayout.addWidget(self.Lang_Combo, 0, 1, 1, 3)

        utils.QMetaObject.connectSlotsByName(Form)

class SettingWindow(utils.QWidget,SettingWindow_UI):
    
    def __init__(self,menu):
        super(SettingWindow,self).__init__()
        self.setupUi(self)
        
        self.setting_data = {}
        self.ptr = None
        
        path = os.environ.get("LOCALAPPDATA")
        directory = os.path.join(path, "Maya_CommandLauncher")
        if not os.path.exists(directory):
            os.mkdir(directory)

        self.SETTING_PATH = os.path.join(directory,"setting.json")
        
        self.menu = menu
        self.search = menu.parent.search
        self.setupMenu()
        
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
        
        if os.path.exists(self.SETTING_PATH):
            self.importJsonSetting(self.SETTING_PATH)

        self.setStyleSheet('font-family: Microsoft YaHei UI;')

        # NOTE 设置语言菜单
        self.__lang_list = {}
        self.trans = utils.QTranslator(self)

        self.localeList = {
            "zh_CN":u"中文",
            "en_US":u"English",
        }

        self.Lang_Combo.currentIndexChanged.connect(self.translateText)

        # NOTE 设置名称
        self.retranslateUi()
    
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
        self.close_action.triggered.connect(lambda :self.ptr.close() if self.ptr else None)
        
        self.help_menu = utils.QMenu(u'帮助',self)
        self.menuBar.addMenu(self.help_menu)
        self.help_action = utils.QAction(u'使用说明', self)    
        self.help_menu.addAction(self.help_action)
        
        self.help_action.triggered.connect(lambda:webbrowser.open_new_tab(INSTRUNCTION_PATH))
    
    def retranslateUi(self):
        self.edit_menu_text  = utils.QApplication.translate('menu','Edit')
        self.import_text     = utils.QApplication.translate('menu','Import')
        self.export_text     = utils.QApplication.translate('menu','Export')
        self.reset_text      = utils.QApplication.translate('menu','Reset')
        self.close_text      = utils.QApplication.translate('menu','Close')
        self.help_menu_text  = utils.QApplication.translate('menu','Help')
        self.help_text       = utils.QApplication.translate('menu','Documentation')
        
        self.Scroll_Lock     = utils.QApplication.translate('setting',"scroll lock line")
        self.Languge         = utils.QApplication.translate('setting',"Language Mode")
        self.Display         = utils.QApplication.translate('setting',"item display num")
        self.Scroll_Start    = utils.QApplication.translate('setting',"scroll start line")
        self.Shortcut        = utils.QApplication.translate('setting',"shortcut number")
        self.Title           = utils.QApplication.translate('setting',"CommandLauncher - SettingWindow")
        
        self.pins_div        = utils.QApplication.translate('sets',"Pins")
        self.sets_div        = utils.QApplication.translate('sets',"Sets")
        self.sets_add        = utils.QApplication.translate('sets',"Add")
        self.sets_clear      = utils.QApplication.translate('sets',"Clear")
        self.sets_delete     = utils.QApplication.translate('sets',"Delete")
        self.command_div     = utils.QApplication.translate('command',"Commands")
        self.command_refresh = utils.QApplication.translate('command',"Refresh")
        self.command_setting = utils.QApplication.translate('command',"Setting")
        self.command_help    = utils.QApplication.translate('command',"Help")
        
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

    @property
    def localeList(self):
        return self.__lang_list
    
    @localeList.setter
    def localeList(self,value):
        if type(value) != dict:
            return
        self.__lang_list = value
        
        system_lang = utils.QLocale.system().name()
        i18n_folder = os.path.join(DIR,"i18n")
        for i,(name,label) in enumerate(self.__lang_list.items()):
            qm_file = os.path.join(i18n_folder,"%s.qm" % name)
            qm_file = qm_file if os.path.exists(qm_file) else None
            self.Lang_Combo.addItem(label)
            self.Lang_Combo.setItemData(i, qm_file)
            # NOTE 判断系统语言进行注册
            if system_lang == name:
                self.i18nInstall(qm_file)
                self.Lang_Combo.setCurrentIndex(i)

    def i18nInstall(self,qm_path):
        if qm_path and os.path.exists(qm_path):
            self.trans.load(qm_path)
            utils.QApplication.instance().installTranslator(self.trans)
        else:
            utils.QApplication.instance().removeTranslator(self.trans)

    def changeEvent(self, event):
        if event.type() == utils.QEvent.LanguageChange:
            self.retranslateUi()
        super(SettingWindow, self).changeEvent(event)

    def translateText(self,index):
        qm_file = self.Lang_Combo.itemData(index)
        self.i18nInstall(qm_file)
        self.exportJsonSetting(self.SETTING_PATH)
        
    def mayaShow(self):
        # NOTE 如果变量存在 就检查窗口多开
        if cmds.window("CMDLauncher_SettingWindow",q=1,ex=1):
            cmds.deleteUI('CMDLauncher_SettingWindow')
        window = cmds.window("CMDLauncher_SettingWindow",title=self.Title)
        cmds.showWindow(window)
        # NOTE 将Maya窗口转换成 Qt 组件
        self.ptr = self.mayaToQT(window)
        self.ptr.setLayout(utils.QVBoxLayout())
        self.ptr.layout().setContentsMargins(0,0,0,0)
        self.ptr.layout().addWidget(self)
        self.ptr.destroyed.connect(self._close)
        self.ptr.resize(0,0)
        
    def _close(self):
        # NOTE 彻底删除窗口
        self.setParent(None)

    def mayaToQT( self,name ):
        # Maya -> QWidget
        ptr = OpenMayaUI.MQtUtil.findControl( name )
        if ptr is None:     ptr = OpenMayaUI.MQtUtil.findLayout( name )
        if ptr is None:     ptr = OpenMayaUI.MQtUtil.findMenuItem( name )
        if ptr is not None: return utils.shiboken.wrapInstance( long( ptr ), utils.QWidget )
    
    def importJsonSetting(self,path=None):
        """
        importJsonSetting 导入Json
        
        Keyword Arguments:
            path {str} -- 导入路径 为空则弹出选择窗口获取 (default: {None})
        """
        if not path:
            path,_ = utils.QFileDialog.getOpenFileName(self, filter= u"json (*.json)")
            if not path:return

        # NOTE 如果文件不存在则返回空
        if not os.path.exists(path):return

        with open(path,'r') as f:
            self.setting_data = json.load(f,encoding="utf-8")

         # NOTE 获取当前设置
        self.Lang_Combo.setCurrentIndex  ( self.setting_data["comboBox"]        )
        self.Scroll_Start_SP.setValue  ( self.setting_data["Scroll_Start_SP"] )
        self.Scroll_Lock_SP.setValue   ( self.setting_data["Scroll_Lock_SP"]  )
        self.Shortcut_SP.setValue      ( self.setting_data["Shortcut_SP"]     )
        self.Display_SP.setValue       ( self.setting_data["Display_SP"]      )
        
    def exportJsonSetting(self,path=None):
        """
        exportJsonSetting 导出Json
        
        Keyword Arguments:
            path {str} -- 导出路径 为空则弹出选择窗口获取 (default: {None})
        """
        if not path:
            path,_ = utils.QFileDialog.getSaveFileName(self,filter= u"json (*.json)")
            if not path:return
        
        self.setting_data["comboBox"]        = self.Lang_Combo.currentIndex()
        self.setting_data["Scroll_Start_SP"] = self.Scroll_Start_SP.value()
        self.setting_data["Scroll_Lock_SP"]  = self.Scroll_Lock_SP.value()
        self.setting_data["Shortcut_SP"]     = self.Shortcut_SP.value()
        self.setting_data["Display_SP"]      = self.Display_SP.value()
        
        with open(path,'w') as f:
            json.dump(self.setting_data,f,indent=4)
 
    def resetJsonSetting(self):
        self.translateText(-1)
        self.Scroll_Start_SP.setValue(3)
        self.Scroll_Lock_SP.setValue(4)
        self.Shortcut_SP.setValue(8)
        self.Display_SP.setValue(100)
 
    def scrollLock(self,value):
        self.search.scroll_locked = value
        self.exportJsonSetting(self.SETTING_PATH)

    def scrollStart(self,value):
        self.search.scroll_start = value
        self.exportJsonSetting(self.SETTING_PATH)
    
    def display(self,value):
        self.search.display_num = value
        self.exportJsonSetting(self.SETTING_PATH)
    
    def shortcut(self,value):
        self.search.shortcut_num = value
        self.exportJsonSetting(self.SETTING_PATH)

# ----------------------------------------------------------------------------

class CommandLauncherIcon(utils.QPushButton):
    def __init__(self,parent=None):
        super(CommandLauncherIcon,self).__init__(parent)
        self.setFlat(True)
        self.setFixedWidth(25)
        self.setFixedHeight(25)

        # NOTE 默认开启
        self.setIconColor()

        self.lancher_state = True

        self.menu = utils.QMenu()
        self.setMenu(self.menu)

        self.divider = utils.Divider(self,"")
        self.add(self.divider)

        self.State_BTN = utils.QPushButton()
        self.State_BTN.clicked.connect(self.toggleState)
        self.add(self.State_BTN)
        
        self.retranslateUi()

    def changeEvent(self, event):
        if event.type() == utils.QEvent.LanguageChange:
            self.retranslateUi()
        super(CommandLauncherIcon, self).changeEvent(event)

    def toggleState(self):
        from . import setup,clean
        self.lancher_state = not self.lancher_state

        if self.lancher_state:
            setup()
            self.setIconColor()
        else:
            clean()
            self.setDarkColor()

        self.retranslateUi()

    def retranslateUi(self):
        self.divider.setText(utils.QApplication.translate('icon','CommandLauncher'))
        text = utils.QApplication.translate('icon','OFF') if self.lancher_state else utils.QApplication.translate('icon','ON')
        self.State_BTN.setText(text)

    def add(self, widget):
        """
        Add widget to a QWidgetAction and add it to the menu.
        
        :param QWidget widget: widget to be added to the menu
        """
        action = utils.QWidgetAction(self)
        action.setDefaultWidget(widget)
        self.menu.addAction(action)

    def setIconColor(self):
        self.setIcon(utils.findSearchIcon())
        self.setIconSize(utils.QSize(25,25))  

    def setDarkColor(self,size=25):
        """setButtonColor set Icon Color
        # NOTE https://stackoverflow.com/questions/53107173/change-color-png-image-qpushbutton
        Parameters
        size : int, optional
            icon size, by default 25
        """
        
        icon = self.icon()
        pixmap = icon.pixmap(size)
        image = pixmap.toImage()
        pcolor = image.pixelColor(size,size)
        for x in range(image.width()):
            for y in range(image.height()):
                pcolor = image.pixelColor(x, y)
                image.setPixelColor(x, y, pcolor.darker())
        self.setIcon(utils.QIcon(utils.QPixmap.fromImage(image)))
