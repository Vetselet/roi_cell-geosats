from constellation import *
from interference import *
from random import randint

def infoInterference(df_structure):
    cellIdx   = randint(0, roi.cellCount) # Задание рандомного номера соты
    epochIdx  = randint(0, len(epochs))  # Задание рандомной эпохи

    # Число видимых геостацинарных спутников из данной соты
    visibleGeoSatsCount = len(df_structure['geosats'][df_structure['cells']==cellIdx].unique())

    for geoSatIdx in range(visibleGeoSatsCount):
        satList = df_structure['sats'][(df_structure['cells'] == cellIdx)     & 
                                           (df_structure['geosats'] == geoSatIdx)  & 
                                           (df_structure['time'] == epochIdx)].tolist()
        print(f"Между сотой номер {cellIdx} и геостационарным спутником номер {geoSatIdx} в эпоху {epochIdx}:")
        print(f'находится {len(satList)} низкоорбитальных спутников.')
        print(f'Индексы спутников: {satList}\n')

# создание объекта типа Constellation, инициализация параметрами группировки Stalink из конфига
constellation = Constellation('Starlink')

# вычисление элементов орбиты для всех КА в начальный момент
constellation.getInitialState()

# определение точек на оси времени, в которые будут проихзводиться расчёты
epochs = list(range(1002))

# расчёт положений всех КА в заданные моменты времени
constellation.propagateJ2(epochs)


''' 
Создание класса для вычисления КА, которые мешают подавать сигнал геостационарным спутникам.
cellCount -- число сот, geoSatsCount -- число геостационарных спутников, 
angleDegLimit -- предельный угол между направлением от центра соты на любой видимый из неё 
геостационарный спутник и направлением от центра соты на КА.
Примечание: запуск числа сот равным в 64000 продолжается порядка 3 часов.
Поэтому результаты записаны в файл "visibility_2deg.json".
В качестве выходных данных выступает roi.df_structure -- датафрейм, в котором содержится информация 
о номере ячейки, о номере геостационарного спутника, о номере низкоорбитального спутника, об эпохе.
'''        
roi=Roi(constellation, epochs, cellCount=10, geoSatsCount = 4, angleDegLimit=2)

# Получение id спутников, видимых геостационарным спутникам
roi.getVisibleSats()

# Информация по числу спутников при рандомном номере соты и эпохе
infoInterference(roi.df_structure)


# Получение результатов из файла для числа сот 64000
df_structure = roi.readFromFile()
print('Из файла')
infoInterference(df_structure)






