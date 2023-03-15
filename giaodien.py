from PyQt5 import QtCore, QtGui, QtWidgets
"""
import subprocess

# Run a Python script from within another Python script
subprocess.run(["python", "D:/project passsss/5-giaodien/main.py"])
"""

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(600, 350)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.img = QtWidgets.QLabel(self.centralwidget)
        self.img.setGeometry(QtCore.QRect(30, 230, 371, 131))
        self.img.setText("")
        self.img.setPixmap(QtGui.QPixmap("../.designer/backup/results.jpg"))
        self.img.setScaledContents(True)
        self.img.setWordWrap(False)
        self.img.setOpenExternalLinks(False)
        self.img.setObjectName("img")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(40, 20, 471, 41))
        font = QtGui.QFont()
        font.setPointSize(24)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(10, 80, 631, 41))
        font = QtGui.QFont()
        font.setPointSize(24)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(40, 170, 191, 21))
        self.label_6.setObjectName("label_6")
        self.btn_img = QtWidgets.QPushButton(self.centralwidget)
        self.btn_img.setGeometry(QtCore.QRect(20, 270, 131, 61))
        self.btn_img.setObjectName("btn_img")
        self.btn_vid = QtWidgets.QPushButton(self.centralwidget)
        self.btn_vid.setGeometry(QtCore.QRect(220, 270, 131, 61))
        self.btn_vid.setObjectName("btn_vid")
        self.btn_real = QtWidgets.QPushButton(self.centralwidget)
        self.btn_real.setGeometry(QtCore.QRect(420, 270, 131, 61))
        self.btn_real.setObjectName("btn_real")
        self.txt_img = QtWidgets.QTextEdit(self.centralwidget)
        self.txt_img.setEnabled(True)
        self.txt_img.setGeometry(QtCore.QRect(400, 130, 141, 131))
        self.txt_img.setObjectName("txt_img")

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "ĐỒ ÁN TỐT NGHIỆP"))
        self.label_2.setText(_translate("MainWindow", "ĐỒ ÁN TỐT NGHIỆP"))
        self.label_3.setText( _translate("MainWindow", "NHẬN DIỆN BIỂN SỐ XE "))
        self.label_6.setText(_translate("MainWindow", "DTC1854802010113-TRẦN TRUNG KIÊN"))
        self.btn_img.setText(_translate("MainWindow", "IMGAGE"))
        self.btn_vid.setText(_translate("MainWindow", "VIDEO"))
        self.btn_real.setText(_translate("MainWindow", "REALTIME"))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())