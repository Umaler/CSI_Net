import json
import numpy as np
import math

"""class CSIDataSet"""

# @title
class CSIDataSet(object):
    """docstring"""

    def __init__(self, filename, trueRange=0, visibleExamples=0):
        """Constructor"""
        self.filename = filename
        self.trueRange = trueRange
        self.countSubcarriers = 56
        self.data = []
        '''Открываем файл с датасетом'''
        with open(filename, "r") as read_file:
            self.data = json.load(read_file)

        ''' Выводим 3 строки датасета, для наглядности '''
        print("Examples from dataset")
        for i in range(visibleExamples):
          print(str(i) + ": " + str(self.data[i]))

        ''' Определяем количество данных '''
        self.packetCount = len(self.data)
        ''' Определяем количество записей '''
        self.frameCount = int(self.packetCount/self.countSubcarriers)
        print("All count: "+str(self.packetCount))
        print("Count by subcurriers: "+str(self.frameCount))


        '''Собираем массив numMas [0..113] для вывода графиков'''
        self.numMas = []
        for i in range(self.countSubcarriers):
            self.numMas.append(i)

        '''Получаем массивы
        # Разложение полученного массива на массивы:
        # Массив реальных частей realMas
        # Массив мнимых частей imagMas
        # Массив амплитуд amplMas
        # Массив фаз phaseMas
        # Массив разностей фаз diffPhaseMass
        '''

        self.phaseMasFF = []
        self.amplMasFF = []
        (self.phaseMasFF,self.amplMasFF)=self.getPhaseAndAmplitudeMass('ff')


        self.phaseMasFS = []
        self.amplMasFS = []
        (self.phaseMasFS,self.amplMasFS)=self.getPhaseAndAmplitudeMass('fs')


        self.phaseMasSS = []
        self.amplMasSS = []
        (self.phaseMasSS,self.amplMasSS)=self.getPhaseAndAmplitudeMass('ss')


        self.phaseMasSF = []
        self.amplMasSF = []
        (self.phaseMasSF,self.amplMasSF)=self.getPhaseAndAmplitudeMass('sf')

        '''
        # Исследование пределов разбросов
        '''
        # Объявляем массивы для хранения разниц минимальных и максимальных значений по записям
        self.phaseMasFFDif = []
        self.phaseMasFSDif = []
        self.phaseMasSFDif = []
        self.phaseMasSSDif = []

        # Объявляем массивы для хранения интегрированных разниц минимальных и максимальных значений по записям
        self.phaseMasFFDifInt = []
        self.phaseMasFSDifInt = []
        self.phaseMasSFDifInt = []
        self.phaseMasSSDifInt = []

        # Объявляем массивы для хранения фаз без переходов на соседние поднесущие
        self.phaseMasFFIntegrated = []
        self.phaseMasFSIntegrated = []
        self.phaseMasSFIntegrated = []
        self.phaseMasSSIntegrated = []

        (self.phaseMasFFDif, self.phaseMasFFDifInt,self.phaseMasFFIntegrated) = self.getDifference(self.phaseMasFF)
        (self.phaseMasFSDif, self.phaseMasFSDifInt,self.phaseMasFSIntegrated) = self.getDifference(self.phaseMasFS)
        (self.phaseMasSFDif, self.phaseMasSFDifInt,self.phaseMasSFIntegrated) = self.getDifference(self.phaseMasSF)
        (self.phaseMasSSDif, self.phaseMasSSDifInt,self.phaseMasSSIntegrated) = self.getDifference(self.phaseMasSS)



    # Функция извлечения данных о фазе и амплитуде
    # TxRx - указатель на принимающую и передающую антенны
    def getPhaseAndAmplitudeMass(self, TxRx):
          realMas = []
          imagMas = []
          phaseMas = []
          amplMas = []
          for i in range(self.frameCount): # По количеству пакетов по 56 значений
            realMasLine = []
            imagMasLine = []
            phaseMasLine = []
            amplMasLine = []
            for j in range(self.countSubcarriers):# По количеству поднесущих - 56
              realMasLine.append(self.data[i*self.countSubcarriers+j][TxRx+'r'])
              imagMasLine.append(self.data[i*self.countSubcarriers+j][TxRx+'i'])
              r=self.data[i*self.countSubcarriers+j][TxRx+'r']
              im=self.data[i*self.countSubcarriers+j][TxRx+'i']
              prev=self.data[i*self.countSubcarriers+j-1][TxRx+'r']
              ''' Расшифровка фазы '''
              if ((r == 0) and (im > 0)):
                  phase = 90                       #????????????????????????
              elif ((r == 0) and (im < 0)):
                  phase = -90
              elif ((r > 0) and (im == 0)):
                  phase = 0                     #????????????????????????
              elif ((r < 0) and (im == 0)):
                  phase = 0
              elif ((r == 0) and (im == 0)):
                  phase = 0
              else:
                  phase = np.arctan(im / r) * 180/math.pi
                  if (phase>180):
                    print("Found-!")
                    phase = phase - 360
                  elif (phase<-180):
                    phase = phase + 360
                    print("Found+!")

              amplitude = math.sqrt(self.data[i*self.countSubcarriers+j][TxRx+'r']*self.data[i*self.countSubcarriers+j][TxRx+'r']+self.data[i*self.countSubcarriers+j][TxRx+'i']*self.data[i*self.countSubcarriers+j][TxRx+'i'])
              ''' Конец расшифровки фазы '''
              phaseMasLine.append(phase)
              amplMasLine.append(amplitude)
            realMas.append(realMasLine)
            imagMas.append(imagMasLine)
            phaseMas.append(phaseMasLine)
            amplMas.append(amplMasLine)
          return phaseMas, amplMas


    def getDifference(self, mass):

        # 1. Находим разницы минимального и максимального значения по записям, чтобы определить где есть перенос на соседнюю понесущую.
        massMin = []
        massMax = []
        massDif = []

        for i in range(self.frameCount):
            massMin.append(min(mass[i]))
            massMax.append(max(mass[i]))
            massDif.append(max(mass[i])-min(mass[i]))
        #self.tempPhaseMasDif =  self.phaseMasDif # Для истории


        '''
        # Исследование пределов разбросов
        '''
        # 2. Дифференцируем разницы для того, чтобы явно вычленить переходы на соседнюю поднесущую.
        integratedPhaseMas = []

        # Интегрируем записи для поиска выбросов
        for i in range(self.frameCount):
          integratedPhaseMasLine = []
          for j in range(self.countSubcarriers):
            if j==0:
              integratedPhaseMasLine.append(0)
            else:
              integratedPhaseMasLine.append(mass[i][j]-mass[i][j-1])
          integratedPhaseMas.append(integratedPhaseMasLine);

        # 3. Ищем записи с выбросами более чем пороговое значение.
        # Ищем записи с выбросами
        p=75
        for i in range(self.frameCount):
            if max(integratedPhaseMas[i])>p or min(integratedPhaseMas[i])<-p:
              integratedPhaseMasLine = integratedPhaseMas[i]
              for j in range(self.countSubcarriers):
                if abs(integratedPhaseMasLine[j]) > p:
                  for k in range(self.countSubcarriers-j):
                    mass[i][k+j] = mass[i][k+j]-integratedPhaseMasLine[j]

        return massDif, integratedPhaseMas, mass
