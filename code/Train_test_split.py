import builtin_data
from builtin_data import InputTable, InputTables, InputVariables, OutputTable, DataType, DataKind, UsageType
import numpy as np, pandas as pd
from builtin_pandas_utils import to_data_frame, prepare_compatible_table, fill_table
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from keras.utils import to_categorical

input_frame1 = to_data_frame(InputTables[0])
_test_size = InputTables[1].Get(0, "test_size")
_random_state = InputTables[1].Get(0, "random_state")


le=LabelEncoder()
Y=le.fit_transform(input_frame1["class"])
Y=to_categorical(Y, input_frame1["class"].nunique())
X=np.array(input_frame1["data"])

# Простое разбиение на тренировочную и тестовую выборку
x_train,x_test,y_train,y_test=train_test_split(X,Y,test_size=_test_size,random_state=_random_state)
print(x_train.shape)

# Создание выходного узла при помощи циклов. Необходимость заключается в том, чтобы
# на выходе из узла иметь структуру, хранящую разные данные (метка класса - одномерный массив, 
# когда как изображение - многомерный) в унифицированном виде, чтобы их можно было передать
# плоской таблицей

# data - одномерный или многомерный массив (байт-строка по сути)
# purpose - назначение data
# dimensions - размер для изображений

output_frame = pd.DataFrame(columns=['data', 'purpose', 'dimensions'])

for i in range(0, len(x_train)):
    output_frame.loc[i] = [x_train[i], "x_train", input_frame1["dimensions"][0]]
    
for i in range(0, len(x_test)):
    output_frame.loc[len(output_frame.index)] = [x_test[i], "x_test", input_frame1["dimensions"][0]]
    
for i in range(0, len(y_train)):
    y_bytes = np.array(y_train[i]).tobytes()
    output_frame.loc[len(output_frame.index)] = [y_bytes, "y_train", ""]
    
for i in range(0, len(y_test)):
    y_bytes = np.array(y_test[i]).tobytes()
    output_frame.loc[len(output_frame.index)] = [y_bytes, "y_test", ""]

    
if isinstance(OutputTable, builtin_data.ConfigurableOutputTableClass):
    prepare_compatible_table(OutputTable, output_frame, with_index=False)

fill_table(OutputTable, output_frame, with_index=False)