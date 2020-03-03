import maya.cmds as cmds
import commandLauncher

if not cmds.about(batch=True):
    # commandLauncher.clean()
    cmds.evalDeferred(commandLauncher.setup)

