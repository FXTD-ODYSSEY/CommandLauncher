from Qt.QtCore import QThreadPool,QRunnable
from Qt.QtWidgets import QWidgetAction,QMenu,QMainWindow,QMenuBar
from Qt.QtCompat import wrapInstance
from maya import OpenMayaUI
import time

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

def showMenu(parent=None):
    """
    Recursive show menu so that we can get menu item in multirheading
    """
    parent = parent if parent else mayaMenu()
    for item in parent.children():
        # skip if no item name
        if not item.objectName():
            continue

        # process menu
        if type(item) == QMenu:
            item.aboutToShow.emit()
            
        # process next
        showMenu(item)

def getMenu(menu):
    """
    Get the name of the QMenu parsed.
    
    :param QMenu menu:
    :return: Menu name
    :rtype: str
    """
    name = menu.title().encode("utf-8")
    menu.aboutToShow.emit()
    return name

if __name__ == "__main__":
    curr =  time.time()
    showMenu()
    # _store(mayaMenu())
    print time.time() - curr


# class Worker(QRunnable):

#     def __init__(self,func,curr):
#         super(Worker,self).__init__()
#         self.func = func
#         self.curr = curr
#     def run(self):
#         '''
#         Initialise the runner function with passed args, kwargs.
#         '''
#         self.func()

#         print "mutlithread complete : ", time.time() - self.curr

# if __name__ == "__main__":
    
#     curr = time.time()
#     thread = QThreadPool()
#     thread.start(Worker(lambda:_store(mayaMenu()),curr))

