from PyQt5 import uic
from pathlib import Path
from PyQt5 import QtWidgets, QtSql, QtCore


path = Path("venv", "ui", "NakladnayaEditForm.ui")

class NakladnayaEditForm(QtWidgets.QDialog):
    def __init__(self):
        super(NakladnayaEditForm, self).__init__()
        uic.loadUi(path, self)
        self.setWindowModality(2)
