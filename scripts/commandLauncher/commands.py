# coding:utf-8

__author__ =  'timmyliang'
__email__ =  '820472580@qq.com'
__date__ = '2019-12-07 14:33:16'


import re
import os
import sys
import json
import inspect
import difflib
from functools import partial
from importlib import import_module

from .ui import utils
from .ui.setting import SETTING_PATH

from maya import cmds
from maya import mel

global COMMANDS
COMMANDS = {}

def get():
    """
    Get all registered commands from the global variable, if the global 
    variable cannot be found an empty dictionary will be returned.
    
    :return: Commands data
    :rtype: dict
    """
    if not "COMMANDS" in globals().keys():
        return {}
    return globals().get("COMMANDS")

    
# ----------------------------------------------------------------------------

def filter(search):
    """
    The search string is processed find matches within the commands variable.
    
    :param str search: search string to match with commands
    :return: Matching commands
    :rtype: list
    """
    matches = []
    regexes = []

    # generate regex
    if not search:
        return []

    # NOTE split 实现空格关键词切分
    for p in search.split():

        regexes.append(
            re.compile(
                r'.*' + 
                p + 
                r'.*'
            )    
        )

    # filter commands
    for k, v in COMMANDS.iteritems():
        if v.get("pin"):
            matches.append(v)
            continue
            
        states = []
        for regex in regexes:
            states.append( 
                re.match(
                    regex.pattern, 
                    v.get("search"), 
                    re.I
                )
            )
            
        if regexes and None not in states:
            matches.append(v)

    # matches.sort(key=lambda x:(-x["pin"], x["hierarchy"]))
    # NOTE https://github.com/csaez/quicklauncher/issues/12
    # NOTE 排序最匹配的结果放到最上面
    ratio = lambda x, y: difflib.SequenceMatcher(None, x, y).ratio()
    matches.sort(key=lambda x: (x["pin"],ratio(x["name"], search)),reverse=True)
    return matches

# ----------------------------------------------------------------------------  

def store():  
    """
    Process Maya's menubar to see if any if its children meet the search 
    command requirements. If so, the button and commands will be added 
    to the commands variable.
    """
    # reset commands
    global COMMANDS
    COMMANDS = {}

    import threading

    # loop menu bar
    _store(utils.mayaMenu())
    getShelfButton()
    getCmdsMember()
    getScripts()

    print "Command Launcher Item Updated "
    
def _store(parent, parents=[], menu_list=[]):
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
            )
            menu_list.append(item)
        # process item
        elif type(item) == utils.QWidgetAction:  
            # get dynamic p
            dynamic = item.dynamicPropertyNames()
            
            if not "isOptionBox" in dynamic:
                # main item
                getItem(item, name, tree , menu_list)
            else:
                # option box item
                getItemOptionBox(item, parent)
            
        # store as parent
        parent = name   
        
        # process next
        _store(item, tree , menu_list)
    
    return menu_list
# ----------------------------------------------------------------------------  
          
def showMenu(parent=None):
    """
    Recursive show menu so that we can get menu item in multirheading
    """
    parent = parent if parent else utils.mayaMenu()
    for item in parent.children():
        # skip if no item name
        if not item.objectName():
            continue

        # process menu
        if type(item) == utils.QMenu:
            item.aboutToShow.emit()
            
        # process next
        showMenu(item)

# ----------------------------------------------------------------------------
    
def getItem(item, name, parents , menu_list):
    """
    Get data from item and store it into COMMANDS variable.
    
    :param QWidgetAction item:
    :param str name: 
    :param list parents: List f all parents, used for hierarchy
    """

    # get name
    text = item.text().encode("utf-8")
    if not name or item.isSeparator() or item.menu():  
        return
    
    # add last parent
    parents.append(text)
        
    # get icon
    icon = cmds.menuItem(utils.qtToMaya(item), query=True, image=True)
      
    # store commands      
    COMMANDS[name] = dict( )
    COMMANDS[name]["name"] = text
    COMMANDS[name]["pin"] = False
    COMMANDS[name]["cmd"] = item 
    COMMANDS[name]["icon"] = utils.QIcon( ":/{0}".format(icon))
    COMMANDS[name]["group"] = parents[0]
    COMMANDS[name]["search"] = "".join([p.lower() for p in parents]) 
    COMMANDS[name]["hierarchy"] = " > ".join(parents)
    COMMANDS[name]["menu"] = menu_list[-1]
    COMMANDS[name]["category"] = "menu"
      
def getItemOptionBox(item, name):
    """
    Get data from option item and store it into COMMANDS variable.
    
    :param QWidgetAction item:
    :param str name: 
    """
    if not name in COMMANDS.keys():
        return

    COMMANDS[name]["cmdOption"]   = item

def getCmdsMember():
    from types import BuiltinFunctionType

    for (name, func) in inspect.getmembers(cmds, callable):
        COMMANDS[name] = dict()
        COMMANDS[name]["name"] = name
        COMMANDS[name]["pin"] = False
        COMMANDS[name]["icon"] = utils.QIcon()
        COMMANDS[name]["search"] = name
        COMMANDS[name]["hierarchy"] = name
        COMMANDS[name]["cmd"]  = func

        # NOTE BuiltinFunction 为 cmds 的命令 | 其他的是 runtime Command 或者 一些插件引入的命令
        if type(func) == BuiltinFunctionType:
            COMMANDS[name]["group"] = "Maya cmds Module" 
            COMMANDS[name]["category"] = "cmds"
        else:
            COMMANDS[name]["group"] = "Maya Command" 
            COMMANDS[name]["category"] = "command"

# ----------------------------------------------------------------------------

def loadShelf(index):
    """loadShelf 
    
    convert shelf.mel loadShelf global proc to python code
    
    Parameters
    ----------
    index : int
        the loading shelf index
    """
    
    varName="shelfName" + str(index)
    shelfName=str(cmds.optionVar(q=varName))
    if cmds.shelfLayout(shelfName, exists=1) and cmds.shelfLayout(shelfName, query=1, numberOfChildren=1) == 0:
        shelfFileNum="shelfFile" + str(index)
        shelfFile=cmds.optionVar(q=shelfFileNum)
        if shelfFile and mel.eval("exists %s"%shelfFile):
            cmds.setParent(shelfName)
            shelfVersion=""
            try:
                shelfVersion = mel.eval("eval %s"%shelfFile)
            except:
                print "eval %s fail" % shelfFile
                import traceback
                traceback.print_exc()
                return False
                
            cmds.optionVar(intValue=(("shelfLoad" + str(index)), True))
            if shelfVersion:
                cmds.optionVar(stringValue=(("shelfVersion" + str(index)), shelfVersion))
                if cmds.shelfLayout(shelfName, exists=1):
                    cmds.shelfLayout(shelfName, edit=1, version=shelfVersion)

    return True    
      
def loadShelves():
    gShelfTopLevel = mel.eval("$temp = $gShelfTopLevel")
    shelves = cmds.shelfTabLayout(gShelfTopLevel,query=1,ca=1)
    for i,_ in enumerate(shelves,1):
        loadShelf(i)

def getShelfButton():
    """getShelfButton 
    
    Get Command data from Maya Shelf
    """
    # NOTE 获取工具架名称
    gShelfTopLevel = mel.eval("$temp = $gShelfTopLevel")
    shelves = cmds.shelfTabLayout(gShelfTopLevel,query=1,ca=1)
    labels = cmds.shelfTabLayout(gShelfTopLevel,query=1,tl=1)
    for i,[shelf,label] in enumerate(zip(shelves,labels),1):
        # NOTE 获取完整组件名称
        shelf = cmds.shelfLayout(shelf,query=1,fpn=1)
        if not cmds.shelfLayout(shelf,query=1,ca=1):
            print "%s empty child" % shelf
            continue
        for btn in cmds.shelfLayout(shelf,query=1,ca=1):
            if cmds.shelfButton(btn,query=1,ex=1):
                name = cmds.shelfButton(btn,query=1,label=1)
                icon = cmds.shelfButton(btn,query=1,i=1)
                # tooltip = cmds.shelfButton(btn,query=1,ann=1)
                
                COMMANDS[name] = dict()
                COMMANDS[name]["name"] = name
                COMMANDS[name]["pin"] = False
                if os.path.exists(icon):
                    COMMANDS[name]["icon"] = utils.QIcon(icon)
                else:
                    COMMANDS[name]["icon"] = utils.QIcon( ":/{0}".format(icon))
                COMMANDS[name]["group"] = "Shelf: %s" % label
                COMMANDS[name]["search"] = "%s%s"%(label,name)
                COMMANDS[name]["hierarchy"] = "%s > %s"%(label,name)
                COMMANDS[name]["category"] = "shelf"
                # COMMANDS[name]["menu"] = menu_list[-1]
                
                # NOTE 点击运行的代码
                command = cmds.shelfButton(btn,query=1,c=1)
                command_type = cmds.shelfButton(btn,query=1,c=1,stp=1)
                if command_type.lower() == "mel":
                    # Note 运行双击的 mel 代码
                    COMMANDS[name]["cmd"]  = partial(mel.eval,command)
                else:
                    # Note 运行双击的 python 代码
                    COMMANDS[name]["cmd"]  = partial(lambda command:eval(compile(command, '<string>', 'exec')),command)

                
                # NOTE 查询双击 shelf 状态
                options = cmds.shelfButton(btn,query=1,dcc=1)
                if options:
                    options_type = cmds.shelfButton(btn,query=1,dcc=1,stp=1)
                    if options_type.lower() == "mel":
                        # Note 运行双击的 mel 代码
                        COMMANDS[name]["cmdOption"]  = partial(mel.eval,options)
                    else:
                        # Note 运行双击的 python 代码
                        COMMANDS[name]["cmdOption"]  = partial(lambda x:eval(compile(x, '<string>', 'exec')),options)

# ----------------------------------------------------------------------------


def getRepo():
    if not os.path.exists(SETTING_PATH):
        path = os.path.join(os.path.dirname(cmds.about(env=1)),"scripts")
        return [path] if os.path.exists(path) else []

    with open(SETTING_PATH,'r') as f:
        data = json.load(f,encoding="utf-8")
    return [path for path,state in data["path"].iteritems() if state and os.path.exists(path)]

def runPyScript(script_path):
    # add to pythonpath and execute
    sys.path.insert(0, os.path.dirname(script_path))
    module_name = os.path.split(script_path)[-1].replace(".py", "")
    import_module(module_name)
    # cleanup
    del sys.modules[module_name]
    sys.path = sys.path[1:]
    
def runMelScript(script_path):
    with open(script_path,'r') as f:
        mel.eval(f.read())

def getScripts():  
    for repo in getRepo():
        for (path, _, files) in os.walk(repo):
            for f in files:
                py_check = f.lower().endswith(".py")
                mel_check = f.lower().endswith(".mel")
                if not py_check and not mel_check:
                    continue

                file_path = os.path.realpath(os.path.join(path, f))
                name = os.path.splitext(f)[0]
                COMMANDS[file_path] = dict()
                COMMANDS[file_path]["name"] = name
                COMMANDS[file_path]["pin"] = False
                COMMANDS[file_path]["group"] = "Scripts Files" 
                COMMANDS[file_path]["search"] = file_path
                COMMANDS[file_path]["hierarchy"] = file_path
                COMMANDS[file_path]["category"] = "script"

                if py_check:
                    COMMANDS[file_path]["icon"] = utils.QIcon(":/pythonFamily.png")
                    COMMANDS[file_path]["cmd"] = partial(runPyScript,file_path) 
                elif mel_check:
                    COMMANDS[file_path]["icon"] = utils.QIcon(":/commandButton.png")
                    COMMANDS[file_path]["cmd"] = partial(runMelScript,file_path) 
