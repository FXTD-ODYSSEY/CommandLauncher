# coding:utf-8

__author__ =  'timmyliang'
__email__ =  '820472580@qq.com'
__date__ = '2019-12-05 14:27:16'

from . import manager, results, utils
from .. import commands
from maya import mel
from maya import cmds
# ---------------------------------------------------------------------------


WIDTH = 320

# ---------------------------------------------------------------------------
    
class SearchWidget(utils.QWidget):
    """
    Search Widget 
    
    The search widget will give access to all of the functionality in the 
    command search package.
    
    * Search input field.
    * Pin set manager.
    * Search results.
    
    :param QWidget parent:
    """
    def __init__(self, parent=None):
        utils.QWidget.__init__(self, parent)
        
        
        
        # NOTE create layout
        layout = utils.QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(1)
        
        # NOTE create container
        self.container = utils.QWidget(self)
        self.container.setFixedWidth(WIDTH)
        
        # NOTE add widgets
        layout.addWidget(self.container)
        
        # NOTE create layout
        layout = utils.QHBoxLayout(self.container)
        layout.setContentsMargins(5,0,5,0)
        layout.setSpacing(5)
        
        self.search_button = utils.QPushButton(self)
        self.search_button.setFlat(True)
        self.search_button.setFixedWidth(25)
        self.search_button.setFixedHeight(25)   
        self.search_button.setIcon(utils.findSearchIcon())
        self.search_button.setIconSize(utils.QSize(25,25))   
        
        # NOTE window
        self.ResultsWindow = results.ResultsWindow(self)
        
        # NOTE menu
        self.menu = results.ResultsMenu(self)
        
        self.results = self.menu
        
        self.search = SearchEdit(self, self.container,self.results)
        
        self.filter = utils.QLabel()
        
        # NOTE add widgets
        layout.addWidget(self.search_button)
        layout.addWidget(self.filter)
        layout.addWidget(self.search)

        self.manager = manager.ManagerMenu(self)
        
        # NOTE 添加计时器
        self.timer = utils.QTimer()
        self.timer_count = 0
        self.tab_long_press = 0
        self.timer.setInterval(100)

        self.resize(WIDTH,25)

        
        
        # Note 初始化 Application 的事件
        app = utils.QApplication.instance()
        app.installEventFilter(self)

        # NOTE variable
        self.setObjectName("CommandLuancherSearchWidget")

         # NOTE 填充底色 https://stackoverflow.com/questions/29762651/autodesk-maya-model-panel-resize-event
        self.setAutoFillBackground(True)

    # ------------------------------------------------------------------------
    
    def initialize(self):

        # NOTE get commands
        if not commands.get():
            self.menu_list = commands.store()
        else:
            self.menu_list = commands.getMenuList()

        # NOTE add signals
        self.menu.aboutToClose.connect(self.closeMenuEvent)
        self.ResultsWindow.aboutToClose.connect(self.closeWindowEvent)

        self.search.textChanged.connect(self.typing)
        self.search.returnPressed.connect(self.enter)
        
        self.search_button.setMenu(self.manager)
        self.timer.timeout.connect(self.timerEvent)

        self.filter.hide()
        self.filter.setStyleSheet("color:orange")

    # ------------------------------------------------------------------------

    def timerEvent(self):
        u'''
        timerEvent 计时器事件
        
        计时器启动后不断累加
        如果计时器累加了两次则说明是单击
        停止计时器并且触发单击事件
        '''
        self.timer.stop()
        # print "tab_long_press",self.tab_long_press
        # print "timer_count",self.timer_count
        if self.timer_count <= 1:
            # NOTE 如果小于等于 3 说明不是长按
            if self.tab_long_press <=3:
                self.show()
                # NOTE 选择输入
                self.search.selectAll()
                self.search.jumpToPins()
                
                
            self.tab_long_press = 0
        else:
            if self.tab_long_press == 0:
                cmds.selectPref(psf=0,ps=0)
            if self.isVisible():
                self.hide()
                self.results.hide()

            
        self.timer_count = 0

    def eventFilter(self,receiver,event):
        # NOTE 键盘事件
        if hasattr(event,"type") and event.type() == utils.QEvent.KeyRelease:
            # NOTE 敲击 Tab 键
            if event.key() == utils.Qt.Key_Tab and not self.isVisible():
                self.tab_long_press += 1
                if not event.isAutoRepeat():
                    cmds.selectPref(psf=1,ps=1)
                    # mel.eval("dR_paintPress;")
                    self.tab_long_press = 0

                if self.timer.isActive():
                    self.timer_count += 1
                else:
                    self.timer.start()
                    

            # NOTE 敲击 Esc 键
            elif event.key() == utils.Qt.Key_Escape:
                self.hide()
                self.results.hide()
                # mel.eval("dR_paintRelease;")
                # cmds.setToolTo(self.curr_ctx)
                cmds.selectPref(psf=0,ps=0)
                self.tab_long_press = 0
            else:
                self.tab_long_press = 0

            
        # Note 鼠标事件 QEvent.Type.MouseButtonPress 为 2
        elif hasattr(event,"type") and event.type() == 2 and self.isVisible():
            # Note 过滤接受的组件是否是自己 避免其他组件触发 如 PySide2 QWindow 也会传入进来
            if (
                'QWindow' not in str(receiver) and
                receiver not in self.children() and
                receiver not in self.container.children() and
                receiver not in self.manager.children() and
                receiver.window() != self.results and
                receiver != self and
                type(receiver.parent()) != utils.Divider
            ):
                self.hide()
                # mel.eval("dR_paintRelease;")
                # cmds.setToolTo(self.curr_ctx)
                cmds.selectPref(psf=0,ps=0)

            self.tab_long_press = 0


        return False   
    
    # def paintEvent(self,event):
    #     # NOTE 填充底色，避免背景错乱
    #     painter=utils.QPainter()
    #     painter.begin(self)
    #     painter.fillRect(event.rect(),utils.QColor('#444444'))
    #     painter.end()
    #     return super(SearchWidget,self).paintEvent(event)
    
    # ------------------------------------------------------------------------

    def typing(self):
        """
        Typing callback, since there are many commands to filter through, 
        when typing it will only start processing when there are at least
        4 characters typed.
        """
        self.process(4)
        
 
    def enter(self):  
        """
        Enter callback, will call the process function regardless of how many
        characters the input field holds, used when you want to search for 
        something with less than 4 char
        """
        # NOTE 如果搜索框弹出，执行第一个命令按钮
        if self.results.isVisible():
            self.search.triggerShortcut(1)
        else:
            self.process(0)
        
    # ------------------------------------------------------------------------
    
    def process(self, num):
        """
        Process the search command, the number determines how many characters
        the search string should at least be for it to continue.
        
        :param int num: Search character number at least before process
        """
        # NOTE filter search 支持中文搜索
        search = self.search.text().encode("utf-8")
        if len(search) < num:      
            search = None
          
        # filter commands
        matches = commands.filter(search)

        if self.search.filter_mode:
            matches = filter(lambda x: x["category"] == self.search.filter_mode, matches)

        # NOTE 默认只显示 100 个结果提高搜索效率
        if self.search.display_num:
            matches = matches[:self.search.display_num] if len(matches) > self.search.display_num else matches

        # add commands
        widget = self.results.widget
        widget.populate(matches)
        
        # display
        num = len(matches)
        self.results.show(num)

        # set focus
        self.search.setFocus()
        
        self.search.selected = 0
        scroll = self.results.widget.scrollArea.verticalScrollBar()
        scroll.setValue(0)
        self.search.showShortcut()
        

    # ------------------------------------------------------------------------
    
    def closeWindowEvent(self):
        self.results.hide()
        self.results = self.menu
        
    def closeMenuEvent(self):
        self.results.hide()
        self.results = self.ResultsWindow
        
        self.typing()

    # ------------------------------------------------------------------------

    def show(self):
        pos = utils.QCursor.pos()
        self.move(pos.x(), pos.y())
        self.search.setFocus()
        self.search.selected = 0
        # NOTE 如果文字留存则显示上次输入的
        if self.search.text():
            self.typing()
        self.setVisible(True)
        # super(SearchWidget,self).show()

# ----------------------------------------------------------------------------

class SearchEdit(utils.QLineEdit):
    """
    Subclass of a line edit to force it to show the parents results window
    on release of the left buttons.
    """
    def __init__(self, parent, widgetParent,results):
        utils.QLineEdit.__init__(self, widgetParent)
        self.parent = parent
        self.results = results
        
        self.selected = 0
        self.mode = 0
        
        self.shortcut = {}
        self.filter_mode = ""
        self.filter_label_dict = {
            "cmds"  : lambda:utils.QApplication.translate('filter','cmds'),
            "menu"  : lambda:utils.QApplication.translate('filter','menu'),
            "shelf" : lambda:utils.QApplication.translate('filter','shelf'),
            "script" : lambda:utils.QApplication.translate('filter','script'),
            "command" : lambda:utils.QApplication.translate('filter','command'),
        }

        self.scroll_start = 3
        self.scroll_locked = 4
        self.shortcut_num = 8
        self.display_num = 100
    
    def changeEvent(self, event):
        if event.type() == utils.QEvent.LanguageChange:
            self.retranslateUi()
        super(SearchEdit, self).changeEvent(event)

    def retranslateUi(self):
        filter = self.parent.filter
        if self.filter_mode in self.filter_label_dict:
            text = self.filter_label_dict[self.filter_mode]()
            filter.setText(text)

    # -----------------------------------------------------------------------
    def filterDisplay(self,mode):
        """filterDisplay 过滤模式切换
        
        Parameters
        ----------
        mode : str
            模式名称
        """
        if mode not in self.filter_label_dict:
            return 

        filter_label = self.parent.filter

        if filter_label.isVisible() and self.filter_label_dict[mode]() == filter_label.text():
            filter_label.hide()
            self.filter_mode = ""
        else:
            filter_label.show()
            self.filter_mode = mode
            self.retranslateUi()
        self.parent.process(4)
            
    def mouseReleaseEvent(self, e): 
        if e.button() == utils.Qt.LeftButton:                
            if not self.parent.results.isVisible():
                self.parent.typing()
        return super(SearchEdit,self).mouseReleaseEvent(e)
    
    def keyPressEvent(self,event):
        
        key = event.key()
        KeySequence = utils.QKeySequence(key+int(event.modifiers()))
        # print "key",key
        
        # NOTE 阻断 ctrl 键实现打字法任意切换
        if key == utils.Qt.Key_Control:
            return
        # NOTE 点击 shfit 键 不会导致失焦
        if key == utils.Qt.Key_Shift:
            return
        # NOTE 开启 menu 过滤模式
        elif KeySequence == utils.QKeySequence("Ctrl+Q"):
            return self.filterDisplay("menu")
        # NOTE 开启 shelf 过滤模式
        elif KeySequence == utils.QKeySequence("Ctrl+W"):
            return self.filterDisplay("shelf")
        # NOTE 开启 cmds 过滤模式
        elif KeySequence == utils.QKeySequence("Ctrl+E"):
            return self.filterDisplay("cmds")
        # NOTE 开启 command 过滤模式
        elif KeySequence == utils.QKeySequence("Ctrl+R"):
            return self.filterDisplay("command")
        elif KeySequence == utils.QKeySequence("Ctrl+T"):
            return self.filterDisplay("script")
         # NOTE 打开搜索菜单
        elif KeySequence == utils.QKeySequence("Ctrl+`"):
            return self.parent.manager.aboutToShow_()
        elif KeySequence == utils.QKeySequence("ctrl+alt+1"):
            return self.jumpToPins(1)
        elif KeySequence == utils.QKeySequence("ctrl+alt+2"):
            return self.jumpToPins(2)
        elif KeySequence == utils.QKeySequence("ctrl+alt+3"):
            return self.jumpToPins(3)
        elif KeySequence == utils.QKeySequence("ctrl+alt+4"):
            return self.jumpToPins(4)
        elif KeySequence == utils.QKeySequence("ctrl+alt+5"):
            return self.jumpToPins(5)
        elif KeySequence == utils.QKeySequence("ctrl+alt+6"):
            return self.jumpToPins(6)
        elif KeySequence == utils.QKeySequence("ctrl+alt+7"):
            return self.jumpToPins(7)
        elif KeySequence == utils.QKeySequence("ctrl+alt+8"):
            return self.jumpToPins(8)
        elif KeySequence == utils.QKeySequence("ctrl+alt+9"):
            return self.jumpToPins(9)

        self.count = self.results.widget.layout.count() - 1
        if self.count < 1:
            return super(SearchEdit,self).keyPressEvent(event)
        
        # NOTE 快捷键显示
        if key == utils.Qt.Key_Control:
            for _,[item,_] in self.shortcut.items():
                shortcut = item.shortcut.text()
                shortcut = shortcut.replace("alt","ctrl")
                item.shortcut.setText(shortcut)
            return
        elif key == utils.Qt.Key_Alt:
            for _,[item,_] in self.shortcut.items():
                shortcut = item.shortcut.text()
                shortcut = shortcut.replace("ctrl","alt")
                item.shortcut.setText(shortcut)
            return
       
        # NOTE 还原样式
        elif self.selected != 0:
            item = self.currentItem()
            self.setCommandStyle(item)
        
        # NOTE 按上箭头
        if key == utils.Qt.Key_Up:
            self.pressUpKey()

        # NOTE 按下箭头
        elif key == utils.Qt.Key_Down:
            self.pressDownKey()
            
        # NOTE 按左箭头
        elif key == utils.Qt.Key_Left and self.selected != 0:
            self.pressLeftKey()

        # NOTE 按右箭头
        elif key == utils.Qt.Key_Right and self.selected != 0:
            self.pressRightKey()

        # NOTE 点击 Enter 或 Return 键
        elif (key == utils.Qt.Key_Enter or key == utils.Qt.Key_Return)and self.selected != 0 and self.results.isVisible():
            self.pressEnterKey()
            

        # # NOTE 点击 ` 键 打开菜单
        # elif key == utils.Qt.Key_QuoteLeft:
        #     print utils.QKeySequence("Ctrl+1")
        #     print utils.QKeySequence("Shift+1")
        #     print utils.QKeySequence("Ctrl+Shift+1")
            # menu = item.info["menu"]
     
            # for child in menu.children():
            #     if type(child) == utils.QWidgetAction:
            #         if item.info["name"] in child.text():
            #             # # print dir(child)
            #             # label = utils.QLabel("TEST")
            #             # # label.setText(child.text())
            #             # label.setStyleSheet("background-color : red")
            #             # child.setDefaultWidget(label)
            #             break
                
            # # pos = utils.QCursor.pos()
            # # pos = utils.QPoint(pos.x()-50,pos.y()-h)
            # menu.showTearOffMenu()

            # self.parent.hide()
            # self.parent.results.hide()
        
        # NOTE 设置 Ctrl 快捷键
        elif KeySequence == utils.QKeySequence("ctrl+1"):
            self.triggerShortcut(1)
        elif KeySequence == utils.QKeySequence("ctrl+2"):
            self.triggerShortcut(2)
        elif KeySequence == utils.QKeySequence("ctrl+3"):
            self.triggerShortcut(3)
        elif KeySequence == utils.QKeySequence("ctrl+4"):
            self.triggerShortcut(4)
        elif KeySequence == utils.QKeySequence("ctrl+5"):
            self.triggerShortcut(5)
        elif KeySequence == utils.QKeySequence("ctrl+6"):
            self.triggerShortcut(6)
        elif KeySequence == utils.QKeySequence("ctrl+7"):
            self.triggerShortcut(7)
        elif KeySequence == utils.QKeySequence("ctrl+8"):
            self.triggerShortcut(8)
        elif KeySequence == utils.QKeySequence("ctrl+9"):
            self.triggerShortcut(9)
            
        # NOTE 设置 Alt 快捷键
        elif KeySequence == utils.QKeySequence("alt+1"):
            self.jumpToShortcut(1)
        elif KeySequence == utils.QKeySequence("alt+2"):
            self.jumpToShortcut(2)
        elif KeySequence == utils.QKeySequence("alt+3"):
            self.jumpToShortcut(3)
        elif KeySequence == utils.QKeySequence("alt+4"):
            self.jumpToShortcut(4)
        elif KeySequence == utils.QKeySequence("alt+5"):
            self.jumpToShortcut(5)
        elif KeySequence == utils.QKeySequence("alt+6"):
            self.jumpToShortcut(6)
        elif KeySequence == utils.QKeySequence("alt+7"):
            self.jumpToShortcut(7)
        elif KeySequence == utils.QKeySequence("alt+8"):
            self.jumpToShortcut(8)
        elif KeySequence == utils.QKeySequence("alt+9"):
            self.jumpToShortcut(9)
            
        else:
            return super(SearchEdit,self).keyPressEvent(event)
    
    def pressEnterKey(self):
        item = self.currentItem()
        if self.mode == 0:
            item.exec_()
            self.parent.hide()

        elif self.mode == 1:
            item.execOption_()
            self.parent.hide()
        elif self.mode == -1:
            if item.info["pin"]:
                item.setUnpin()
            else:
                item.setPin()
            self.setCommandStyle(item,self.mode)

    def pressRightKey(self):
        item = self.currentItem()
        self.mode += 1
        self.mode = 1 if self.mode > 1 else self.mode
        if self.mode == 1 and not item.commandOption:
            self.mode = 0
        
        self.setCommandStyle(item,self.mode)
        
    def pressLeftKey(self):
        item = self.currentItem()
        
        self.mode -= 1
        self.mode = -1 if self.mode < -1 else self.mode
        self.setCommandStyle(item,self.mode)
        
    def pressUpKey(self):
        self.scrollBar = self.results.widget.scrollArea.verticalScrollBar()
        self.selected -= 1
        if self.selected <= 0:
            self.selected = 0
            self.setFocus()
            self.update()
            return

        item = self.currentItem()
        item.setStyleSheet("color:coral")

        # NOTE 设置滚动值
        if self.selected > self.scroll_start:
            height = self.scrollHeight()
            self.scrollBar.setValue(height)
        else:
            self.scrollBar.setValue(0)

        self.setCommandStyle(item,self.mode)
        self.showShortcut()
    
    def pressDownKey(self):
        self.scrollBar = self.results.widget.scrollArea.verticalScrollBar()
        self.count = self.results.widget.layout.count() - 1
        if self.count == 0:
            return
        
        self.selected += 1
        self.selected = self.selected % self.count

        item = self.currentItem(False)

        # NOTE 设置滚动值
        if self.selected > self.scroll_start:
            height = self.scrollHeight()
            self.scrollBar.setValue(height)
        else:
            self.scrollBar.setValue(0)

        self.setCommandStyle(item,self.mode)
        self.showShortcut()
    
    def jumpToPins(self,num=0):
        manager = self.parent.manager
        if num:
            pins_list = manager.setActive(num)
            self.parent.typing()
            if not self.parent.results.isVisible() and pins_list:
                widget = self.parent.results.widget
                widget.populate(pins_list)
                self.parent.results.show(len(pins_list))
                self.pressDownKey()
        else:
            if not hasattr(manager,"group"):return
            btn = manager.group.checkedButton()
            if not btn and not self.parent.results.isVisible():
                pins_list = manager.getActive()
                widget = self.parent.results.widget
                widget.populate(pins_list)
                self.parent.results.show(len(pins_list))
                self.pressDownKey()
            
    def jumpToShortcut(self,num):
        if self.shortcut.has_key(num):
            item,index = self.shortcut[num]
            self.selected = index
            # # NOTE 设置滚动值
            # scroll = self.results.widget.scrollArea.verticalScrollBar()
            # if self.selected > self.scroll_start:
            #     height = self.scrollHeight()
            #     scroll.setValue(height)
            # else:
            #     scroll.setValue(0)

            self.setCommandStyle(item,self.mode)
            self.showShortcut()
        elif self.selected != 0:
            item = self.currentItem()
            self.setCommandStyle(item,0)
            
    def triggerShortcut(self,num):
        if self.shortcut.has_key(num):
            item,_ = self.shortcut[num]
            try:
                item.exec_()
                self.parent.hide()
            except:
                import traceback
                traceback.print_exc()

    def showShortcut(self):
        scroll = self.results.widget.scrollArea.verticalScrollBar()
        # NOTE 显示快速快捷输入数字键
        if self.selected > self.scroll_locked and scroll.isVisible():
            self.showItemShortcut(self.selected - self.scroll_locked)
        else:
            self.showItemShortcut()
            
    def showItemShortcut(self,start=0):
        self.clearItemShortcut()
        layout = self.results.widget.layout
        display = 0
        index = start
        while display < self.shortcut_num:
            index += 1
            item = layout.itemAt(index)
            # NOTE 说明当前数量小于快捷键数量
            if item == None:break
                
            item = item.widget()
            if not item or type(item) == utils.Divider:
                continue
            display += 1

            shortcut = "alt + %s" % (display)
            item.shortcut.setText(shortcut)
            self.shortcut[display] = item,index
                
    def clearItemShortcut(self):
        u"""
        clearItemShortcut 清理热键显示
        """
        self.shortcut = {}
        layout = self.results.widget.layout
        for count in range(layout.count()):
            item = layout.itemAt(count).widget()
            if not item or type(item) == utils.Divider:
                continue
            if item.shortcut.text():
                item.shortcut.setText("")

    def currentItem(self,up=True):
        layout = self.results.widget.layout
        item = layout.itemAt(self.selected).widget()
        if type(item) == utils.Divider:

            if up:
                self.selected -= 1
            else:
                self.selected += 1

            item = layout.itemAt(self.selected).widget()
        return item
    
    def scrollHeight(self):
        layout = self.results.widget.layout
        height = 0
        for i in range(self.selected):
            item = layout.itemAt(i).widget()
            height += item.height()
        return height - self.scroll_start * 20

    def setCommandStyle(self,item,mode=2):
        style = "QPushButton{ \
                border: 1px solid orange; \
                border-radius: 3px; \
                background-color: orange; \
            }"
        hover = "QPushButton:hover{ \
                border: 1px solid orange; \
                border-radius: 3px; \
                background-color: orange; \
            }"

        if mode == 0:
            item.setStyleSheet("color:coral")
            item.pin.setStyleSheet(hover)
            if item.commandOption:
                item.option.setStyleSheet(hover)
        elif mode == -1:
            item.setStyleSheet("")
            item.pin.setStyleSheet(style)
            if item.commandOption:
                item.option.setStyleSheet(hover)
        elif mode == 1:
            item.setStyleSheet("")
            item.pin.setStyleSheet(hover)
            if item.commandOption:
                item.option.setStyleSheet(style)
            else:
                # NOTE 说明当前item没有选项，自动跳转到中间
                self.mode -= 1
                self.setCommandStyle(item,self.mode)
        else:
            item.setStyleSheet("")
            item.pin.setStyleSheet(hover)
            if item.commandOption:
                item.option.setStyleSheet(hover)