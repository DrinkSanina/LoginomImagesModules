import builtin_data
from builtin_data import InputTable, InputTables, InputVariables, OutputTable, DataType, DataKind, UsageType
import numpy as np, pandas as pd
from builtin_pandas_utils import to_data_frame, prepare_compatible_table, fill_table

import tkinter as tk
import tkinter.filedialog as fd

# Создание экзкмпляра окна Tkinter и его скрытие с экрана
root = tk.Tk()
root.withdraw()

# Запуск окна выбора файлов
save_directory = fd.askdirectory(parent=root, title='Выберите директорию с изображениями')
output_frame = pd.DataFrame({"root_path": [save_directory]})
fill_table(OutputTable, output_frame, with_index=False)

# Уничтожение скрытого в начале окна, чтобы освободить ресурсы и позволить перезапускать узел
root.destroy()