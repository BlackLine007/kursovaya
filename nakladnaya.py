from pathlib import Path
from PyQt5 import uic
from PyQt5 import QtWidgets, QtSql, QtCore
from datetime import datetime
from PyQt5.QtSql import QSqlDatabase
from PyQt5.QtWidgets import QApplication, QMessageBox
from nakladnaya_edit import NakladnayaEditForm

path = Path("venv", "ui", "NakladnayaForm.ui")

class NakladnayaForm(QtWidgets.QDialog):
    def __init__(self):
        super(NakladnayaForm, self).__init__()
        uic.loadUi(path, self)
        self.setWindowModality(2)
        self.model_nakladnaya_init()
        self.NakladnayaEditForm = None
        self.model_poziciya_init()
        self.ui_init()

    def ui_init(self):
        self.tBPosSave.clicked.connect(self.btnClickSave)
        #описываем что будет по двойному нажатию на tableView Накладная (будет вызываться процедура btnDClickEdit)
        self.tVPos.doubleClicked.connect(self.btnDClickEdit)
        #описываем что будет при нажатии на кнопку Добавить на форме NakladnayaForm
        self.tBPosAdd.clicked.connect(
            self.btnClickAdd)  #при нажатии кнопки добавить будет вызываться процедура btnClickAdd
        self.tBPosDel.clicked.connect(self.btnClickDel)
        self.tVPos.clicked.connect(self.tVPosClick)
        self.lESearchPos.textEdited.connect(self.lESearchPos_textChanged)
        self.lESearchMat.textEdited.connect(self.lESearchMat_textChanged)

        self.tBPozAdd.clicked.connect(self.btnClickPozAdd)
        self.tBPozDel.clicked.connect(self.btnClickPozDel)
        self.tBPozSave.clicked.connect(self.btnClickPozSave)
        self.tBPozRfrsh.clicked.connect(self.btnClickPozRfrsh)
        self.tBPozCancel.clicked.connect(self.btnClickPozCancel)

        self.tVPos.setModel(self.model_nakladnaya)
        self.tVPos.hideColumn(0)  # скрываем столбец id_накладной у таблицы Накладная
        self.tVPos.verticalHeader().setVisible(False)  # скрываем нумерацию строк в tableView
        self.tVPos.setSortingEnabled(True)
        self.tVPos.resizeColumnsToContents()  # подгоняем размеры столбцов
        self.tVPosClick()

        self.tVPoz.setModel(self.model_poziciya)  # связываем модель "Позиция" с соответ. table View
        self.tVPoz.setItemDelegateForColumn(2, QtSql.QSqlRelationalDelegate(
            self.tVPoz))
        self.tVPoz.hideColumn(3)
        self.tVPoz.hideColumn(0)
        self.tVPoz.verticalHeader().setVisible(False)  # скрываем нумерацию строк в tableView
        self.tVPoz.resizeColumnsToContents()
        self.tVPoz.setSortingEnabled(True)

    def model_nakladnaya_init(self):
        self.model_nakladnaya = QtSql.QSqlTableModel(self)  # dataSet, records создание модели
        self.model_nakladnaya.setTable("nakladnaya")
        self.model_nakladnaya.setEditStrategy(QtSql.QSqlTableModel.OnManualSubmit)
        self.model_nakladnaya.select()
        self.model_nakladnaya.setHeaderData(1, QtCore.Qt.Horizontal, "Дата привоза")
        self.model_nakladnaya.setHeaderData(2, QtCore.Qt.Horizontal, "Поставщик")


    def model_poziciya_init(self):
        self.model_poziciya = QtSql.QSqlRelationalTableModel(self)  # dataSet, records создание модели
        self.model_poziciya.setTable("poziciya")
        self.model_poziciya.setEditStrategy(QtSql.QSqlTableModel.OnManualSubmit)
        self.model_poziciya.setRelation(2, QtSql.QSqlRelation("material", "id_materiala",
                                                          "Naimenovanie_mat"))  # устанавливаем связь подчиненной таблицы с главной
        self.model_poziciya.select()
        self.model_poziciya.setHeaderData(1, QtCore.Qt.Horizontal, "Количество пришедшего материала")
        self.model_poziciya.setHeaderData(2, QtCore.Qt.Horizontal, "Наименование материала")
        self.model_poziciya.setHeaderData(3, QtCore.Qt.Horizontal, "id накладной")

    #внимание кнопка не используется, потому что редактирование на форме NakladnayaForm реализовано в режиме формы, а не таблицы!
    def btnClickSave(self):
        # фиксируем все изменения которые сделал пользователь
        if not self.model_nakladnaya.submitAll():  # метод submitAll возвращает true или false
            QMessageBox.critical(self, "Ошибка",
                                 self.model_nakladnaya.lastError().text() + "\nИзменение не было выполнено!",
                                 QMessageBox.Ok)

        # при вызове данной процедуры должна открываться форма редактирования

    def btnDClickEdit(self):
        cur_row = self.tVPos.currentIndex().row()  # index - элемент внутри виджета tableView, вытаскиваем номер строки в tV
        if not self.NakladnayaEditForm:
            self.NakladnayaEditForm = NakladnayaEditForm()

        self.NakladnayaEditForm.dEPrivoz.setDate(self.model_nakladnaya.record(cur_row).value(
            "Data_privoza"))  # вытаскиваем текущее значение поля Дата привоза, чтобы при необходимости его редактировать
        self.NakladnayaEditForm.lEPos.setText(self.model_nakladnaya.record(cur_row).value("Postavshik"))

        # по нажаитию ок после редактирования данных необходимо записать данные в модель и выполнить submit
        if self.NakladnayaEditForm.exec_():
            # первый параметр в setData - это координаты ячейки, второй параметр - значение
            self.model_nakladnaya.setData(self.model_nakladnaya.index(cur_row, 1), self.NakladnayaEditForm.dEPrivoz.date())
            self.model_nakladnaya.setData(self.model_nakladnaya.index(cur_row, 2), self.NakladnayaEditForm.lEPos.text())
            # далее submit
            self.btnClickSave()

    def btnClickAdd(self):
        if not self.NakladnayaEditForm:
            self.NakladnayaEditForm = NakladnayaEditForm()
        self.NakladnayaEditForm.dEPrivoz.setDate(datetime.today())
        self.NakladnayaEditForm.lEPos.clear()


        if self.NakladnayaEditForm.exec_():  # функция при нажатии ок возвращает 1, при нажатии cancel 0
            record = self.model_nakladnaya.record()  #создаем запись структура которой соответствует модели Накладная
            record.remove(record.indexOf("id_nakladnoi")) #удаляем из созданной выше записи первое поле, потому что оно автоинкрементное (иначе будет ошибка)
            #далее в запись надо записать те значения, которые пользователь введет в поля
            record.setValue("Data_privoza", self.NakladnayaEditForm.dEPrivoz.date())
            record.setValue("Postavshik", self.NakladnayaEditForm.lEPos.text())
            self.model_nakladnaya.insertRecord(-1, record)
            self.btnClickSave()

    def btnClickDel(self):
        cur_row = self.tVPos.currentIndex().row()
        # вызываем MessageBox с вопросом для подтверждения удаления
        if QMessageBox.question(self, "Подтвердите удаление",
                                "Вы действительно хотите удалить накладную поставщика " + self.model_nakladnaya.record(cur_row).value(
                                    "Postavshik") + "?",
                                QMessageBox.Cancel, QMessageBox.Ok) == QMessageBox.Ok:
            self.model_nakladnaya.removeRow(cur_row)
        self.btnClickSave()

    def lESearchPos_textChanged(self):
        if self.lESearchPos.text() != "":  # если поле для поиска не пустое, то выполнить поиск
            self.tVPos.selectionModel().clearSelection()  # убираем текущие "выделения" в tV Изделия
            start = self.model_nakladnaya.index(0,
                                              2)
            matches = self.model_nakladnaya.match(  # matches - массив всех символов которые соответствуют поиску
                start,  # стартовый индекс
                QtCore.Qt.DisplayRole,
                self.lESearchPos.text(),  # критерий поиска
                -1,
                QtCore.Qt.MatchContains,  # тип поиска - все индексы которые содержат текст в критерии поиска
            )
            for match in matches:  # проходимся по каждому соответствию и вызываем метод select (т.е. "подсвечиваем" в tV всё что соответствует результатам поиска)
                self.tVPos.selectionModel().select(
                    match,
                    QtCore.QItemSelectionModel.Select
                )

    def lESearchMat_textChanged(self):
        if self.lESearchMat.text() != "":  # если поле для поиска не пустое, то выполнить поиск
            self.tVPoz.selectionModel().clearSelection()  # убираем текущие "выделения" в tV Позиции
            start = self.model_poziciya.index(0, 2)  # стартовый индекс с которого будет выполняться функция match (со значения поля Наименование материала и первой записи в таблице Ингредиенты)
            matches = self.model_poziciya.match(  # matches - массив всех символов которые соответствуют поиску
                start,  # стартовый индекс
                QtCore.Qt.DisplayRole,
                self.lESearchMat.text(),  # критерий поиска
                -1,
                QtCore.Qt.MatchContains,  # тип поиска - все индексы которые содержат текст в критерии поиска
            )
            for match in matches:  # проходимся по каждому соответствию и вызываем метод select (т.е. "подсвечиваем" в tV всё что соответствует результатам поиска)
                self.tVPoz.selectionModel().select(
                    match,
                    QtCore.QItemSelectionModel.Select
                )


    def tVPosClick(self):
        if self.tVPos.selectedIndexes():  # если список выбранных индексов не пустой, то
            cur_row = self.tVPos.currentIndex().row()  # определяем какая строка нажата
            #print(cur_row)
            self.id_nakladnoi = self.model_nakladnaya.record(cur_row).value(
                "id_nakladnoi")  # определяем id_nakladnoi для выбранной строки в таблице "Накладная"
        else:  # иначе если накладная не выбрана
            self.id_nakladnoi = self.model_nakladnaya.record(0).value("id_nakladnoi")
        self.model_poziciya.setFilter(f"id_nakladnoi = {self.id_nakladnoi}") #в таблице ингредиенты оставляем только те записи, у которых id_nakladnoi вычисленный строчкой выше
        self.model_poziciya.select()

    def btnClickPozAdd(self):
        record = self.model_poziciya.record()  # создаем запись структура которой соответствует модели poziciya
        record.setValue("id_nakladnoi", self.id_nakladnoi)
        record.remove(record.indexOf("id_pozicii"))  # удаляем из созданной выше записи первое поле, потому что оно AI
        self.model_poziciya.insertRecord(-1, record)  # добавляем пустую запись в конец таблицы
        index = self.model_poziciya.index(self.model_poziciya.rowCount() - 1, 1)  # передаем фокус в конкретную ячейку (в последней строке, первом столбце) для удобства пользователя (-1, 1 так как перед этим мы добавили запись)
        self.tVPoz.edit(index)  # программно вызываем редактирование ячейки, которую определили сверху

    def btnClickPozDel(self):
        #выбранно ли что-нибудь, есть ли вообще записи?
        if self.tVPoz.selectedIndexes():
            cur_row = self.tVPoz.currentIndex().row()
            # вызываем MessageBox с вопросом для подтверждения удаления
            if QMessageBox.question(self, "Подтвердите удаление",
                                    "Вы действительно хотите удалить выпуск выбранный ингредиент?",
                                    QMessageBox.Cancel, QMessageBox.Ok) == QMessageBox.Ok:
                self.model_poziciya.removeRow(cur_row)
        else:
            QMessageBox.critical(self, "Ошибка", "\nПеред удалением необходимо выбрать строку!",
                                 QMessageBox.Ok)

    def btnClickPozSave(self):
        if not self.model_poziciya.submitAll():
            QMessageBox.critical(self, "Ошибка",
                                 self.model_poziciya.lastError().text() + "\nИзменения не были сохранены!",
                                 QMessageBox.Ok)
        self.model_poziciya.select()

    def btnClickPozRfrsh(self):
        self.model_poziciya.select()  # выбираем то что сейчас находится в базе

    def btnClickPozCancel(self):
        self.model_poziciya.revertAll()  # отменить все изменения (все изменения которые делает пользователь кэширу

