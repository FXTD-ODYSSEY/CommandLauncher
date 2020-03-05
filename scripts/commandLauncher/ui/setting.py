# coding:utf-8

__author__ =  'timmyliang'
__email__ =  '820472580@qq.com'
__date__ = '2020-03-04 21:30:31'


import os
import json
import webbrowser

from maya import cmds
from maya import OpenMayaUI

DIR = os.path.dirname(__file__)
INSTRUNCTION_PATH = "file:///%s" % os.path.join(os.path.dirname(DIR),"instruction","README.html")
       

path = os.environ.get("LOCALAPPDATA")
directory = os.path.join(path, "Maya_CommandLauncher")
if not os.path.exists(directory):
    os.mkdir(directory)

SETTING_PATH = os.path.join(directory,"setting.json")

from . import utils
from .. import commands

class RedFrame(utils.QWidget):
    BorderColor     = utils.QColor("coral")     
    BackgroundColor = utils.QColor(100, 100, 100, 125) 
    
    def __init__(self, parent):
        super(RedFrame,self).__init__()
        self.setAttribute(utils.Qt.WA_NoSystemBackground)
        self.setAttribute(utils.Qt.WA_TransparentForMouseEvents)
        self.setWindowFlags(utils.Qt.WindowTransparentForInput | utils.Qt.FramelessWindowHint)
        self.setFocusPolicy( utils.Qt.NoFocus )

        self.setParent(parent)
        parent.installEventFilter(self)

    def paintEvent(self, event):
        
        # NOTE https://stackoverflow.com/questions/51687692/how-to-paint-roundedrect-border-outline-the-same-width-all-around-in-pyqt-pysi
        painter = utils.QPainter(self)
        painter.setRenderHint(utils.QPainter.Antialiasing)   

        rectPath = utils.QPainterPath()                      
        height = self.height() - 4                     
        rect = utils.QRectF(2, 2, self.width()-4, height)
        
        # NOTE 绘制边界颜色
        rectPath.addRoundedRect(rect, 3, 3)
        painter.setPen(utils.QPen(self.BorderColor, 2, utils.Qt.SolidLine,utils.Qt.RoundCap, utils.Qt.RoundJoin))
        painter.drawPath(rectPath)
    
    def eventFilter(self, obj, event):
        if not obj.isWidgetType():
            return False
        
        if self.isVisible():
            self.setGeometry(obj.rect())
        elif event.type() == utils.QEvent.Resize:
            self.setGeometry(obj.rect())

        return False

class PathItem(utils.QWidget):
    def __init__(self,setting_win,path):
        super(PathItem,self).__init__()
        self.setupUi()
        self.setting_win = setting_win

        self.setText(path)

        # NOTE 添加数据
        setting_win.setting_data["path"][path] = True
        self.setChecked(True)

        frame = RedFrame(self)
        frame.show()

        
    def setupUi(self):
        self.setObjectName("Path_Widget")
        self.horizontalLayout_2 = utils.QHBoxLayout()
        self.setLayout(self.horizontalLayout_2)
        self.horizontalLayout_2.setContentsMargins(5, 5, 5, 5)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.Path_CB = utils.QCheckBox(self)
        sizePolicy = utils.QSizePolicy(utils.QSizePolicy.Expanding, utils.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Path_CB.sizePolicy().hasHeightForWidth())
        self.Path_CB.setSizePolicy(sizePolicy)
        self.Path_CB.setContextMenuPolicy(utils.Qt.CustomContextMenu)
        self.Path_CB.setStyleSheet("")
        self.Path_CB.setObjectName("Path_CB")
        self.horizontalLayout_2.addWidget(self.Path_CB)
        self.Path_Del = utils.QPushButton(self)
        self.Path_Del.setMinimumSize(utils.QSize(0, 0))
        self.Path_Del.setMaximumSize(utils.QSize(25, 16777215))
        self.Path_Del.setStyleSheet('''
            QPushButton {
                background:coral;
                color:white
            }

            QPushButton::pressed {
                background:red
            }
        ''')
        self.Path_Del.setObjectName("Path_Del")
        self.horizontalLayout_2.addWidget(self.Path_Del)

        self.Path_Del.setText("X")
        self.Path_Del.clicked.connect(self.deleleItem)

        self.Path_CB.stateChanged.connect(self.checkChangeEvent)

    def checkChangeEvent(self,checked):
        self.setting_win.setting_data["path"][self.text()] = checked
        self.setting_win.exportJsonSetting(SETTING_PATH)
    
    def deleleItem(self):
        self.setParent(None)

        # NOTE 清理数据
        del self.setting_win.setting_data["path"][self.text()]
        self.setting_win.exportJsonSetting(SETTING_PATH)
        
    def text(self):
        return self.Path_CB.text()

    def setText(self,text):
        self.Path_CB.setText(text)

    def setChecked(self,checked):
        self.Path_CB.setChecked(checked)

class SearchPathWidget(utils.QWidget):
    def __init__(self,setting_win):
        super(SearchPathWidget,self).__init__()
        self.setupUi()

        self.setting_win = setting_win

    def setupUi(self):
        self.verticalLayout_2 = utils.QVBoxLayout(self)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_4 = utils.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.line_2 = utils.QFrame(self)
        self.line_2.setFrameShape(utils.QFrame.HLine)
        self.line_2.setFrameShadow(utils.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.horizontalLayout_4.addWidget(self.line_2)
        self.Path_Label = utils.QLabel(self)
        self.Path_Label.setAlignment(utils.Qt.AlignCenter)
        self.Path_Label.setObjectName("Path_Label")
        self.horizontalLayout_4.addWidget(self.Path_Label)
        self.line_5 = utils.QFrame(self)
        self.line_5.setFrameShape(utils.QFrame.HLine)
        self.line_5.setFrameShadow(utils.QFrame.Sunken)
        self.line_5.setObjectName("line_5")
        self.horizontalLayout_4.addWidget(self.line_5)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.scrollArea = utils.QScrollArea(self)
        self.scrollArea.setFrameShape(utils.QFrame.StyledPanel)
        self.scrollArea.setFrameShadow(utils.QFrame.Plain)
        self.scrollArea.setLineWidth(1)
        self.scrollArea.setMidLineWidth(0)
        self.scrollArea.setHorizontalScrollBarPolicy(utils.Qt.ScrollBarAsNeeded)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.Path_Container = utils.QWidget()
        self.Path_Container.setGeometry(utils.QRect(0, 0, 403, 186))
        self.Path_Container.setObjectName("Path_Container")
        self.verticalLayout = utils.QVBoxLayout(self.Path_Container)
        self.verticalLayout.setObjectName("verticalLayout")
        self.Add_Container = utils.QWidget(self.Path_Container)
        sizePolicy = utils.QSizePolicy(utils.QSizePolicy.Preferred, utils.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Add_Container.sizePolicy().hasHeightForWidth())
        self.Add_Container.setSizePolicy(sizePolicy)
        self.Add_Container.setMaximumSize(utils.QSize(16777215, 30))
        self.Add_Container.setObjectName("Add_Container")
        self.horizontalLayout = utils.QHBoxLayout(self.Add_Container)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = utils.QSpacerItem(40, 20, utils.QSizePolicy.Expanding, utils.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.Add_BTN = utils.QPushButton(self.Add_Container)
        sizePolicy = utils.QSizePolicy(utils.QSizePolicy.Preferred, utils.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Add_BTN.sizePolicy().hasHeightForWidth())
        self.Add_BTN.setSizePolicy(sizePolicy)
        self.Add_BTN.setMinimumSize(utils.QSize(0, 0))
        self.Add_BTN.setAutoFillBackground(False)
        self.Add_BTN.setStyleSheet('''
            QPushButton{
                padding:5px;
                padding-bottom:8px;
                border-radius:10px;
                background:orange;
                color:white;
                font-size:25px;
                font:bold;
            }

            QPushButton::hover{
                color:rgb(255, 255, 0)
            }

            QPushButton::pressed {
                background:wheat
            }
        ''')
        self.Add_BTN.setObjectName("Add_BTN")
        self.horizontalLayout.addWidget(self.Add_BTN)


        self.Refresh_BTN = utils.QPushButton(self.Add_Container)
        sizePolicy = utils.QSizePolicy(utils.QSizePolicy.Preferred, utils.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Refresh_BTN.sizePolicy().hasHeightForWidth())
        self.Refresh_BTN.setSizePolicy(sizePolicy)
        self.Refresh_BTN.setMinimumSize(utils.QSize(0, 0))
        self.Refresh_BTN.setAutoFillBackground(False)
        self.Refresh_BTN.setStyleSheet('''
            QPushButton{
                padding:5px;
                padding-bottom:8px;
                border-radius:10px;
                background:orange;
                color:white;
                font-size:25px;
                font:bold;
            }

            QPushButton::hover{
                color:rgb(255, 255, 0)
            }

            QPushButton::pressed {
                background:wheat
            }
        ''')
        self.Refresh_BTN.setObjectName("Refresh_BTN")
        self.horizontalLayout.addWidget(self.Refresh_BTN)


        spacerItem1 = utils.QSpacerItem(40, 20, utils.QSizePolicy.Expanding, utils.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout.addWidget(self.Add_Container)
        spacerItem2 = utils.QSpacerItem(20, 40, utils.QSizePolicy.Minimum, utils.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.scrollArea.setWidget(self.Path_Container)
        self.verticalLayout_2.addWidget(self.scrollArea)

        utils.QMetaObject.connectSlotsByName(self)
        self.retranslateUi()

        self.Add_BTN.setText(u"+")
        self.Refresh_BTN.setText(u"↻")
        self.Add_BTN.clicked.connect(self.addPath)
        self.Refresh_BTN.clicked.connect(commands.store)

    def addPath(self):
        path = utils.QFileDialog.getExistingDirectory(self)

        if not os.path.exists(path):
            return

        # NOTE 重名判断
        if path in self.setting_win.setting_data:
            return
        
        self.addItem(path)

    def addItem(self,path,checked=True):
        
        item = PathItem(self.setting_win,path)
        item.setChecked(checked)
        layout = self.Path_Container.layout()
        layout.insertWidget(layout.count()-2,item)

    def retranslateUi(self):
        self.Path_Label.setText(utils.QApplication.translate("path", "Repo Search Path "))
        
    def changeEvent(self, event):
        if event.type() == utils.QEvent.LanguageChange:
            self.retranslateUi()
        super(SearchPathWidget, self).changeEvent(event)

# ----------------------------------------------------------------------------

class SettingWindow(utils.QWidget):
    
    def __init__(self,menu):
        super(SettingWindow,self).__init__()
        self.setupUi()
        
        self.setting_data = {}
        self.setting_data["path"] = {os.path.join(os.path.dirname(cmds.about(env=1)),"scripts"):True}
        self.ptr = None
        
        
        
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
        
        if os.path.exists(SETTING_PATH):
            self.importJsonSetting(SETTING_PATH)
        else:
            self.exportJsonSetting(SETTING_PATH)

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
    
    def setupUi(self):
        self.resize(379, 120)
        self.gridLayout = utils.QGridLayout()
        self.gridLayout.setContentsMargins(0,0,0,0)
        self.gridLayout.setObjectName("gridLayout")
        self.Scroll_Lock_SP = utils.QSpinBox()
        self.Scroll_Lock_SP.setObjectName("Scroll_Lock_SP")
        self.gridLayout.addWidget(self.Scroll_Lock_SP, 2, 3, 1, 1)
        self.Scroll_Lock_Label = utils.QLabel()
        self.Scroll_Lock_Label.setObjectName("Scroll_Lock_Label")
        self.gridLayout.addWidget(self.Scroll_Lock_Label, 2, 2, 1, 1)
        self.Languge_Label = utils.QLabel()
        self.Languge_Label.setObjectName("Languge_Label")
        self.gridLayout.addWidget(self.Languge_Label, 0, 0, 1, 1)
        # spacerItem = utils.QSpacerItem(20, 40, utils.QSizePolicy.Minimum, utils.QSizePolicy.Expanding)
        # self.gridLayout.addItem(spacerItem, 5, 0, 1, 1)
        self.Display_Label = utils.QLabel()
        self.Display_Label.setObjectName("Display_Label")
        self.gridLayout.addWidget(self.Display_Label, 3, 2, 1, 1)
        self.Display_SP = utils.QSpinBox()
        self.Display_SP.setMaximum(9999)
        self.Display_SP.setObjectName("Display_SP")
        self.gridLayout.addWidget(self.Display_SP, 3, 3, 1, 1)
        self.Scroll_Start_SP = utils.QSpinBox()
        self.Scroll_Start_SP.setObjectName("Scroll_Start_SP")
        self.gridLayout.addWidget(self.Scroll_Start_SP, 2, 1, 1, 1)
        self.Scroll_Start_Label = utils.QLabel()
        sizePolicy = utils.QSizePolicy(utils.QSizePolicy.Preferred, utils.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Scroll_Start_Label.sizePolicy().hasHeightForWidth())
        self.Scroll_Start_Label.setSizePolicy(sizePolicy)
        self.Scroll_Start_Label.setObjectName("Scroll_Start_Label")
        self.gridLayout.addWidget(self.Scroll_Start_Label, 2, 0, 1, 1)
        self.Shortcut_Label = utils.QLabel()
        self.Shortcut_Label.setObjectName("Shortcut_Label")
        self.gridLayout.addWidget(self.Shortcut_Label, 3, 0, 1, 1)
        self.Shortcut_SP = utils.QSpinBox()
        self.Shortcut_SP.setMaximum(9)
        self.Shortcut_SP.setObjectName("Shortcut_SP")
        self.gridLayout.addWidget(self.Shortcut_SP, 3, 1, 1, 1)
        self.Lang_Combo = utils.QComboBox()
        self.Lang_Combo.setObjectName("Lang_Combo")
        self.gridLayout.addWidget(self.Lang_Combo, 0, 1, 1, 3)

        self.Setting_Container = utils.QWidget()
        self.Setting_Container.setLayout(self.gridLayout)

        self.Path_Contianer = SearchPathWidget(self)
        self.splitter = utils.QSplitter(utils.Qt.Vertical)
        self.splitter.addWidget(self.Setting_Container)
        self.splitter.addWidget(self.Path_Contianer)

        layout = utils.QVBoxLayout()
        layout.setContentsMargins(9,20,9,9)
        self.setLayout(layout)
        layout.addWidget(self.splitter)

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
        self.exportJsonSetting(SETTING_PATH)
        
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
        self.setParent(utils.mayaWindow())

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
        self.Scroll_Start_SP.setValue    ( self.setting_data["Scroll_Start_SP"] )
        self.Scroll_Lock_SP.setValue     ( self.setting_data["Scroll_Lock_SP"]  )
        self.Shortcut_SP.setValue        ( self.setting_data["Shortcut_SP"]     )
        self.Display_SP.setValue         ( self.setting_data["Display_SP"]      )
        
        for path,checked in self.setting_data["path"].iteritems():
            self.Path_Contianer.addItem(path,checked)
        
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
        self.exportJsonSetting(SETTING_PATH)

    def scrollStart(self,value):
        self.search.scroll_start = value
        self.exportJsonSetting(SETTING_PATH)
    
    def display(self,value):
        self.search.display_num = value
        self.exportJsonSetting(SETTING_PATH)
    
    def shortcut(self,value):
        self.search.shortcut_num = value
        self.exportJsonSetting(SETTING_PATH)

