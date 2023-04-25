from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
import os


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class TextToBinWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.coding = 'cp1251'
        self.parent = parent

        exit_action = QtWidgets.QAction(QIcon(resource_path('exit.png')), '&Выйти', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Закрыть приложение')
        exit_action.triggered.connect(QtWidgets.qApp.quit)

        clear_action = QtWidgets.QAction(QIcon(resource_path('minus.png')), '&Очистить', self)
        clear_action.triggered.connect(self.clear)

        show_help = QtWidgets.QAction(QIcon(), '&Справка', self)
        show_help.setShortcut('Ctrl+H')
        show_help.setStatusTip('Открыть справку')
        show_help.triggered.connect(self.show_dialog_help)

        open_act = QtWidgets.QAction(QIcon(), '&TextToBin', self)
        open_act.setStatusTip('Открыть справку')
        open_act.triggered.connect(self.parent.show)

        utf8 = QtWidgets.QAction('UTF-8', self)
        cp1251 = QtWidgets.QAction('windows-1251', self)
        utf8.setCheckable(True)
        cp1251.setCheckable(True)
        cp1251.setChecked(True)

        self.menu_bar = QtWidgets.QMenuBar()
        file_menu = self.menu_bar.addMenu('&Файл')
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        opt_menu = self.menu_bar.addMenu('&TextToBin')
        self.coding_menu = opt_menu.addMenu('Кодировка')
        self.coding_menu.addAction(utf8)
        self.coding_menu.addAction(cp1251)
        opt_menu.addSeparator()
        opt_menu.addAction(open_act)
        self.menu_bar.addAction(show_help)

        coding_group = QtWidgets.QActionGroup(self)
        coding_group.addAction(utf8)
        coding_group.addAction(cp1251)

        utf8.triggered.connect(lambda: self.set_coding('utf-8'))
        cp1251.triggered.connect(lambda: self.set_coding('cp1251'))

        self.text_edit = QtWidgets.QTextEdit(self)
        self.text_edit.textChanged.connect(self.str_to_bytes)
        self.hex_text_edit = QtWidgets.QTextEdit()
        self.hex_text_edit.textChanged.connect(self.bytes_to_str)

        self.v_box = QtWidgets.QVBoxLayout()
        self.top_h_box = QtWidgets.QHBoxLayout()
        self.l_label = QtWidgets.QLabel('<center>Text</center>')
        self.r_label = QtWidgets.QLabel('<center>Bin</center>')
        self.top_h_box.addWidget(self.l_label)
        self.top_h_box.addWidget(self.r_label)
        self.text_h_box = QtWidgets.QHBoxLayout()
        self.text_h_box.addWidget(self.text_edit)
        self.text_h_box.addWidget(self.hex_text_edit)

        '''self.copy_h_box = QtWidgets.QHBoxLayout()
        self.paste_h_box = QtWidgets.QHBoxLayout()

        self.l_copy_btn = QtWidgets.QPushButton()
        self.r_copy_btn = QtWidgets.QPushButton()
        self.l_paste_btn = QtWidgets.QPushButton()
        self.r_paste_btn = QtWidgets.QPushButton()

        self.copy_h_box.addWidget(self.l_copy_btn)
        self.copy_h_box.addWidget(self.r_copy_btn)
        self.paste_h_box.addWidget(self.l_paste_btn)
        self.paste_h_box.addWidget(self.r_paste_btn)'''

        self.v_box.addLayout(self.top_h_box)
        self.v_box.addLayout(self.text_h_box)
        #self.v_box.addLayout(self.copy_h_box)
        #self.v_box.addLayout(self.paste_h_box)

        self.setLayout(self.v_box)
        self.convert = True

    def set_coding(self, coding):
        self.coding = coding
        self.str_to_bytes()

    def show_dialog_help(self):
        text = "СПО позволяет провести частотный анализ изображений и выявить наиболее часто встречающуюся бинарную " \
               "последовательность.</p><p align='right'>Разработал: к-т Афанасьев А.И.</p>"
        dialog = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, "Справка", "<p align='justify'>" + text,
                                       buttons=QtWidgets.QMessageBox.Ok, parent=self)
        dialog.exec()

    def clear(self):
        self.text_edit.clear()
        self.hex_text_edit.clear()

    def bytes_to_str(self):
        if self.convert:
            self.text_edit.blockSignals(True)

        self.text_edit.clear()
        string = self.hex_text_edit.toPlainText()
        try:
            letters = string.split(' ')
            res = ''
            for letter in letters:
                res += bytearray.fromhex((hex(int(letter, base=2))[2:])).decode(self.coding)
            self.text_edit.insertPlainText(res)
        except:
            self.text_edit.insertPlainText('invalid data!')
        if self.convert:
            self.text_edit.blockSignals(False)

    def str_to_bytes(self):
        if self.convert:
            self.hex_text_edit.blockSignals(True)
        try:
            self.hex_text_edit.clear()
            string = self.text_edit.toPlainText()
            byte_string = string.encode(self.coding)
            res = ''
            for b in byte_string:
                res += bin(b)[2:] + ' '
            self.hex_text_edit.setText(res)
        except:
            if self.convert:
                self.hex_text_edit.blockSignals(False)
        if self.convert:
            self.hex_text_edit.blockSignals(False)

    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(self, 'Выйти', "Вы уверены что хотите выйти?",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def error(self, text):
        dialog = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Critical, "Ошибка!", text,
                                       buttons=QtWidgets.QMessageBox.Ok, parent=self)
        dialog.exec()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    window = QtWidgets.QMainWindow()

    widget = TextToBinWidget()
    window.setCentralWidget(widget)
    window.setMenuBar(widget.menu_bar)
    window.setWindowIcon(QIcon(resource_path('dec.png')))
    window.setWindowTitle("Блочный шифр")
    window.setStatusBar(QtWidgets.QStatusBar())
    screen = app.primaryScreen()
    size = screen.size()
    window.setGeometry(QtCore.QRect(int(size.width() / 2) - 320, int(size.height() / 2) - 210, 640, 420))
    window.show()

    sys.exit(app.exec_())