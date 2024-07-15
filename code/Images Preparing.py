import builtin_data
from builtin_data import InputTable, InputTables, InputVariables, OutputTable, DataType, DataKind, UsageType
import numpy as np, pandas as pd
from builtin_pandas_utils import to_data_frame, prepare_compatible_table, fill_table
import os
import cv2


if InputTable:
    # Из первого входного узла получить корневую директорию
    input_frame = to_data_frame(InputTables[0])
    root_folder = input_frame.iloc[:1].to_string(header=False, index=False)
    folders = os.listdir(root_folder)
    
    # Из второго входного узла получить размеры, к которым будут приведены
    # изображения
    height = InputTables[1].Get(0, "height")
    width = InputTables[1].Get(0, "width")
    
    image_names = []
    train_labels = []
    train_images = []
    
    size = height,width
    
    # Проход по всем файлам и папкам в корневой директории
    for folder in folders:
        for file in os.listdir(os.path.join(root_folder,folder)):
            # Если попался файл изображения
            if file.endswith("jpg") or file.endswith("png"):
                # Добавить имя файла в выходной узел
                image_names.append(os.path.join(root_folder,folder,file))
                # Добавить имя класса в выходной узел
                train_labels.append(folder)
                # Считать файл изображения, представить его в виде массива numpy,
                # и изменить размер
                img = cv2.imread(os.path.join(root_folder,folder,file))
                im = cv2.resize(img,size)
                train_images.append(im)
                print(len(train_images))
            else:
                continue
    
    imageNpArray = np.array(train_images)
    
    allimages = []
    dimensions = []
    
    i=0
    # Преобразовать каждый массив numpy в байт-строку
    for i in range(i, len(train_images)):
        imagebytes = imageNpArray[i].tobytes()
        dimension = np.array(imageNpArray[i].shape).tobytes()
        dimensions.append(dimension)
        allimages.append(imagebytes)
            
    # Заполнение выходного фрейма
    output_frame = pd.DataFrame({"filename": image_names, "class": train_labels, "data": allimages, "dimensions": dimensions})

    
    if isinstance(OutputTable, builtin_data.ConfigurableOutputTableClass):
        prepare_compatible_table(OutputTable, output_frame, with_index=False)
    fill_table(OutputTable, output_frame, with_index=False)