# coding:GBK

__author__ =  'timmyliang'
__email__ =  '820472580@qq.com'
__date__ = '2019-12-05 11:19:04'

"""
查找 Maya 下拉菜单的各个选项
"""
import os
import sys

# NOTE 判断当前环境是否存在 Qt.py
if not 'Qt' in sys.modules:
    for path in sys.path:
        if os.path.exists(os.path.join(path,"Qt.py")):
            break
    else:
        doc = os.path.dirname(cmds.about(env=1))
        os.path.join(doc,"scirpts")
        

from Qt.QtGui import *
from Qt.QtCore import *
from Qt.QtWidgets import *
from Qt.QtCompat import wrapInstance

from maya import OpenMayaUI


def mayaWindow():
    """
    Get Maya's main window.
    
    :rtype: QMainWindow
    """
    window = OpenMayaUI.MQtUtil.mainWindow()
    window = wrapInstance(long(window), QMainWindow)
    return window
    
def mayaMenu():
    """
    Find Maya's main menu bar.
    
    :rtype: QMenuBar
    """
    for m in mayaWindow().children():
        if type(m) == QMenuBar:
            return m

def store(parent, parents=[]):
    """
    Process the parent to see if any if its children meet the search 
    command requirements. If so, the button and commands will be added 
    to the commands variable.
    
    :param QWidget parent: direct parent
    :param list parents: linked menu's
    """
    children = parent.children()
    for i, item in enumerate(children):
        # tree
        tree = parents[:]
    
        # get items
        name = item.objectName().encode("utf-8")
        
        # skip if no item name
        if not name:
            continue
            
        # process menu
        if type(item) == utils.QMenu:
            tree.append(
                item.title().encode("utf-8")
                # getMenu(item)
            )
            
        # process item
        elif type(item) == utils.QWidgetAction:  
            # get dynamic p
            dynamic = item.dynamicPropertyNames()
            # break
            if "isOptionBox" in dynamic:
                print dynamic
            #     # main item
            #     getItem(item, name, tree)
            # else:
            #     # option box item
            #     getItemOptionBox(item, parent)
            
        # store as parent
        parent = name   
        
        # process next
        store(item, tree)

if __name__ == "__main__":
    store(mayaMenu())