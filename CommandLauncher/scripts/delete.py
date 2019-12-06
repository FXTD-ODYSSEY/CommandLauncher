from commandSearch.ui import search
reload(search)
from commandSearch.ui import utils
reload(utils)

for w in utils.mayaWindow().children():
    if type(w) == search.SearchWidget:
        w.deleteLater()