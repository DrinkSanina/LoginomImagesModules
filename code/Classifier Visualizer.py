import builtin_data
from builtin_data import InputTable, InputTables, InputVariables, OutputTable, DataType, DataKind, UsageType
import numpy as np, pandas as pd
from builtin_pandas_utils import to_data_frame, prepare_compatible_table, fill_table
from sklearn.preprocessing import LabelEncoder

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvas

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class MainWindow(QWidget):
    def __init__(self, x_test, wrong_answers, right_answers, predictionMineral, label_encoder):
        super().__init__()
        self.setWindowTitle('Визуализатор классификатора')
        self.setGeometry(0, 0, 1200, 900)
        self.setFixedSize(1400,900)
        
        gridLayout = QGridLayout()
        
        formLayout = QFormLayout()
        formLayout2 = QFormLayout()
        
        groupBox = QGroupBox()
        groupBox2 = QGroupBox()

        label_right = QLabel("Правильные ответы классификатора")
        label_wrong = QLabel("Неправильные ответы классификатора")
        label_right.setAlignment(Qt.AlignCenter)
        label_wrong.setAlignment(Qt.AlignCenter)
        label_right.setStyleSheet("QLabel {background-color: green; color: white; font-size: 18pt}")
        label_wrong.setStyleSheet("QLabel {background-color: red; color: white; font-size: 18pt}")

        formLayout.addRow(label_right)
        formLayout2.addRow(label_wrong)
                    
        for n in range(len(right_answers)):
            figure = Figure(figsize=(4, 4))
            canvas = FigureCanvas(figure)
            ax = figure.subplots()
            ax.grid()
            ax.imshow(x_test[right_answers[n]])
            ax.set_title("Предсказанный класс : "+str(label_encoder.inverse_transform([predictionMineral[right_answers[n]]]))+"\n"+"Правильный класс : "+str(label_encoder.inverse_transform([c[right_answers[n]]])))
            formLayout.addRow(canvas)
            
        for n in range(len(wrong_answers)):
            figure = Figure(figsize=(4, 4))
            canvas = FigureCanvas(figure)
            ax = figure.subplots()
            ax.grid()
            ax.imshow(x_test[wrong_answers[n]])
            ax.set_title("Предсказанный класс : "+str(label_encoder.inverse_transform([predictionMineral[wrong_answers[n]]]))+"\n"+"Правильный класс : "+str(label_encoder.inverse_transform([c[wrong_answers[n]]])))
            formLayout2.addRow(canvas)
        
        
        groupBox.setLayout(formLayout)
        groupBox2.setLayout(formLayout2)

        scroll = QScrollArea()
        scroll2 = QScrollArea()
        
        scroll.setWidget(groupBox)
        scroll2.setWidget(groupBox2)
        
        scroll.setWidgetResizable(False)
        scroll2.setWidgetResizable(False)

        

        layout = QGridLayout(self)
        layout.addWidget(scroll, 0, 0)
        layout.addWidget(scroll2, 0, 1)

################### Обмен изображениями между узлами ################

def ConvertImageBytesToNumpy(ImageByteString, Dimensions):
    img_bytes = ImageByteString.encode().decode('unicode_escape').encode("raw_unicode_escape")
    img_bytes = img_bytes[2:-1]
    image_array = np.frombuffer(img_bytes, dtype = np.uint8)
    reshaped = image_array.reshape(Dimensions)
    return reshaped

def ConvertArrayToNumpy(ArrayByteString, Type):
    arr_bytes = ArrayByteString.encode().decode('unicode_escape').encode("raw_unicode_escape")
    arr_bytes = arr_bytes[2:-1]
    result_array = np.frombuffer(arr_bytes, dtype=Type)
    return result_array
######################################################################

############# Параметры визуализации #############
icon_size = InputTables[1].Get(0, "icon_size")
columns = InputTables[1].Get(0, "columns")
max_images = InputTables[1].Get(0, "max_images")
##################################################

splits = to_data_frame(InputTables[0])

dimensions = ConvertArrayToNumpy(splits.loc[splits['purpose'] == "dimensions"]['data'].values[0], int)


train_accuracy = ConvertArrayToNumpy(splits.loc[splits['purpose'] == "train_accuracy"]['data'].values[0], float)
test_accuracy = ConvertArrayToNumpy(splits.loc[splits['purpose'] == "test_accuracy"]['data'].values[0], float)
train_loss = ConvertArrayToNumpy(splits.loc[splits['purpose'] == "train_loss"]['data'].values[0], float)
test_loss = ConvertArrayToNumpy(splits.loc[splits['purpose'] == "test_loss"]['data'].values[0], float)
predictionMineral =  ConvertArrayToNumpy(splits.loc[splits['purpose'] == "predictionMineral"]['data'].values[0], np.uint64)

y_test = []
x_test = []

for index, row in splits.iterrows():
    if(row['purpose'] == "y_test"):
        y_test.append(ConvertArrayToNumpy(row['data'], np.float64))
    elif(row['purpose'] == "x_test"):
        x_test.append(ConvertImageBytesToNumpy(row['data'], dimensions))

i=0
right_answers=[]
wrong_answers=[]

for i in range(len(y_test)):
    if(np.argmax(y_test[i])==predictionMineral[i]):
        right_answers.append(i)
    if(len(right_answers)==max_images):
        break

i=0
for i in range(len(y_test)):
    if(not np.argmax(y_test[i])==predictionMineral[i]):
        wrong_answers.append(i)
    if(len(wrong_answers)==max_images):
        break

c = np.argmax(y_test, axis=1)
        
app = QApplication([])

label_encoder=LabelEncoder()
label_encoder.fit_transform(to_data_frame(InputTables[2])["class"])

window = MainWindow(x_test, wrong_answers, right_answers, predictionMineral, label_encoder)
window.show()

    
output_frame = pd.DataFrame({"train_accuracy": train_accuracy, "test_accuracy": test_accuracy, "train_loss": train_loss, "test_loss": test_loss})
if isinstance(OutputTable, builtin_data.ConfigurableOutputTableClass):
    prepare_compatible_table(OutputTable, output_frame, with_index=False)

fill_table(OutputTable, output_frame, with_index=False)

sys.exit(app.exec())
