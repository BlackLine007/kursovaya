from pathlib import Path
from PyQt5 import uic
from PyQt5 import QtWidgets, QtSql, QtCore
from PyQt5.QtWidgets import QApplication, QMessageBox
from izdeliya_edit import IzdeliyaEditForm

path = Path("venv", "ui", "IzdeliyaForm.ui")

class IzdeliyaForm(QtWidgets.QDialog):
    def __init__(self):
        super(IzdeliyaForm, self).__init__()
        uic.loadUi(path, self)
        self.setWindowModality(2)
        self.model_izdeliya_init()
        self.IzdeliyaEditForm = None
        self.model_ingredients_init()
        self.ui_init()


    def ui_init(self):
        self.tBIzdelSave.clicked.connect(self.btnClickSave)
        # описываем что будет по двойному нажатию на tableView Изделия (будет вызываться процедура btnDClickEdit)
        self.tVIzdel.doubleClicked.connect(self.btnDClickEdit)
        # описываем что будет при нажатии на кнопку Добавить на форме IzdeliyaForm
        self.tBIzdelAdd.clicked.connect(
            self.btnClickAdd)  # при нажатии кнопки добавить будет вызываться процедура btnClickAdd
        self.tBIzdelDel.clicked.connect(self.btnClickDel)
        self.tVIzdel.clicked.connect(self.tVIzdelClick)
        self.lESearchIzdel.textEdited.connect(self.lESearchIzdel_textChanged)
        self.lESearchMat.textEdited.connect(self.lESearchMat_textChanged)

        self.tBIngredAdd.clicked.connect(self.btnClickIngredAdd)
        self.tBIngredDel.clicked.connect(self.btnClickIngredDel)
        self.tBIngredSave.clicked.connect(self.btnClickIngredSave)
        self.tBIngredRfrsh.clicked.connect(self.btnClickIngredRfrsh)
        self.tBIngredCancel.clicked.connect(self.btnClickIngredCancel)


        self.tVIzdel.setModel(self.model_izdeliya)
        self.tVIzdel.hideColumn(0) #скрываем столбец id_изделия у таблицы Изделия
        self.tVIzdel.verticalHeader().setVisible(False) #скрываем нумерацию строк в tableView
        self.tVIzdel.setSortingEnabled(True)
        self.tVIzdel.resizeColumnsToContents() #подгоняем размеры столбцов
        self.tVIzdelClick()

        self.tVIngred.setModel(self.model_ingredients)  # связываем модель "Ингредиенты" с соответ. table View
        self.tVIngred.setItemDelegateForColumn(3, QtSql.QSqlRelationalDelegate(
            self.tVIngred))  # выпадающий список для поля изделие в таблице "Выпуск товара"
        self.tVIngred.hideColumn(2)  # скрываем столбец id изделия
        self.tVIngred.hideColumn(0)  # скрываем столбец id_ингредиента в таблице Ингредиенты
        self.tVIngred.verticalHeader().setVisible(False)  # скрываем нумерацию строк в tableView
        self.tVIngred.resizeColumnsToContents()
        self.tVIngred.setSortingEnabled(True)

    def model_izdeliya_init(self):
        self.model_izdeliya = QtSql.QSqlTableModel(self)  # dataSet, records создание модели
        self.model_izdeliya.setTable("izdeliya")
        self.model_izdeliya.setEditStrategy(QtSql.QSqlTableModel.OnManualSubmit)
        self.model_izdeliya.select()
        self.model_izdeliya.setHeaderData(1, QtCore.Qt.Horizontal, "Наименование изделия")
        self.model_izdeliya.setHeaderData(2, QtCore.Qt.Horizontal, "Цена изделия")
        self.model_izdeliya.setHeaderData(3, QtCore.Qt.Horizontal, "Вес")

    def model_ingredients_init(self):
        self.model_ingredients = QtSql.QSqlRelationalTableModel(self)  # dataSet, records создание модели
        self.model_ingredients.setTable("ingredients")
        self.model_ingredients.setEditStrategy(QtSql.QSqlTableModel.OnManualSubmit)
        self.model_ingredients.setRelation(3, QtSql.QSqlRelation("material", "id_materiala",
                                                          "Naimenovanie_mat"))  # устанавливаем связь подчиненной таблицы с главной
        self.model_ingredients.select()
        self.model_ingredients.setHeaderData(1, QtCore.Qt.Horizontal, "Количество игредиента")
        self.model_ingredients.setHeaderData(2, QtCore.Qt.Horizontal, "Id_изделия")
        self.model_ingredients.setHeaderData(3, QtCore.Qt.Horizontal, "Наименование материала")

    def btnClickAdd(self):
        if not self.IzdeliyaEditForm:
            self.IzdeliyaEditForm = IzdeliyaEditForm()
        self.IzdeliyaEditForm.lENaim.clear()
        self.IzdeliyaEditForm.dSBStoim.clear()
        self.IzdeliyaEditForm.dSBVes.clear()

        if self.IzdeliyaEditForm.exec_():  # функция при нажатии ок возвращает 1, при нажатии cancel 0
            record = self.model_izdeliya.record()  #создаем запись структура которой соответствует модели izdeliya
            record.remove(record.indexOf("id_izdeliya")) #удаляем из созданной выше записи первое поле, потому что оно автоинкрементное (иначе будет ошибка)
            #далее в запись надо записать те значения, которые пользователь введет в поля
            record.setValue("Naimen_izdeliya", self.IzdeliyaEditForm.lENaim.text())
            record.setValue("Cena_izdeliya", self.IzdeliyaEditForm.dSBStoim.value())
            record.setValue("Ves", self.IzdeliyaEditForm.dSBVes.value())
            self.model_izdeliya.insertRecord(-1, record)
            self.btnClickSave()

    #при вызове данной процедуры должна открываться форма редактирования
    def btnDClickEdit(self):
        cur_row = self.tVIzdel.currentIndex().row() #index - элемент внутри виджета tableView, вытаскиваем номер строки в tV
        if not self.IzdeliyaEditForm:
            self.IzdeliyaEditForm = IzdeliyaEditForm()

        self.IzdeliyaEditForm.lENaim.setText(self.model_izdeliya.record(cur_row).value("Naimen_izdeliya")) #вытаскиваем текущее значение поля наименования изделия, чтобы при необходимости его редактировать
        self.IzdeliyaEditForm.dSBStoim.setValue(self.model_izdeliya.record(cur_row).value("Cena_izdeliya"))
        self.IzdeliyaEditForm.dSBVes.setValue(self.model_izdeliya.record(cur_row).value("Ves"))

        #по нажаитию ок после редактирования данных необходимо записать данные в модель и выполнить submit
        if self.IzdeliyaEditForm.exec_():
            #первый параметр в setData - это координаты ячейки, второй параметр - значение
            self.model_izdeliya.setData(self.model_izdeliya.index(cur_row, 1), self.IzdeliyaEditForm.lENaim.text())
            self.model_izdeliya.setData(self.model_izdeliya.index(cur_row, 2), self.IzdeliyaEditForm.dSBStoim.value())
            self.model_izdeliya.setData(self.model_izdeliya.index(cur_row, 3), self.IzdeliyaEditForm.dSBVes.value())
            #далее submit
            self.btnClickSave()

        #внимание кнопка не используется, потому что редактирование на форме IzdeliyaForm реализовано в режиме формы, а не таблицы!
    def btnClickSave(self):
        #фиксируем все изменения которые сделал пользователь
        if not self.model_izdeliya.submitAll():  # метод submitAll возвращает true или false
            QMessageBox.critical(self, "Ошибка", self.model_izdeliya.lastError().text() + "\nИзменение не было выполнено!",
                                 QMessageBox.Ok)

    def btnClickDel(self):
        cur_row = self.tVIzdel.currentIndex().row()
        # вызываем MessageBox с вопросом для подтверждения удаления
        if QMessageBox.question(self, "Подтвердите удаление",
                                "Вы действительно хотите удалить изделие " + self.model_izdeliya.record(cur_row).value(
                                    "Naimen_izdeliya") + "?",
                                QMessageBox.Cancel, QMessageBox.Ok) == QMessageBox.Ok:
            self.model_izdeliya.removeRow(cur_row)
        self.btnClickSave()

    def tVIzdelClick(self):
        if self.tVIzdel.selectedIndexes():  # если список выбранных индексов не пустой, то
            cur_row = self.tVIzdel.currentIndex().row()  # определяем какая строка нажата
            #print(cur_row)
            self.id_izdeliya = self.model_izdeliya.record(cur_row).value(
                "id_izdeliya")  # определяем id_izdeliya для выбранной строки в таблице "Изделия"
        else:  # иначе если сотрудник не выбран
            self.id_izdeliya = self.model_izdeliya.record(0).value("id_izdeliya")
        self.model_ingredients.setFilter(f"id_izdeliya = {self.id_izdeliya}") #в таблице ингредиенты оставляем только те записи, у которых id_izdeliya вычисленный строчкой выше
        self.model_ingredients.select()


    def btnClickIngredAdd(self):
        record = self.model_ingredients.record()  # создаем запись структура которой соответствует модели ingredients
        record.setValue("id_izdeliya", self.id_izdeliya)
        record.remove(record.indexOf("id_ingredienta"))  # удаляем из созданной выше записи первое поле, потому что оно AI
        self.model_ingredients.insertRecord(-1, record)  # добавляем пустую запись в конец таблицы
        index = self.model_ingredients.index(self.model_ingredients.rowCount() - 1, 1)  # передаем фокус в конкретную ячейку (в последней строке, первом столбце) для удобства пользователя (-1, 1 так как перед этим мы добавили запись)
        self.tVIngred.edit(index)  # программно вызываем редактирование ячейки, которую определили сверху

    def btnClickIngredDel(self):
        #выбранно ли что-нибудь, есть ли вообще записи?
        if self.tVIngred.selectedIndexes():
            cur_row = self.tVIngred.currentIndex().row()
            # вызываем MessageBox с вопросом для подтверждения удаления
            if QMessageBox.question(self, "Подтвердите удаление",
                                    "Вы действительно хотите удалить выпуск выбранный ингредиент?",
                                    QMessageBox.Cancel, QMessageBox.Ok) == QMessageBox.Ok:
                self.model_ingredients.removeRow(cur_row)
        else:
            QMessageBox.critical(self, "Ошибка", "\nПеред удалением необходимо выбрать строку!",
                                 QMessageBox.Ok)

    def btnClickIngredSave(self):
        if not self.model_ingredients.submitAll():
            QMessageBox.critical(self, "Ошибка",
                                 self.model_ingredients.lastError().text() + "\nИзменения не были сохранены!",
                                 QMessageBox.Ok)
        self.model_ingredients.select()

    def btnClickIngredRfrsh(self):
        self.model_ingredients.select()  # выбираем то что сейчас находится в базе

    def btnClickIngredCancel(self):
        self.model_ingredients.revertAll()  # отменить все изменения (все изменения которые делает пользователь кэшируются в буфер и хранятся до тех пор пока не будет вызван метод submit)


    def lESearchIzdel_textChanged(self):
        if self.lESearchIzdel.text() != "": #если поле для поиска не пустое, то выполнить поиск
            self.tVIzdel.selectionModel().clearSelection() #убираем текущие "выделения" в tV Изделия
            start = self.model_izdeliya.index(0, 1) #стартовый индекс с которого будет выполняться функция match (со значения поля Наименование первой записи в таблице Изделия)
            matches = self.model_izdeliya.match( #matches - массив всех символов которые соответствуют поиску
                start, #стартовый индекс
                QtCore.Qt.DisplayRole,
                self.lESearchIzdel.text(), #критерий поиска
                -1,
                QtCore.Qt.MatchContains, #тип поиска - все индексы которые содержат текст в критерии поиска
            )
            for match in matches: #проходимся по каждому соответствию и вызываем метод select (т.е. "подсвечиваем" в tV всё что соответствует результатам поиска)
                self.tVIzdel.selectionModel().select(
                    match,
                    QtCore.QItemSelectionModel.Select
                )

    def lESearchMat_textChanged(self):
        if self.lESearchMat.text() != "":  # если поле для поиска не пустое, то выполнить поиск
            self.tVIngred.selectionModel().clearSelection()  # убираем текущие "выделения" в tV Изделия
            start = self.model_ingredients.index(0, 3)  # стартовый индекс с которого будет выполняться функция match (со значения поля Наименование материала первой записи в таблице Ингредиенты)
            matches = self.model_ingredients.match(  # matches - массив всех символов которые соответствуют поиску
                start,  # стартовый индекс
                QtCore.Qt.DisplayRole,
                self.lESearchMat.text(),  # критерий поиска
                -1,
                QtCore.Qt.MatchContains,  # тип поиска - все индексы которые содержат текст в критерии поиска
            )
            for match in matches:  # проходимся по каждому соответствию и вызываем метод select (т.е. "подсвечиваем" в tV всё что соответствует результатам поиска)
                self.tVIngred.selectionModel().select(
                    match,
                    QtCore.QItemSelectionModel.Select
                )




