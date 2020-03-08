# coding:utf-8
from .utils import *
from .search import *
from .manager import *
from .results import *
from .commands import *


from maya import cmds

# ----------------------------------------------------------------------------

global COMMAND_SEARCH_ICON
COMMAND_SEARCH_ICON = None
global COMMAND_LAUNCHER
COMMAND_LAUNCHER = None

# ----------------------------------------------------------------------------

class Worker(QRunnable):
    def __init__(self,func):
        super(Worker,self).__init__()
        self.func = func
    def run(self):
        self.func()

def setup(): 

    global COMMAND_LAUNCHER
    
    # validate timeline marker
    if COMMAND_LAUNCHER:
        raise RuntimeError("Command search is already installed!")
    
    COMMAND_LAUNCHER = SearchWidget(mayaWindow())

    thread = QThreadPool()
    thread.start(Worker(COMMAND_LAUNCHER.initialize))


def clean():
    for w in mayaWindow().children():
        if str(type(w)) == str(SearchWidget):
            # NOTE 删除设定窗口
            setting = w.manager.setting
            if w.parent() != setting.window():
               setting.window().close()
            setting.deleteLater()
            w.deleteLater()
    global COMMAND_SEARCH_ICON
    COMMAND_SEARCH_ICON = None
    global COMMAND_LAUNCHER
    COMMAND_LAUNCHER = None
    
def getCommandLauncher():
    global COMMAND_LAUNCHER
    return COMMAND_LAUNCHER
# ----------------------------------------------------------------------------
        
def install():
    """
    Add the cmd search functionality to Maya's native status bar.
    
    :raises RuntimeError: When the command search is already installed.
    """
    global COMMAND_SEARCH_ICON
    
    if COMMAND_SEARCH_ICON:
        raise RuntimeError("Command search is already installed!")

    # convert status line
    statusLine = getStatusLine()
    
    # get parent
    parent = mayaWindow()
    
    # get layout        
    layout = statusLine.layout()  

    # create CommandLauncher Icon to status line
    from .statusIcon import CommandLauncherIcon
    COMMAND_SEARCH_ICON = CommandLauncherIcon(parent)
    layout.addWidget(COMMAND_SEARCH_ICON)

    # setup CommandLauncher
    from .setting import SETTING_PATH
    with open(SETTING_PATH,'r') as f:
        data = json.load(f,encoding="utf-8")
    if data.get("enable"):
        cmds.evalDeferred(setup)
    else:
        COMMAND_SEARCH_ICON.button.toggleState(False)