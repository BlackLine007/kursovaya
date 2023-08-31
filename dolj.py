from PyQt5 import uic
from pathlib import Path
from PyQt5 import QtWidgets, QtSql, QtCore
from PyQt5.QtWidgets import QMessageBox
from dolj_edit import DoljEditForm

path = Path("venv", "ui", "DoljForm.ui")


class DoljForm(QtWidgets.QDialog):
    def __init__(self):
        super(DoljForm, self).__init__()
        uic.loadUi(path, self)
        self.setWindowModality(2)
        self.model_dolj_init()
        self.DoljEditForm = None
        self.ui_init()

    def ui_init(self):
        # описываем что будет по двойному нажатию на tableView Должность (будет вызываться процедура btnDClickEdit)
        self.tVDolj.doubleClicked.connect(self.btnDClickEdit)
        # описываем что будет при нажатии на кнопку Добавить на форме DoljForm
        self.pBAdd.clicked.connect(
            self.btnClickAdd)  # при нажатии кнопки добавить будет вызываться процедура btnClickAdd
        self.pBSave.clicked.connect(self.btnClickSave)
        self.pBDel.clicked.connect(self.btnClickDel)
        self.tVDolj.setModel(self.model_dolj)
        self.tVDolj.hideColumn(0) #скрываем столбец id у таблицы Должность
        self.tVDolj.verticalHeader().setVisible(False) #скрываем нумерацию строк в tableView
        self.tVDolj.resizeColumnsToContents()

    def model_dolj_init(self):
        #self.model_dolj = QtSql.QSqlQueryModel(self) #dataSet, records создание модели
        #self.model_dolj.setQuery("select * from doljnost")
        self.model_dolj = QtSql.QSqlTableModel(self)  # dataSet, records создание модели
        self.model_dolj.setTable("doljnost")
        self.model_dolj.setEditStrategy(QtSql.QSqlTableModel.OnManualSubmit)
        self.model_dolj.select()
        self.model_dolj.setHeaderData(1, QtCore.Qt.Horizontal, "Должность")


    def btnClickAdd(self):
        if not self.DoljEditForm:
            self.DoljEditForm = DoljEditForm()
        self.DoljEditForm.lEDolj.clear()

        if self.DoljEditForm.exec_():  # функция при нажатии ок возвращает 1, при нажатии cancel 0
            record = self.model_dolj.record()  #создаем запись структура которой соответствует модели dolj
            #record.remove(0)
            record.remove(record.indexOf("id_doljnosti")) #удаляем из созданной выше записи первое поле, потому что оно автоинкрементное (иначе будет ошибка)
            #далее в запись надо записать те значения, которые пользователь в ведет в поле "наименование должности"
            record.setValue("doljnost", self.DoljEditForm.lEDolj.text())
            self.model_dolj.insertRecord(-1, record)
            if not self.model_dolj.submitAll(): #метод submitAll возвращает true или false
                QMessageBox.critical(self, "Ошибка", self.model_dolj.lastError().text() + "\nЗапись не была добавлена!",
                QMessageBox.ok)


    #при вызове данной процедуры должна открываться форма редактирования
    def btnDClickEdit(self):
        cur_row = self.tVDolj.currentIndex().row() #index - элемент внутри виджета tableView, вытаскиваем номер строки в tV
        if not self.DoljEditForm:
            self.DoljEditForm = DoljEditForm()

        self.DoljEditForm.lEDolj.setText(self.model_dolj.record(cur_row).value("doljnost")) #вытаскиваем текущее значение поля наименование должности, чтобы при необходимости его редактировать

        #по нажаитию ок после редактирования данных необходимо записать данные в модель и выполнить submit
        if self.DoljEditForm.exec_():
            #первый параметр в setData - это координаты ячейки, второй параметр - значение
            self.model_dolj.setData(self.model_dolj.index(cur_row, 1), self.DoljEditForm.lEDolj.text())
            #далее submit
            if not self.model_dolj.submitAll():  # метод submitAll возвращает true или false
                QMessageBox.critical(self, "Ошибка", self.model_dolj.lastError().text() + "\nЗапись не была изменена!",
                                     QMessageBox.ok)

    #внимание кнопка не используется, потому что редактирование на форме DoljForm реализовано в режиме формы, а не таблицы!
    def btnClickSave(self):
        #фиксируем все изменения которые сделал пользователь
        if not self.model_dolj.submitAll():  # метод submitAll возвращает true или false
            QMessageBox.critical(self, "Ошибка", self.model_dolj.lastError().text() + "\nСохранение не выполнено!",
                                 QMessageBox.ok)

    def btnClickDel(self):
        cur_row = self.tVDolj.currentIndex().row()
        #вызываем MessageBox с вопросом для подтверждения удаления
        if QMessageBox.question(self, "Подтвердите удаление",
            "Вы действительно хотите удалить должность "+self.model_dolj.record(cur_row).value("doljnost")+"?",
                                QMessageBox.Cancel, QMessageBox.Ok) == QMessageBox.Ok:
            self.model_dolj.removeRow(cur_row)
        if not self.model_dolj.submitAll():  # метод submitAll возвращает true или false
            QMessageBox.critical(self, "Ошибка", self.model_dolj.lastError().text() + "\nУдаление не выполнено!",
                                 QMessageBox.ok)


