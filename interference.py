import numpy as np
import pandas as pd
from itertools import chain


class Parameters(object):
    pass

Const = Parameters()
Const.earthRadius = 6378135      # Экваториальный радиус Земли [m]


class Roi:
    def __init__(self, constellation, epochs, cellCount = 64000, geoSatsCount = 4, angleDegLimit = 2):
        self.constellation=constellation
        self.cellCount = cellCount
        self.geoSatsCount = geoSatsCount
        self.angleDegLimit = angleDegLimit   # в градусах
        self.goldenRatio = (1 + 5**0.5)/2
        self.altitudeGeoSats = Const.earthRadius + 35*1000*1000    # в метрах
        self.altitudeSats = np.array([[el for i in range(len(epochs))] for el in self.constellation.elements[:, 0]]) 
        
        self.cell_x, self.cell_y, self.cell_z = self.findSphereCoords(Const.earthRadius, self.cellCount) # Координаты сот
        self.cellsList, self.geoSatsList, self.satsList, self.timeList = [], [], [], []
        self.parametersVisibilityFromCell = np.zeros([])
        self.parametersVisibility = np.zeros([])
#         self.df_structure = pd.DataFrame(columns = ['cells', 'geosats', 'sats', 'time'])

    def findSphereCoords(self, height, dotCount):
        # Сферическая сетка Фибоначчи
        steps = np.arange(0, dotCount)
        theta = 2 * np.pi * steps / self.goldenRatio
        phi = np.arccos(1 - 2 * (steps + 0.5)/dotCount)
        
        x = height * np.cos(theta) * np.sin(phi) 
        y = height * np.sin(theta) * np.sin(phi)
        z = height * np.cos(phi)
        
        return x, y, z
    
    def findDistance(self, cellNumber, coords:str):
        # Поиск расстояния между сотой и спутником
        if coords == 'geo':
            coord_x, coord_y, coord_z = self.findSphereCoords(self.altitudeGeoSats, self.geoSatsCount)
        elif coords == 'low':
            coord_x = self.constellation.stateEci[:, 0, :]
            coord_y = self.constellation.stateEci[:, 1, :]
            coord_z = self.constellation.stateEci[:, 2, :]
            
        d = ((self.cell_x[cellNumber] - coord_x)**2 + \
             (self.cell_y[cellNumber] - coord_y)**2 + \
             (self.cell_z[cellNumber] - coord_z)**2)**0.5

        return d
    
    def findAngleDeg(self, d, altitudeSats):
        ''' Расчет внешнего угла треугольника межд точками: центр Земли, 
        точка расположения соты на поверхности Земли, точка расположения спутника на орбите.
        psi -- угол между направлением на центр Земли и на спутник из соты'''
        
        psi = np.arccos((Const.earthRadius**2 + d**2 - altitudeSats**2)/   
                        (2 * Const.earthRadius * d))                       
        angleDeg = (np.pi - psi) * 180/np.pi 
        
        return angleDeg

    def getVisibleSatsFromCell(self, cellNumber, epoch):
        # Расчет внешнего угла между сотой и геостац. спутником
        D = self.findDistance(cellNumber, coords = 'geo')
        angleDeg = self.findAngleDeg(D, self.altitudeGeoSats)
        angleDegMask = (angleDeg <= 90)  # ограничение на область видимости соты
        
        # Расчет внешнего угла между сотой и низкоорбитальным спутником
        d = self.findDistance(cellNumber, coords = 'low')
        gammaDeg = self.findAngleDeg(d, self.altitudeSats)  
        
        cellsList_, geoSatsList_, satsList_, timeList_ = [], [], [], []
        for idx_geoSats in range(sum(angleDegMask)):  # Для каждого видимого геостационарного спутника
            gammaDegMask = ((gammaDeg > (angleDeg[angleDegMask][idx_geoSats] - self.angleDegLimit)) & \
                            (gammaDeg < (angleDeg[angleDegMask][idx_geoSats] + self.angleDegLimit)) & \
                            (gammaDeg <= 90))  # ограничение на область видимости соты
            
            # Ниже возвращаются индексы сот, геостац. спутников, КА и времени
            local_satsList    = ([i for i in range(len(gammaDegMask[:, epoch])) if gammaDegMask[i, epoch]])            
            local_cellsList   = [cellNumber for i in range(len(local_satsList))]
            local_geoSatsList = [idx_geoSats for i in range(len(local_satsList))]

            if len(local_satsList)!= 0: 
                cellsList_.extend(local_cellsList)
                geoSatsList_.extend(local_geoSatsList)
                satsList_.extend(local_satsList)
                
        self.parametersVisibilityFromCell = np.vstack([cellsList_, geoSatsList_, satsList_]).T     
        return cellsList_, geoSatsList_, satsList_
        
    def getVisibleSats(self, epoch):        
        # 64000 точки обрабатываются полтора часа
        for cellNumber in range(self.cellCount):
            if cellNumber%1000 == 0: print('Processing... {} / {}'.format(cellNumber, self.cellCount))
            cellsList_, geoSatsList_, satsList_ = self.getVisibleSatsFromCell(cellNumber, epoch)
            if len(satsList_) != 0:          
                self.cellsList.extend(cellsList_)
                self.geoSatsList.extend(geoSatsList_)                
                self.satsList.extend(satsList_)
        self.parametersVisibility= np.vstack([self.cellsList, self.geoSatsList, self.satsList]).T

    def writeToFile(self, name_outfile = None):
        if name_outfile is None:
            name_outfile=f'visibility_{self.angleDegLimit}deg.json'
        np.savetxt(name_outfile, self.parametersVisibility)
        
    def readFromFile(self, name_outfile = None):
        if name_outfile is None:
            name_outfile=f'visibility1_{self.angleDegLimit}deg.json'
        parameters = np.loadtxt(name_outfile, delimiter=' ')
        
        return parameters

