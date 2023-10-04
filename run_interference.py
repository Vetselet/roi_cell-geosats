from constellation import *
from interference import *
from random import randint
import os.path


def infoInterference(structure):
    # Видимые геостацинарные спутники из заданной соты в заданный момент времени
    visibleGeoSatsCount = np.unique(structure[:,1][structure[:,0]==cellIdx])
    for geoSatIdx in visibleGeoSatsCount:
        satList = structure[:,2][(structure[:,0] == cellIdx) & (structure[:,1] == geoSatIdx)].tolist()
        print(f"\n    Между сотой номер {cellIdx} и геостационарным спутником номер {geoSatIdx}:")
        print(f'    находится {len(satList)} низкоорбитальных спутников.')
        print(f'    Индексы спутников: {satList}')

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
Примечание: запуск числа сот равным в 64000 продолжается порядка 1.5 часов.
Поэтому результаты записаны в файл "visibility_64000cell_2deg.json".
В качестве выходных данных выступает roi.parametersVisibility -- numpy массив, в котором содержится информация 
о номере ячейки, о номере геостационарного спутника, о номере низкоорбитального спутника.
Или для одной выбранной ячейки массив roi.parametersVisibilityFromCell, аналогичный по строению roi.parametersVisibility
'''        
roi=Roi(constellation, epochs, cellCount=10, geoSatsCount = 4, angleDegLimit=2)


cellIdx   = randint(0, roi.cellCount-1) # Задание рандомного номера соты
epochIdx  = randint(0, len(epochs)-1)  # Задание рандомной эпохи
# cellIdx,epochIdx=0,989    # при этих параметрах точно есть спутники

# Получение id спутников, видимых геостационарным спутникам для заданной соты на определенной эпохе.
roi.getVisibleSatsFromCell(cellIdx,epochIdx) 

# Информация по числу спутников при заданном номере соты и эпохе
print(f'В эпоху {epochIdx}:')
infoInterference(roi.parametersVisibilityFromCell)


# Получение id спутников, видимых геостационарным спутникам для всех сот на определенной эпохе.
# Для числа сот 64000 этот счет длится порядка 2 часов
if roi.cellCount != 64000:
    print('\nРасчет для всех сот')
    roi.getVisibleSats(epoch = epochIdx) 
    print(f'\nВ эпоху {epochIdx}:')
    infoInterference(roi.parametersVisibility)
    roi.writeToFile(name_outfile = f'visibility_{roi.cellCount}cell_{roi.angleDegLimit}deg.json')
    print('Done')

    
# Получение результатов из файла для числа сот 64000 на эпохе 0
name_outfile = f'visibility_64000cell_2deg.json'
if os.path.exists(name_outfile ):
    parametersVisibility = roi.readFromFile(name_outfile = name_outfile)
    print('\nИнформация из файла, в котором результат расчета для 64000 сот на эпохе 0')
    infoInterference(parametersVisibility)


