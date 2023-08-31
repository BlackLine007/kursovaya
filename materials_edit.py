from PyQt5 import uic
from pathlib import Path
from PyQt5 import QtWidgets, QtSql, QtCore


path = Path("venv", "ui", "MaterialsEditForm.ui")

class MaterialsEditForm(QtWidgets.QDialog):
    def __init__(self):
        super(MaterialsEditForm, self).__init__()
        uic.loadUi(path, self)
        self.setWindowModality(2)
