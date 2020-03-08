from PySide2 import QtWidgets

dialog = QtWidgets.QInputDialog()
dialog.setOkButtonText     ( u"确定" )
dialog.setCancelButtonText ( u"取消" )
dialog.setComboBoxEditable ( False )

title = QtWidgets.QApplication.translate('pins',"Get The New Pins Name")
msg   = QtWidgets.QApplication.translate('pins',"input pins new name below")
pin_list = ["1","2","3","4"]
dialog.setComboBoxItems ( pin_list )
dialog.setLabelText ( msg )
dialog.setWindowTitle ( title )


if dialog.exec_():
    print dialog.textValue()
# print dialog.open(QtWidgets.QApplication.activeWindow(),"")
#print dialog.getItem(QtWidgets.QApplication.activeWindow(),title,msg,pin_list,editable=False,ok=1)
# print dialog.getText(QtWidgets.QApplication.activeWindow(),title,msg)