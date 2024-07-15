# Original keras model code by Atif Bilal (https://www.kaggle.com/code/atifbilal/starter-minerals-identification-39f249e8-0)

import builtin_data
from builtin_data import InputTable, InputTables, InputVariables, OutputTable, DataType, DataKind, UsageType

import numpy as np, pandas as pd
from builtin_pandas_utils import to_data_frame, prepare_compatible_table, fill_table

from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.model_selection import train_test_split

from keras import backend as K
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam,SGD,Adagrad,Adadelta,RMSprop
from keras.utils import to_categorical

from keras.layers import Dropout, Flatten,Activation
from keras.layers import Conv2D, MaxPooling2D, BatchNormalization


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

############# Получение размеров матриц изображений ##################
dimensions_frame = to_data_frame(InputTables[0])
dimensions_raw = dimensions_frame["dimensions"][0]

dimensions = ConvertArrayToNumpy(dimensions_raw, int)
######################################################################

################## Сбор выборки ##################
splits = to_data_frame(InputTables[0])

x_train = []
x_test = []
y_train = []
y_test = []


for index, row in splits.iterrows():
    if(row['purpose'] == "y_train"):
        y_train.append(ConvertArrayToNumpy(row['data'], np.float64))
    elif(row['purpose'] == "y_test"):
        y_test.append(ConvertArrayToNumpy(row['data'], np.float64))
    elif(row['purpose'] == "x_train"):
        x_train.append(ConvertImageBytesToNumpy(row['data'], dimensions))
    elif(row['purpose'] == "x_test"):
        x_test.append(ConvertImageBytesToNumpy(row['data'], dimensions))

x_train = np.array(x_train)
x_test = np.array(x_test)
y_train = np.array(y_train)
y_test = np.array(y_test)

##################################################



################## Классификатор Keras ##########
model = Sequential()
model.add(Conv2D(filters = 32, kernel_size = (5,5),padding = 'Same',activation ='relu', input_shape = dimensions))
model.add(MaxPooling2D(pool_size=(2,2)))

model.add(Conv2D(filters = 64, kernel_size = (3,3),padding = 'Same',activation ='relu'))
model.add(MaxPooling2D(pool_size=(2,2), strides=(2,2)))
 
model.add(Conv2D(filters =96, kernel_size = (3,3),padding = 'Same',activation ='relu'))
model.add(MaxPooling2D(pool_size=(2,2), strides=(2,2)))

model.add(Conv2D(filters = 96, kernel_size = (3,3),padding = 'Same',activation ='relu'))
model.add(MaxPooling2D(pool_size=(2,2), strides=(2,2)))

model.add(Flatten())
model.add(Dense(512))
model.add(Activation('relu'))
model.add(Dense(y_train[0].shape[0], activation = "softmax"))

batch_size=InputTables[1].Get(0, "batch_size")
epochs = InputTables[1].Get(0, "epochs")

datagen = ImageDataGenerator(
        featurewise_center=False,
        samplewise_center=False,
        featurewise_std_normalization=False,
        samplewise_std_normalization=False,
        zca_whitening=False,
        rotation_range=30,
        zoom_range = 0.1,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        vertical_flip=False)


datagen.fit(x_train)

model.compile(optimizer=Adam(),loss='categorical_crossentropy',metrics=['accuracy'])
sgd = SGD(decay=1e-6, momentum=0.9, nesterov=True)
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

History = model.fit(datagen.flow(x_train,y_train, batch_size=batch_size),
                              epochs = epochs, validation_data = (x_test,y_test),
                              verbose = 1, steps_per_epoch=x_train.shape[0] // batch_size)

acc = History.history['accuracy']
val_acc = History.history['val_accuracy']

loss = History.history['loss']
val_loss = History.history['val_loss']

predictions = model.predict(x_test)
predictionMineral=np.argmax(predictions,axis=1)

output_frame = pd.DataFrame(columns=['data', 'purpose'])

for i in range(0, len(y_test)):
    y_bytes = y_test[i].tobytes()
    output_frame.loc[len(output_frame.index)] = [y_bytes, "y_test"]
    
for i in range(0, len(x_test)):
    x_bytes = x_test[i].tobytes()
    output_frame.loc[len(output_frame.index)] = [x_bytes, "x_test"]

    
output_frame.loc[len(output_frame.index)] = [np.array(acc).tobytes(), "train_accuracy"]
output_frame.loc[len(output_frame.index)] = [np.array(val_acc).tobytes(), "test_accuracy"]
output_frame.loc[len(output_frame.index)] = [np.array(loss).tobytes(), "train_loss"]
output_frame.loc[len(output_frame.index)] = [np.array(val_loss).tobytes(), "test_loss"]
output_frame.loc[len(output_frame.index)] = [predictionMineral.tobytes(), "predictionMineral"]
output_frame.loc[len(output_frame.index)] = [dimensions_frame["dimensions"][0], "dimensions"]



if isinstance(OutputTable, builtin_data.ConfigurableOutputTableClass):
    prepare_compatible_table(OutputTable, output_frame, with_index=False)
    
fill_table(OutputTable, output_frame, with_index=False)

##################################################
