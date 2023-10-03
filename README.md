# Задача

*Реализуйте вычислительную процедуру, позволяющую равномерно расположить N точек на поверхности сферической Земли. Воспользовавшись этой процедурой, разделите поверхность Земли на 64000 примерно одинаковых области (соты). Для некоторого состояния космической системы (координаты КА, соответствующие группировке 'Starlink' из constellationTest.json и некоторому фиксированному моменту времени, вычисление координат реализовано в примере) определите для каждой соты набор КА, которые удовлетворяют следующему условию: угол между направлением от центра соты на любой видимый из неё геостационарный спутник составляет с направлением от центра соты на КА не более 2 градусов. Для простоты будем считать, что геостационарных спутников всего 4 и они равномерно распределены по геостационарной орбите.*
  
*Создайте структуру данных, в которой содержится список таких КА для каждой соты.*

*P.S. Фактически в задаче реализуется упрощённая маска, позволяющая учитывать требования электромагнитной совместимости проектируемой группировки с геостационарными системами.*


Процедура осуществлена в файле [interference.py](https://github.com/Vetselet/roi_cell-geosats/blob/main/interference.py) в виде класса.

Запустить процедуру можно в файле [run_interference.py](https://github.com/Vetselet/roi_cell-geosats/blob/main/run_interference.py).
В качестве результата будет датафрейм, в котором содержится информация 
о номере ячейки, о номере геостационарного спутника, о номере низкоорбитального спутника и об эпохе.

Для числа сот 64000 результат процедуры записан в файле []().

Ответ на первую задачу записан в файле [CodeReview.pdf](https://github.com/Vetselet/roi_cell-geosats/blob/main/CodeReview.pdf)


