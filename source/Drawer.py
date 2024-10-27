
import json
import time
from matplotlib import interactive
from matplotlib import pyplot as plt
from matplotlib.widgets import Slider
import math
import numpy as np
from tensorflow import keras
from keras.layers import Dense, Flatten, Dropout, concatenate
from keras.models import Sequential
from keras.utils import plot_model
from pathlib import Path
from CSIDataSet import CSIDataSet


plt.ion()

net_to_heatmap = {
  0: (1, 0),
  1: (2, 1),
  2: (1, 1),
  3: (0, 1),
  4: (2, 2),
  5: (1, 2),
  6: (0, 2),
  7: (2, 3),
  8: (1, 3),
  9: (0, 3),
  10:(1, 4)
}

class model(object):
    def __init__(self, model_arch_path, model_weights_path):
      with open(model_arch_path, "r") as json_file:
        loaded_model=keras.models.model_from_json(json_file.read())
        loaded_model.load_weights(model_weights_path)
        loaded_model.compile(loss="categorical_crossentropy", optimizer="Adam")
        self.model = loaded_model

    def predict(self, x_arr):
      y = self.model.predict(np.expand_dims(x_arr, axis=0), verbose=0)
      return y

net = model('CSI_DataSet/mnist_model.json', 'CSI_DataSet/model.weights.h5')

DST1 = CSIDataSet ("CSI_DataSet/plase12.dat.json")



movePhaseFF = np.asarray(DST1.phaseMasFFIntegrated)
moveAmplFF = np.asarray(DST1.amplMasFF)
movePhaseFS = np.asarray(DST1.phaseMasFSIntegrated)
moveAmplFS = np.asarray(DST1.amplMasFS)
movePhaseSF = np.asarray(DST1.phaseMasSFIntegrated)
moveAmplSF = np.asarray(DST1.amplMasSF)
movePhaseSS = np.asarray(DST1.phaseMasSSIntegrated)
moveAmplSS = np.asarray(DST1.amplMasSS)

moveFullAmplMass = concatenate([moveAmplFF, moveAmplFS, moveAmplSF, moveAmplSS])
moveFullPhaseMass = concatenate([movePhaseFF, movePhaseFS, movePhaseSF, movePhaseSS])
moveFullAmplAndPhaseMass=concatenate([moveFullPhaseMass,moveFullAmplMass])

window_position = 0


def getHeatmapArr():
  global window_position
  orig_arr = net.predict(moveFullAmplAndPhaseMass[window_position])
  heatmap_arr = np.reshape(orig_arr, (1, 11))
  return heatmap_arr

def getTrueHeatmapArr():
  return [[0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0]]

fig, ax = plt.subplots()
plt.subplot(2, 2, 1)
heatmap = plt.imshow(getHeatmapArr(), cmap='hot', interpolation='nearest')
plt.title("Predicted values")

plt.subplot(2, 2, 2)
true_heatmap = plt.imshow(getTrueHeatmapArr(), cmap='hot', interpolation='nearest')
plt.title("True values")

plt.subplots_adjust(left=0, bottom=0.25)

ax_window_position = plt.subplot(2, 2, (3, 4))
window_slider = Slider(
    ax=ax_window_position,
    label='Window start',
    valmin=0,
    valmax=len(moveFullAmplAndPhaseMass) - 1,
    valinit=window_position,
)

def update(val):
  global window_position
  window_position = int(val)
  heatmap.set_data(getHeatmapArr())
  true_heatmap.set_data(getTrueHeatmapArr())

window_slider.on_changed(update)
plt.show(block=True)
