import builtin_data
from builtin_data import InputTable, InputTables, InputVariables, OutputTable, DataType, DataKind, UsageType
import numpy as np, pandas as pd
from builtin_pandas_utils import to_data_frame, prepare_compatible_table, fill_table

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import QMessageBox, QFileDialog
import sys
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import urllib
import shutil
import requests
from multiprocessing import Pool
from PyQt5 import QtWidgets, QtCore
import urllib.request
import os
import asyncio
import time
from PyQt5.QtGui import QIntValidator

# Класс формы с встроенным браузером
class MineralBrowser(QMainWindow):
    htmlFinished = pyqtSignal()
    def __init__(self, mineral_name):
        # Первоначальное создание формы
        super(MineralBrowser, self).__init__()
        self.setWindowTitle("Mineral Browser")
        self.setFixedWidth(1280)
        self.setFixedHeight(720)
        self.mineral_name = mineral_name
        layout = QVBoxLayout()
        
        # Встраивание браузера в окно с открытой ссылкой на минерал
        self.view = QWebEngineView()
        layout.addWidget(self.view)
        self.view.load(QUrl(f"https://www.mindat.org/photoscroll.php?frm_id=pscroll&cform_is_valid=1&searchbox={mineral_name}&submit_pscroll=Search'"))
        
        # Строчка с целочисленным значением оффсета - с какой картинки по счету
        # следует начать загрузку
        self.e1 = QLineEdit()
        self.e1.setValidator(QIntValidator())
        self.e1.setMaxLength(5)
        self.e1.setPlaceholderText("Оффсет скачивания изображений (целое число)")
      
        # Создание кнопки сохранения
        btn = QPushButton('Сохранить изображения')
        btn.clicked.connect(self.onSaveButtonClick)
        btn.resize(btn.sizeHint())
        layout.addWidget(self.e1)
        layout.addWidget(btn)
        
        
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
    
    # Необходимая функция, позволяющая заполучить html-страницу
    def callback(self, html):
        self.mHtml = html
        self.htmlFinished.emit()
    
    # Обработка нажатия на клавишу "Сохранить" - подсчитывает число фотографий,
    # а также запускает окно подтверждения
    def onSaveButtonClick(self):
        # Получить html-страницу в переменную mHtml
        self.view.page().toHtml(self.callback)
        loop = QEventLoop()
        self.htmlFinished.connect(loop.quit)
        loop.exec_()
        photo_links = []
        
        # Парсинг html-страницы. Поиск всех атрибутов <href> в тегах <a>, 
        # где присутствует слово и ссылка на фотографию 
        soup = BeautifulSoup(self.mHtml, 'html.parser')
        for link in soup.findAll('a'):
            linktext = str(link.get('href'))
            if("photo" in linktext and ".html" in linktext):
                photo_links.append("https://www.mindat.org"+linktext)
                
        offset = 0
        if(self.e1.text() != ""):
            offset = int(self.e1.text())
        reply = QMessageBox.question(self, 'Загрузка изображений', f'Будет загружено до {len(photo_links) - offset} изображений', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.downloadImages(photo_links)
    
    # Функция непосредственной загрузки фотографии
    def downloadImages(self, photo_links):
        save_directory = QFileDialog.getExistingDirectory(self, 'Выберите место для сохранения изображений')
        if(save_directory):
            try:
                progress = QProgressDialog('Загрузка', 'Отмена', 0,len(photo_links), self)
                progress.setCancelButton(None)
                progress.setWindowModality(Qt.WindowModal)
                progress.show()
                progress.setValue(0)
                
                
                offset = 0
                if(self.e1.text() != ""):
                    offset = int(self.e1.text())
                for y in range(offset, len(photo_links)):
                    # Создать первый запрос - по адресу изображения и перейти на страницу просмотра
                    url_request = Request(photo_links[y], headers={"User-Agent": "Mozilla/5.0"})
                    # Считать ответ первого запроса
                    webpage = urlopen(url_request).read()
                    # Снова парсинг, но на этот раз - поиск всех тегов <img>, где есть слова "xpic", "imagecache" или "photos",
                    # тк. в ссылках на первоначальные изображения на mindat.org всегда указано одно из этих слов
                    soup = BeautifulSoup(webpage, 'html.parser')
                    for t in soup.find_all('img', src=lambda x: x and ('xpic' in x or 'imagecache' in x or 'photos' in x)):
                        # Последний запрос, но уже по пути оригинального изображения
                        image_url = "https://www.mindat.org/"+t['src']
                        req = urllib.request.Request(image_url, data=None,headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'})
                        f = urllib.request.urlopen(req)
                        # Сохранить изображение по пути сохранения с именем - номером изображения в каталоге
                        with open(f"{save_directory}\\{self.mineral_name}-{y+1}.png", 'wb') as file:
                            shutil.copyfileobj(f, file)
                        break
                    progress.setValue(y)
                
                # Заполнение выходного узла
                output_frame = pd.DataFrame({"Mineral_name": [self.mineral_name], "Images_path": [save_directory]})
                fill_table(OutputTable, output_frame, with_index=False)
                QCoreApplication.quit()
                          
            except Exception as e:
                errBox = QMessageBox()
                errBox.setWindowTitle('Error')
                errBox.setText('Error: ' + str(e))
                errBox.addButton(QMessageBox.Ok)
                errBox.exec()
                return
            
if InputTable:
    input_frame = to_data_frame(InputTable)
    mineral_name = input_frame.iloc[:1].to_string(header=False, index=False)
    
    app = QApplication(sys.argv)
    window = MineralBrowser(mineral_name)
    window.show()
    app.exec()
    
else:
    sys.stderr("Не выбран минерал для поиска")
