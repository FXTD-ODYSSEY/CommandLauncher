# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\MayaTecent\CommandLauncher\ui\CommandLauncher.ui'
#
# Created: Wed Dec 11 17:23:27 2019
#      by: pyside2-uic  running on PySide2 2.0.0~alpha0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(379, 120)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.Scroll_Lock_SP = QtWidgets.QSpinBox(Form)
        self.Scroll_Lock_SP.setObjectName("Scroll_Lock_SP")
        self.gridLayout.addWidget(self.Scroll_Lock_SP, 2, 3, 1, 1)
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 2, 1, 1)
        self.label_5 = QtWidgets.QLabel(Form)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 0, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(Form)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 3, 2, 1, 1)
        self.Display_SP = QtWidgets.QSpinBox(Form)
        self.Display_SP.setMaximum(9)
        self.Display_SP.setObjectName("Display_SP")
        self.gridLayout.addWidget(self.Display_SP, 3, 3, 1, 1)
        self.Scroll_Start_SP = QtWidgets.QSpinBox(Form)
        self.Scroll_Start_SP.setObjectName("Scroll_Start_SP")
        self.gridLayout.addWidget(self.Scroll_Start_SP, 2, 1, 1, 1)
        self.label = QtWidgets.QLabel(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 2, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)
        self.Shortcut_SP = QtWidgets.QSpinBox(Form)
        self.Shortcut_SP.setMaximum(9)
        self.Shortcut_SP.setObjectName("Shortcut_SP")
        self.gridLayout.addWidget(self.Shortcut_SP, 3, 1, 1, 1)
        self.comboBox = QtWidgets.QComboBox(Form)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.gridLayout.addWidget(self.comboBox, 0, 1, 1, 3)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle("Form")
        self.label_2.setText("scroll lock line")
        self.label_5.setText("Language Mode")
        self.label_4.setText("item display num")
        self.label.setText("scroll start line")
        self.label_3.setText("shortcut number")
        self.comboBox.setItemText(0, "English")
        self.comboBox.setItemText(1, u"中文")

