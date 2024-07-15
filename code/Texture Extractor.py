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

class LocalBinaryPatterns:
    def __init__(self, numPoints, radius):
        self.numPoints = numPoints
        self.radius = radius

    def describe(self, image, eps=1e-7):
        lbp = feature.local_binary_pattern(image, self.numPoints,
            self.radius, method="uniform")
        (hist, _) = np.histogram(lbp.ravel(),
            bins=np.arange(0, self.numPoints + 3),
            range=(0, self.numPoints + 2))

        # normalize the histogram
        hist = hist.astype("float")
        hist /= (hist.sum() + eps)

        return np.array(hist)


    
descriptor = LocalBinaryPatterns(32, 8)

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

grays = []
histograms = []

for i in range(0, len(images_data)):
    grays.append(cv2.cvtColor(images_data[i], cv2.COLOR_BGR2GRAY))
    histograms.append(descriptor.describe(grays[i]))

    
histogram_bytes = []
for i in range(0, len(images_data)):
    histogram_bytes.append(histograms[i].tobytes())

# Полученный выходной pd.DataFrame
output_frame = pd.DataFrame({"filename": input_frame["filename"], "class": input_frame["class"], "data": histogram_bytes, "dimensions": dimensions_frame["dimensions"][0]})

# Если включена опция "Разрешить формировать выходные столбцы из кода", структуру выходного набора можно подготовить по pd.DataFrame
if isinstance(OutputTable, builtin_data.ConfigurableOutputTableClass):
    prepare_compatible_table(OutputTable, output_frame, with_index=False)
fill_table(OutputTable, output_frame, with_index=False)
