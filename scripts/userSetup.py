import maya.cmds as cmds
from textwrap import dedent

if not cmds.about(batch=True):
    cmds.evalDeferred(dedent("""
    import commandLauncher
    try:
        commandLauncher.install()
    except:
        import traceback
        traceback.print_exc()
    """))

