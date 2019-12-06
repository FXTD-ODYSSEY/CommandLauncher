# coding:utf-8

__author__ =  'timmyliang'
__email__ =  '820472580@qq.com'
__date__ = '2019-12-05 14:27:16'

from . import manager, results, utils
from .. import commands
from maya import cmds
# ---------------------------------------------------------------------------

BAR_CLOSE_ICON = ":/closeBar.png"
BAR_OPEN_ICON = ":/openBar.png"

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
        
        # NOTE get commands
        if not commands.get():
            commands.store()
        
        self.timer = utils.QTimer()
        self.timer_count = 0
        self.tab_long_press = 0
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.timerEvent)

        # NOTE variable
        self.setObjectName("CMDSearch")
        
        # NOTE create layout
        layout = utils.QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(1)
        
        # NOTE create container
        self.container = utils.QWidget(self)
        self.container.setFixedWidth(250)
        
        # add widgets
        layout.addWidget(self.container)
        
        # create layout
        layout = utils.QHBoxLayout(self.container)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(1)
        
        self.search_button = utils.QPushButton(self)
        self.search_button.setFlat(True)
        self.search_button.setFixedWidth(25)
        self.search_button.setFixedHeight(25)   
        self.search_button.setIcon(utils.findSearchIcon())
        self.search_button.setIconSize(utils.QSize(25,25))   
        
        
        
        self.manger_menu = manager.ManagerMenu(self)
        self.search_button.setMenu(self.manger_menu)
        
        # NOTE window
        self.window = results.ResultsWindow(self)
        self.window.aboutToClose.connect(self.closeWindowEvent)
        
        # NOTE menu
        self.menu = results.ResultsMenu(self)
        self.menu.aboutToClose.connect(self.closeMenuEvent)
        
        self.results = self.menu
        
        self.search = SearchEdit(self, self.container,self.results)
        
        # NOTE add widgets
        layout.addWidget(self.search_button)
        layout.addWidget(self.search)
          
        # NOTE add signals
        self.search.textChanged.connect(self.typing)
        self.search.returnPressed.connect(self.enter)


        self.resize(250,25)
        # Note 初始化 Application 的事件
        app = utils.QApplication.instance()
        app.installEventFilter(self)

    # ------------------------------------------------------------------------

    def timerEvent(self):
        u'''
        timerEvent 计时器事件
        
        计时器启动后不断累加
        如果计时器累加了两次则说明是单击
        停止计时器并且触发单击事件
        '''
        self.timer.stop()
        if self.timer_count < 1:
            # NOTE 如果小于等于 3 说明不是长按
            if self.tab_long_press <=3:
                self.show()
            self.tab_long_press = 0
        else:
            self.hide()
            self.results.hide()
            
        self.timer_count = 0

    def eventFilter(self,receiver,event):
        # NOTE 键盘事件
        if hasattr(event,"type") and event.type() == utils.QEvent.KeyPress:
            # NOTE 敲击 Tab 键
            if event.key() == 16777217:
                self.tab_long_press += 1
                if self.timer.isActive():
                    self.timer_count += 1
                else:
                    self.timer.start()

            # NOTE 敲击 Esc 键
            elif event.key() == 16777216:
                self.hide()
                self.results.hide()
                cmds.selectPref(ps=0)
                self.tab_long_press = 0
            else:
                self.tab_long_press = 0

            
        # Note 鼠标事件 QEvent.Type.MouseButtonPress 为 2
        elif hasattr(event,"type") and event.type() == 2 and self.isVisible():
            print receiver
            # Note 过滤接受的组件是否是自己 避免其他组件触发 如 PySide2 QWindow 也会传入进来
            if (
                'QWindow' not in str(receiver) and
                receiver not in self.children() and
                receiver not in self.container.children() and
                receiver not in self.manger_menu.children() and
                receiver.window() != self.results and
                receiver != self and
                type(receiver.parent()) != utils.Divider
            ):
                self.hide()
                cmds.selectPref(ps=0)

            self.tab_long_press = 0


        return False   
    
    # ------------------------------------------------------------------------

    def typing(self):
        """
        Typing callback, since there are many commands to filter through, 
        when typing it will only start processing when there are at least
        4 characters typed.
        """
        self.search.selected = 0
        self.process(4)
 
    def enter(self):  
        """
        Enter callback, will call the process function regardless of how many
        characters the input field holds, used when you want to search for 
        something with less than 4 char
        """
        self.process(0)
        
    # ------------------------------------------------------------------------
    
    def process(self, num):
        """
        Process the search command, the number determines how many characters
        the search string should at least be for it to continue.
        
        :param int num: Search character number at least before process
        """
        # filter search
        search = str(self.search.text())
        if len(search) < num:      
            search = None
          
        # filter commands
        matches = commands.filter(search)

        # add commands
        widget = self.results.widget
        widget.populate(matches)
        
        # display
        num = len(matches)
        self.results.show(num)

        # set focus
        self.search.setFocus()

    # ------------------------------------------------------------------------
    
    def closeWindowEvent(self):
        self.results.hide()
        self.results = self.menu
        
    def closeMenuEvent(self):
        self.results.hide()
        self.results = self.window
        
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
        self.vert_selected = 0
        self.scrollY = 0
    # -----------------------------------------------------------------------

    def mouseReleaseEvent(self, e): 
        if e.button() == utils.Qt.LeftButton:                
            if not self.parent.results.isVisible():
                self.parent.typing()
        return super(SearchEdit,self).mouseReleaseEvent(e)

    def keyPressEvent(self,event):
        key = event.key()
        # print key
        self.count = self.results.widget.layout.count() - 2

        self.scrollY = 0
        scroll = self.results.widget.scrollArea.verticalScrollBar()
        self.vert_selected = 0
        vert_max = 1


        # NOTE 还原样式
        if self.selected != 0:
            item = self.currentItem()
            item.setStyleSheet("")
            
        
        # NOTE 按左箭头
        if key == 16777234:
            if self.selected <= 0:
                self.update()
                return super(SearchEdit,self).keyPressEvent(event)
            self.vert_selected -= 1
            self.vert_selected = -1 if self.vert_selected < -1 else self.vert_selected

        # NOTE 按右箭头
        elif key == 16777236:
            if self.selected <= 0:
                self.update()
                return super(SearchEdit,self).keyPressEvent(event)
            self.vert_selected += 1
            self.vert_selected = 1 if self.vert_selected > vert_max else self.vert_selected


        # NOTE 按上箭头
        elif key == 16777235:
            print self.hasFocus()
            self.selected -= 1
            if self.selected <= 0:
                self.selected = 0
                self.setFocus()
                self.update()
                return

            item = self.currentItem()
     
            item.setStyleSheet("color:coral")

            # NOTE 设置滚动值
            if self.selected > 5:
                y = scroll.value()
                scroll.setValue(y-self.scrollY)
            else:
                scroll.setValue(0)

            print item.info.get("name")

        # NOTE 按下箭头
        elif key == 16777237:
            print self.hasFocus()

            self.selected += 1
            self.selected = self.selected % self.count

            item = self.currentItem(False)
            item.setStyleSheet("color:coral")

            # NOTE 设置滚动值
            if self.selected > 5:
                y = scroll.value()
                scroll.setValue(y+self.scrollY)
            else:
                scroll.setValue(0)

            print item.info.get("name")

        else:
            return super(SearchEdit,self).keyPressEvent(event)

    def currentItem(self,dn=True):
        layout = self.results.widget.layout
        item = layout.itemAt(self.selected).widget()
        self.scrollY += item.height()
        if type(item) == utils.Divider:

            if dn:
                self.selected -= 1
            else:
                self.selected += 1

            item = layout.itemAt(self.selected).widget()
            self.scrollY += item.height()

        return item

