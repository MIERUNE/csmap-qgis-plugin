import sys
import os

# to import modules as non-relative
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), "csmap_py"))


def classFactory(iface):
    from qcsmap import QCsMap

    return QCsMap(iface)
