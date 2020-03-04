# coding:utf-8
from .utils import *
from .search import *
from .manager import *
from .results import *
from .commands import *

import threading
# ----------------------------------------------------------------------------

global COMMAND_SEARCH_ICON
COMMAND_SEARCH_ICON = None
global COMMAND_LAUNCHER
COMMAND_LAUNCHER = None

# ----------------------------------------------------------------------------

def setup(): 

    global COMMAND_LAUNCHER
    
    # validate timeline marker
    if COMMAND_LAUNCHER:
        raise RuntimeError("Command search is already installed!")

    COMMAND_LAUNCHER = SearchWidget(mayaWindow())

    thread = threading.Thread(target=COMMAND_LAUNCHER.initialize)
    thread.start()

    return COMMAND_LAUNCHER

def clean():
    for w in utils.mayaWindow().children():
        if str(type(w)) == str(SearchWidget):
            w.deleteLater()
    global COMMAND_SEARCH_ICON
    COMMAND_SEARCH_ICON = None
    global COMMAND_LAUNCHER
    COMMAND_LAUNCHER = None
    
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

    # create command search
    COMMAND_SEARCH_ICON = CommandLauncherIcon(parent)
    layout.addWidget(COMMAND_SEARCH_ICON)

    # setup CommandLauncher
    setup()

