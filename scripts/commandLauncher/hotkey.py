from . import ui

def show():
    """
    Set focus to the input search field of the command search widget. Will
    return early if either the results window or the search bar already
    has focus.
    
    :param SearchWidget commandSearch: decorator handles this argument
    """
    # get COMMAND_LAUNCHER
    COMMAND_LAUNCHER = ui.COMMAND_LAUNCHER
    
    # validate COMMAND_LAUNCHER
    if not COMMAND_LAUNCHER:
        raise ValueError("COMMAND LAUNCHER not exists!")
        
    COMMAND_LAUNCHER.show()