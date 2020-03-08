# coding:utf-8

__author__ =  'timmyliang'
__email__ =  '820472580@qq.com'
__date__ = '2020-03-04 21:55:38'

import json
import webbrowser
from . import utils

class CommandLauncherSwitch(utils.QPushButton):
    def __init__(self,parent=None):
        super(CommandLauncherSwitch,self).__init__(parent)
        self.setFlat(True)
        self.setFixedWidth(25)
        self.setFixedHeight(25)

        # NOTE 默认开启
        self.setIconColor()

        self.lancher_state = True

        self.menu = utils.QMenu()
        self.menu.setFixedWidth(120)
        self.setMenu(self.menu)

        self.divider = utils.Divider(self,"")
        self.add(self.divider)

        self.State_BTN = utils.QPushButton()
        self.State_BTN.clicked.connect(self.toggleState)
        self.add(self.State_BTN)

        self.Setting_BTN = utils.QPushButton()
        self.Setting_BTN.clicked.connect(self.openSettingWindow)
        self.add(self.Setting_BTN)

        self.Help_BTN = utils.QPushButton()
        self.Help_BTN.clicked.connect(lambda:webbrowser.open_new_tab(r"https://github.com/FXTD-ODYSSEY/CommandLauncher/blob/master/readme.md"))
        self.add(self.Help_BTN)
        
        self.retranslateUi()


    def getCommandLauncher(self):
        from . import getCommandLauncher
        COMMAND_LAUNCHER = getCommandLauncher()
        if COMMAND_LAUNCHER:
            return COMMAND_LAUNCHER

    def openSettingWindow(self):
        
        COMMAND_LAUNCHER = self.getCommandLauncher()
        if COMMAND_LAUNCHER:
            COMMAND_LAUNCHER.manager.setting.mayaShow()
    
    def toggleState(self,state=None):
        from . import setup,clean
        self.lancher_state = not self.lancher_state if state is None else state
        self.Setting_BTN.setEnabled(self.lancher_state)


        if self.lancher_state:
            setup()
            self.setIconColor()
        else:
            clean()
            self.setDarkColor()

        self.retranslateUi()

        from .setting import SETTING_PATH
        with open(SETTING_PATH,'r') as f:
            data = json.load(f,encoding="utf-8")
        
        if data["enable"] != self.lancher_state:
            data["enable"] = self.lancher_state
            with open(SETTING_PATH,'w') as f:
                json.dump(data,f,indent=4)

    def changeEvent(self, event):
        if event.type() == utils.QEvent.LanguageChange:
            self.retranslateUi()
        super(CommandLauncherSwitch, self).changeEvent(event)


    def retranslateUi(self):
        self.divider.setText(utils.QApplication.translate('icon','CommandLauncher'))
        text = utils.QApplication.translate('icon','OFF') if self.lancher_state else utils.QApplication.translate('icon','ON')
        self.State_BTN.setText(text)
        self.Setting_BTN.setText(utils.QApplication.translate('icon','setting'))
        self.Help_BTN.setText(utils.QApplication.translate('icon','help'))

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


# ----------------------------------------------------------------------------

BAR_CLOSE_ICON = ":/closeBar.png"
BAR_OPEN_ICON = ":/openBar.png"

class CommandLauncherIcon(utils.QWidget):

    def __init__(self,parent=None):
        super(CommandLauncherIcon,self).__init__(parent)
        
        # create bar
        self.bar = utils.QPushButton()
        self.bar.setFlat(True)
        self.bar.setFixedWidth(8)
        self.bar.setFixedHeight(25)   
        self.bar.setIcon(utils.QPixmap(BAR_CLOSE_ICON))
        self.bar.setIconSize(utils.QSize(8,25))
        self.bar.released.connect(self.switch)

        self.button = CommandLauncherSwitch()

        # create layout
        layout = utils.QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(1)

        layout.addWidget(self.bar)
        layout.addWidget(self.button)

    def switch(self):
        """
        Switch visibility of the widget, it is build in the same style as all
        if the maya status line ui elements.
        """
        if self.button.isVisible():
            self.button.setVisible(False)
            self.bar.setIcon(utils.QPixmap(BAR_CLOSE_ICON))
        else:
            self.button.setVisible(True)
            self.bar.setIcon(utils.QPixmap(BAR_OPEN_ICON))

