import maya.cmds as cmds
from textwrap import dedent

if not cmds.about(batch=True):
    import commandLauncher
    # commandLauncher.clean()
    cmds.evalDeferred(dedent("""
    try:
        commandLauncher.install()
    except:
        import traceback
        traceback.print_exc()
    """))

