import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from seoul_widget import *

class SeoulForTour(QWidget, Ui_Form):
    def __init__(self, name, address, working_day, working_time, holiday, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.seoul_main = parent
        self.name = name
        self.address = address
        self.working_day = working_day
        self.working_time = working_time
        self.holiday = holiday

        self.name_lab.setText(f"이 름 : {self.name}")
        self.type_lab.setText(f"운영요일 : {self.working_day}\n운영시간 : {self.working_time}\n휴무일 :{self.holiday}")
        self.location_lab.setText(f"주 소 : {self.address}")
        # self.img_label.setPixmap(QPixmap(f"{self.img_path}"))

    def mousePressEvent(self, event):
        self.seoul_main.stackedWidget.setCurrentWidget(self.seoul_main.main_page_4)
        self.seoul_main.name_lab.setText(f"이 름 : {self.name}")
        self.seoul_main.type_lab.setText(f"운영요일 : {self.working_day}\n운영시간 : {self.working_time}\n휴무일 :{self.holiday}")
        self.seoul_main.location_lab.setText(f"주 소 : {self.address}")
        # self.seoul_main.img_label.setPixmap(QPixmap(f"{self.img_path}"))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWindow = SeoulForTour()
    myWindow.show()
    app.exec()
