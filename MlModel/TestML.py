import tensorflow as tf
import keras
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import openpyxl
from random import random, randrange, randint, uniform
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import r2_score
from tensorflow.python.keras.utils import np_utils
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import GRU
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import RepeatVector
import time
from Repository import DataBaseRepository as repository

def generator(data, lookback, delay, min_index, max_index,
              shuffle=False, batch_size=128, step=1):
    if max_index is None:
        max_index = len(data) - delay - 1
    i = min_index + lookback
    while 1:
        # Перемешивание, в данном случае нам не требуется, так как нам дана ретроспектива данных, по которым определяем тренд
        if shuffle:
            rows = np.random.randint(
                min_index + lookback, max_index, size=batch_size)
        else:
            if i + batch_size >= max_index:
                i = min_index + lookback
            rows = np.arange(i, min(i + batch_size, max_index))
            i += len(rows)
        # Многомерный массив нулей
        samples = np.zeros((len(rows),
                            lookback // step,
                            data.shape[-1]))
        # Одномерный массив нулей
        targets = np.zeros((len(rows)))
        # Получаем индекс и само значение массива
        for j, row in enumerate(rows):
            indices = range(rows[j] - lookback, rows[j], step)
            # Выборки
            samples[j] = data[indices]
            # Целевые значения
            targets[j] = data[rows[j] + delay]
        # Генератор работает до того момента пока не закончатся все значения
        yield samples, targets

def univariate_data(dataset, start_index, end_index, history_size,
                      target_size, step, single_step=False):
  data = []
  labels = []

  start_index = start_index + history_size
  if end_index is None:
    end_index = len(dataset) - target_size

  for i in range(start_index, end_index):
    indices = range(i-history_size, i, step)
    data.append(dataset[indices])

    if single_step:
      labels.append(dataset[i+target_size])
    else:
      labels.append(dataset[i:i+target_size])

  return np.array(data), np.array(labels)

def create_time_steps(length):
  return list(range(-length, 0))


def training():
    # Загрузка набора данных (ИТС за первые 3 года)
    df_ITS_perday = pd.read_excel(r"E:\APR_ITS_PRED\ITS.xlsx")
    df_ITS_perday=df_ITS_perday[['ИТС']]
    # df_ITS_perday=df_ITS_perday.set_index('Data')
    # display(df_ITS_perday)
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaler.fit(df_ITS_perday)
    uni_data = scaler.transform(df_ITS_perday)
    univariate_past_history = 1094
    univariate_future_target = 0
    STEP = 1

    x_train_uni, y_train_uni = univariate_data(uni_data, 0, len(uni_data),
                                               univariate_past_history,
                                               univariate_future_target, STEP, single_step=True)

    BATCH_SIZE = 128

    train_univariate = tf.data.Dataset.from_tensor_slices((x_train_uni, y_train_uni))
    train_univariate = train_univariate.cache().batch(BATCH_SIZE).repeat()

    model = Sequential()

    model.add(LSTM(32, return_sequences=True, input_shape=x_train_uni.shape[-2:]))
    model.add(LSTM(16, activation='relu'))
    model.add(Dense(1))
    model.summary()

    model.compile(loss='mse',
                  optimizer='adam',
                  metrics='mae')

    for x, y in train_univariate.take(1):
        print(model.predict(x).shape)

    EVALUATION_INTERVAL = 10
    EPOCHS = 5

    multi_step_history = model.fit(train_univariate, epochs=EPOCHS, steps_per_epoch=EVALUATION_INTERVAL)

    ITS_predicted = x_train_uni[0].copy()
    k = 52

    for i in range(0, 3650):
        if k == 0:
            y_train_uni[0][0] = y_train_uni[0][0] - uniform(0.05, 0.15)
            k = randint(70, 150)
        k -= 1

        ITS_predicted = np.vstack((ITS_predicted, model.predict(x_train_uni)))
        x_train_uni[0] = ITS_predicted[i + 1:i+1095]

        train_univariate = tf.data.Dataset.from_tensor_slices((x_train_uni, y_train_uni))
        train_univariate = train_univariate.cache().batch(BATCH_SIZE).repeat()

        model.fit(train_univariate, epochs=EPOCHS, steps_per_epoch=EVALUATION_INTERVAL)

    ITS_predicted_real = scaler.inverse_transform(ITS_predicted)

    repository.saveToPredictedItsObraz(ITS_predicted_real)

    return ITS_predicted_real
