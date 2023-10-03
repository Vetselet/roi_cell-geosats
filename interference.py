import numpy as np
import pandas as pd
from itertools import chain


class Parameters(object):
    pass

Const = Parameters()
Const.earthRadius = 6378135    # Экваториальный радиус Земли [m]


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
        self.df_structure = pd.DataFrame(columns = ['cells', 'geosats', 'sats', 'time'])

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
    
    def findangleDeg(self, d, altitudeSats):
        ''' Расчет внешнего угла треугольника межд точками: центр Земли, 
        точка расположения соты на поверхности Земли, точка расположения спутника на орбите.
        psi -- угол между направлением на центр Земли и на спутник из соты'''
        
        psi = np.arccos((Const.earthRadius**2 + d**2 - altitudeSats**2)/   
                        (2 * Const.earthRadius * d))                       
        angleDeg = (np.pi - psi) * 180/np.pi 
        
        return angleDeg

    def getVisibleSatsFromCell(self, cellNumber):
        # Расчет внешнего угла между сотой и геостац. спутником
        D = self.findDistance(cellNumber, coords = 'geo')
        angleDeg = self.findangleDeg(D, self.altitudeGeoSats)
        angleDegMask = (angleDeg <= 90)  # ограничение на область видимости соты
        
        # Расчет внешнего угла между сотой и низкоорбитальным спутником
        d = self.findDistance(cellNumber, coords = 'low')
        gammaDeg = self.findangleDeg(d, self.altitudeSats)  
        
        cellsList_, geoSatsList_, satsList_, timeList_ = [], [], [], []
        for idx_geoSats in range(sum(angleDegMask)):  # Для каждого видимого геостационарного спутника
            gammaDegMask = ((gammaDeg > (angleDeg[angleDegMask][idx_geoSats] - self.angleDegLimit)) & \
                            (gammaDeg < (angleDeg[angleDegMask][idx_geoSats] + self.angleDegLimit)) & \
                            (gammaDeg <= 90))  # ограничение на область видимости соты
            
            # Ниже возвращаются индексы сот, геостац. спутников, КА и времени
            local_satsList    = ([i for i in range(len(gammaDegMask[:, 0])) if sum(gammaDegMask[i])>0 \
                               for j in range(sum(gammaDegMask[i]))])
            local_timeList    = ([[j for j in range(len(gammaDegMask[i, :])) if gammaDegMask[i, j]] \
                               for i in np.unique(local_satsList)])
            local_timeList    = list(chain(*local_timeList))
            local_cellsList   = [cellNumber for i in range(len(local_satsList))]
            local_geoSatsList = [idx_geoSats for i in range(len(local_satsList))]
            
            if len(local_satsList)!= 0: 
                cellsList_.extend(local_cellsList)
                geoSatsList_.extend(local_geoSatsList)
                satsList_.extend(local_satsList)
                timeList_.extend(local_timeList)
                
        return cellsList_, geoSatsList_, satsList_, timeList_
        
    def getVisibleSats(self):        
        cellsList, geoSatsList, satsList, timeList = [], [], [], []
        # 64000 точки обрабатываются полтора часа
        for cellNumber in range(self.cellCount):
            if cellNumber%1000 == 0: print('Processing... {} / {}'.format(cellNumber, self.cellCount))
            cellsList_, geoSatsList_, satsList_, timeList_ = self.getVisibleSatsFromCell(cellNumber)
            if len(satsList_)!= 0:          
                cellsList.extend(cellsList_)
                geoSatsList.extend(geoSatsList_)                
                satsList.extend(satsList_)
                timeList.extend(timeList_)

        self.df_structure[['cells', 'geosats', 'sats', 'time']] = list(zip(cellsList, geoSatsList, 
                                                                        satsList, timeList))
        return self.df_structure     
    
    
    def writeToFile(self, name_outfile = None):
        if name_outfile is None:
            name_outfile = f'visibility_{self.angleDegLimit}deg.json'
        (self.df_structure).to_csv(name_outfile, index = False)
        
    def readFromFile(self, name_outfile = None):
        if name_outfile is None:
            name_outfile = f'visibility1_{self.angleDegLimit}deg.json'
        df = pd.read_csv(name_outfile, sep = ', ', header = 0)
        
        return df





