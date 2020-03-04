import maya.cmds as cmds

if not cmds.about(batch=True):
    import commandLauncher
    # commandLauncher.clean()
    cmds.evalDeferred(commandLauncher.install)

