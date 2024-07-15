import builtin_data
from builtin_data import InputTable, InputTables, InputVariables, OutputTable, DataType, DataKind, UsageType

import numpy as np, pandas as pd
from builtin_pandas_utils import to_data_frame, prepare_compatible_table, fill_table

import cv2
from skimage import feature

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

# Функция извлечения цветовой гистограммы
def extract_histogram(image, bins=(8, 8, 8)):
    hist = cv2.calcHist([image], [0, 1, 2], None, bins, [0, 256, 0, 256, 0, 256])
    cv2.normalize(hist, hist)
    return np.array(hist.flatten())
    
######################################################################

############# Получение размеров матриц изображений ##################
dimensions_frame = to_data_frame(InputTables[0])
dimensions_raw = dimensions_frame["dimensions"][0]

dimensions = ConvertArrayToNumpy(dimensions_raw, int)
######################################################################

############# Получение самих изображений ############################
input_frame = to_data_frame(InputTables[0])

#input_frame["image_array"] = np.nan
images_data = []

for i in range(0, input_frame.shape[0]):
    ImageBytes = input_frame["data"][i]
    images_data.append(ConvertImageBytesToNumpy(ImageBytes, dimensions))
#######################################################################

bin_size = InputTables[1].Get(0, "bin_size")
bins = [bin_size, bin_size, bin_size]

grays = []
histograms = []

for i in range(0, len(images_data)):
    histograms.append(extract_histogram(images_data[i], bins))

    
histogram_bytes = []
for i in range(0, len(images_data)):
    histogram_bytes.append(histograms[i].tobytes())


# Полученный выходной pd.DataFrame
output_frame = pd.DataFrame({"filename": input_frame["filename"], "class": input_frame["class"], "data": histogram_bytes, "dimensions": dimensions_frame["dimensions"][0]})

# Если включена опция "Разрешить формировать выходные столбцы из кода", структуру выходного набора можно подготовить по pd.DataFrame
if isinstance(OutputTable, builtin_data.ConfigurableOutputTableClass):
    prepare_compatible_table(OutputTable, output_frame, with_index=False)
fill_table(OutputTable, output_frame, with_index=False)
