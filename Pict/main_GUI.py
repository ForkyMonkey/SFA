from PyQt5 import QtWidgets, QtCore, QtGui
import os
import shutil
import threading

from n_gramm_finder import *
import TTB


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class MainWidget(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.files = []
        self.small = True

        self.l_vbox = QtWidgets.QVBoxLayout()
        self.r_vbox = QtWidgets.QVBoxLayout()
        self.menu_bar = QtWidgets.QMenuBar()

        self.mode_group = QtWidgets.QGroupBox('Режим работы')
        self.bin_rad = QtWidgets.QRadioButton('bin')
        self.bin_rad.setChecked(True)
        self.byte_rad = QtWidgets.QRadioButton('byte')
        self.btns_box = QtWidgets.QHBoxLayout()
        self.btns_box.addWidget(self.bin_rad)
        self.btns_box.addWidget(self.byte_rad)
        self.mode_group.setLayout(self.btns_box)

        self.win_label_max = QtWidgets.QLabel('Максимальный размер последовательности:')
        self.win_spin_max = QtWidgets.QSpinBox()
        self.win_label_min = QtWidgets.QLabel('Минимальный размер последовательности: ')
        self.win_spin_min = QtWidgets.QSpinBox()
        self.win_spin_max.setMinimum(2)
        self.win_spin_max.setValue(10)
        self.win_spin_max.valueChanged.connect(self.change_spin)
        self.win_spin_min.valueChanged.connect(self.change_spin)
        self.win_spin_min.setMinimum(2)
        self.win_max_box = QtWidgets.QHBoxLayout()
        self.win_max_box.addWidget(self.win_label_max)
        self.win_max_box.addWidget(self.win_spin_max)
        self.win_min_box = QtWidgets.QHBoxLayout()
        self.win_min_box.addWidget(self.win_label_min)
        self.win_min_box.addWidget(self.win_spin_min)

        self.scan_btn = QtWidgets.QPushButton('Сканировать')
        self.scan_btn.clicked.connect(self.scan)
        self.res_edit = QtWidgets.QTextEdit()
        self.res_edit.setReadOnly(True)
        self.more_btn = QtWidgets.QPushButton('Подробный отчет')
        self.more_btn.clicked.connect(self.more)
        self.more_btn.setDisabled(True)
        self.scan_btn.setDisabled(True)

        self.l_vbox.addWidget(self.mode_group)
        self.l_vbox.addLayout(self.win_min_box)
        self.l_vbox.addLayout(self.win_max_box)
        self.l_vbox.addWidget(self.scan_btn)
        self.l_vbox.addWidget(self.res_edit)
        self.l_vbox.addWidget(self.more_btn)

        self.chose_btn = QtWidgets.QPushButton('Выбрать файлы')
        self.chose_btn.clicked.connect(self.chose_files)
        self.chosen_edit = QtWidgets.QTextEdit()
        self.chosen_edit.setReadOnly(True)

        self.r_vbox.addWidget(self.chose_btn)
        self.r_vbox.addWidget(self.chosen_edit)

        self.h_box = QtWidgets.QHBoxLayout()
        self.h_box.addLayout(self.l_vbox)
        self.h_box.addLayout(self.r_vbox)

        w = QtWidgets.QWidget()
        w.setLayout(self.h_box)
        self.setCentralWidget(w)

        self.files_dialog = QtWidgets.QFileDialog(self)
        self.files_dialog.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
        self.files_dialog.setViewMode(QtWidgets.QFileDialog.List)

    def change_spin(self):
        if self.win_spin_max.value() < self.win_spin_min.value():
            self.win_spin_min.setValue(self.win_spin_max.value())
        if self.win_spin_min.value() > self.win_spin_max.value():
            self.win_spin_max.setValue(self.win_spin_min.value())

    def chose_files(self):
        result = self.files_dialog.exec()
        self.files.clear()
        if result:
            files = self.files_dialog.selectedFiles()
            if files:
                self.scan_btn.setEnabled(True)
                for file in files:
                    self.files.append(file)
                    self.chosen_edit.insertPlainText(file)
                    self.chosen_edit.insertPlainText('\n')
        else:
            self.chosen_edit.clear()

    def more(self):
        file = QtWidgets.QFileDialog.getSaveFileName(parent=self, filter="Text (*.txt)")
        if file[0]:
            with open('temp.txt', 'rb') as f:
                data = f.read()
            with open(file[0], 'wb') as f:
                f.write(data)

    def scan(self):
        self.res_edit.clear()
        self.more_btn.setEnabled(True)
        thread = threading.Thread(target=self.scan_thread, daemon=True).start()

    def scan_thread(self):
        with open('temp.txt', 'w') as f:
            for file in self.files:
                total_ins = find_n_gramm_total(self.win_spin_min.value(),
                                               self.win_spin_max.value(),
                                               file,
                                               self.bin_rad.isChecked())

                self.res_edit.insertPlainText(f'{file}\n')
                f.write(f'{file}\n')
                max = 0
                ins_max = 0
                for id, ins in enumerate(total_ins):
                    f.write(f'\n{id + self.win_spin_min.value()}\n\n')
                    for key in ins.keys():
                        if len(ins[key]) > max:
                            max = len(ins[key])
                            ins_max = key
                        if self.small:
                            if len(ins[key]) > 20:
                                f.write(f'{key}:\t[{len(ins[key])}]\t{ins[key][:20]}...\n')
                            else:
                                f.write(f'{key}:\t[{len(ins[key])}]\t{ins[key]}\n')
                        else:
                            f.write(f'{key}:\t[{len(ins[key])}]\t{ins[key]}\n')
                self.res_edit.insertPlainText(f'{ins_max}: {max}\n')
                f.write(f'\n\n')
                if not os.path.exists(ins_max):
                    try:
                        os.mkdir(ins_max)
                    except Exception as e:
                        print(e)
                        ins_max = bin(int.from_bytes(ins_max, 'big'))
                        os.mkdir(ins_max)
                try:
                    shutil.copy(file, ins_max)
                except Exception as e:
                    print(e)
                    shutil.copy(file, ins_max.decode())

    def closeEvent(self, a0: QtGui.QCloseEvent):
        if os.path.exists('temp.txt'):
            os.remove('temp.txt')


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)

    window = QtWidgets.QMainWindow()
    window.setWindowTitle("Статистический анализатор файлов")
    main_widget = MainWidget()
    dock = QtWidgets.QDockWidget('Text to Bin', parent=window)
    sub_widget = TTB.TextToBinWidget(parent=dock)
    window.setCentralWidget(main_widget)
    dock.setWidget(sub_widget)
    dock.setFloating(True)
    window.setMenuBar(sub_widget.menu_bar)
    screen = app.primaryScreen()
    size = screen.size()
    window.setGeometry(QtCore.QRect(int(size.width() / 2) - 320, int(size.height() / 2) - 210, 640, 420))
    window.show()

    sys.exit(app.exec_())