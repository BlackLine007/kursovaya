from PyQt5 import uic
from pathlib import Path
from PyQt5 import QtWidgets, QtSql, QtCore
from PyQt5.QtWidgets import QMessageBox
from materials_edit import MaterialsEditForm

path = Path("venv", "ui", "MaterialsForm.ui")

class MaterialsForm(QtWidgets.QDialog):
    def __init__(self):
        super(MaterialsForm, self).__init__()
        uic.loadUi(path, self)
        self.setWindowModality(2)
        self.model_materials_init()
        self.MaterialsEditForm = None
        self.ui_init()

    def ui_init(self):
        self.tVMaterials.doubleClicked.connect(self.btnDClickEdit)
        # описываем что будет при нажатии на кнопку Добавить на форме MaterialsForm
        self.pBMatAdd.clicked.connect(
            self.btnClickAdd)  # при нажатии кнопки добавить будет вызываться процедура btnClickAdd
        self.pBMatSave.clicked.connect(self.btnClickSave)
        self.pBMatDel.clicked.connect(self.btnClickDel)
        self.tVMaterials.setModel(self.model_materials)
        self.tVMaterials.hideColumn(0)  # скрываем столбец id у таблицы Должность
        self.tVMaterials.verticalHeader().setVisible(False)  # скрываем нумерацию строк в tableView
        self.tVMaterials.resizeColumnsToContents()

    def model_materials_init(self):
        self.model_materials = QtSql.QSqlTableModel(self)  # dataSet, records создание модели
        self.model_materials.setTable("material")
        self.model_materials.setEditStrategy(QtSql.QSqlTableModel.OnManualSubmit)
        self.model_materials.select()
        self.model_materials.setHeaderData(1, QtCore.Qt.Horizontal, "Наименование материала")
        self.model_materials.setHeaderData(2, QtCore.Qt.Horizontal, "Единица измерения")

    def btnClickAdd(self):
        if not self.MaterialsEditForm:
            self.MaterialsEditForm = MaterialsEditForm()
        self.MaterialsEditForm.lENaimMat.clear()
        self.MaterialsEditForm.lEEdIzm.clear()

        if self.MaterialsEditForm.exec_():  # функция при нажатии ок возвращает 1, при нажатии cancel 0
            record = self.model_materials.record()  # создаем запись структура которой соответствует модели materials
            record.remove(record.indexOf(
                "id_materiala"))  # удаляем из созданной выше записи первое поле, потому что оно автоинкрементное (иначе будет ошибка)
            # далее в запись надо записать те значения, которые пользователь в ведет в поле "наименование должности"
            record.setValue("Naimenovanie_mat", self.MaterialsEditForm.lENaimMat.text())
            record.setValue("Ed_izm", self.MaterialsEditForm.lEEdIzm.text())
            self.model_materials.insertRecord(-1, record)
            self.btnClickSave()

    # при вызове данной процедуры должна открываться форма редактирования
    def btnDClickEdit(self):
        cur_row = self.tVMaterials.currentIndex().row()  # index - элемент внутри виджета tableView, вытаскиваем номер строки в tV
        if not self.DoljEditForm:
            self.MaterialsEditForm = MaterialsEditForm()

        self.MaterialsEditForm.lENaimMat.setText(self.model_materials.record(cur_row).value(
            "Naimenovanie_mat"))  # вытаскиваем текущее значение поля наименование материала, чтобы при необходимости его редактировать
        self.MaterialsEditForm.lEEdIzm.setText(self.model_materials.record(cur_row).value(
            "Ed_izm"))

        # по нажаитию ок после редактирования данных необходимо записать данные в модель и выполнить submit
        if self.MaterialsEditForm.exec_():
            # первый параметр в setData - это координаты ячейки, второй параметр - значение
            self.model_materials.setData(self.model_materials.index(cur_row, 1), self.MaterialsEditForm.lENaimMat.text())
            self.model_materials.setData(self.model_materials.index(cur_row, 2),
                                         self.MaterialsEditForm.lEEdIzm.text())
            # далее submit
            self.btnClickSave()

    # внимание кнопка не используется, потому что редактирование на форме DoljForm реализовано в режиме формы, а не таблицы!
    def btnClickSave(self):
        # фиксируем все изменения которые сделал пользователь
        if not self.model_materials.submitAll():  # метод submitAll возвращает true или false
            QMessageBox.critical(self, "Ошибка", self.model_materials.lastError().text() + "\nСохранение не выполнено!",
                                 QMessageBox.Ok)

    def btnClickDel(self):
        cur_row = self.tVMaterials.currentIndex().row()
        # вызываем MessageBox с вопросом для подтверждения удаления
        if QMessageBox.question(self, "Подтвердите удаление",
                                "Вы действительно хотите удалить выбранный материал " + self.model_materials.record(cur_row).value(
                                    "Naimenovanie_mat") + "?",
                                QMessageBox.Cancel, QMessageBox.Ok) == QMessageBox.Ok:
            self.model_materials.removeRow(cur_row)
        self.btnClickSave()