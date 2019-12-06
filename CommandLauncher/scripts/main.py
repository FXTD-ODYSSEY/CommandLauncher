import sys

path = r"F:\MayaTecent\CommandLauncher\Reference\CommandSearch\Contents\scripts"

if path not in sys.path:
    sys.path.append(path)

from commandSearch.ui import commands
reload(commands)
from commandSearch.ui import search
reload(search)
from commandSearch.ui import utils
reload(utils)
from commandSearch.ui import results
reload(results)
from commandSearch import ui
reload(ui)
import commandSearch
reload(commandSearch)

commandSearch.setup()