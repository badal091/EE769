# -*- coding: utf-8 -*-
"""EE769_project.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1_nRVkqja7dvIjDncbUZjid4SxKrYYDbr
"""

!pip install yfinance
!pip install yahoofinancials
!pip install fastai
!pip install pmdarima

"""## Importing Basic Libraries"""

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import pandas as pd
import matplotlib.pyplot as pt
import yfinance as yf
from yahoofinancials import YahooFinancials
# %matplotlib inline
from fastai.tabular.all import add_datepart

"""##creating dataframe for stock and EDA"""

# stock for TATAMOTORS
stock = "TATAMOTORS.NS"

# accessing data
df = yf.download(stock, start='2010-01-01', end='2023-03-31', progress=False)
df_copy1 = df.copy()
df_copy1.tail()

df_copy1.shape

df_copy1 = df_copy1.reset_index()

# dropping features as they are highly correalted with the closing price
df_copy1 = df_copy1.drop(['Open', 'High', 'Low', 'Adj Close' ], axis=1)
df_copy1.shape

# checking for repeated rows
dates = df_copy1['Date']
df_copy1[dates.isin(dates[dates.duplicated()])].sort_index()

df_copy1 = df_copy1.drop_duplicates()

# # plotting price movement
df_copy1['Date'] = pd.to_datetime(df_copy1.Date, format='%Y-%m-%d')
df_copy1.set_index('Date', inplace=True)
 # plotting
pt.figure(figsize=(20,10))
pt.plot(df_copy1['Close'], label='Close Price movement')
pt.xlabel('Date')
pt.ylabel('Price')

"""##creating new features and understanding their nature"""

stock_price = df_copy1['Close'].to_frame()
stock_price['simple_MA_60'] = stock_price['Close'].rolling(60).mean()
stock_price['cumulative_MA'] = stock_price['Close'].expanding().mean()
stock_price['exponential_MA_60'] = stock_price['Close'].ewm(span=60).mean()
stock_price.dropna(inplace=True)

"""plots for Mean Averages for a roll back period for 60 days"""

ax = stock_price[['Close', 'simple_MA_60','cumulative_MA','exponential_MA_60']].plot(label='MA comparison', figsize=(20,10))
ax.set_xlabel('Date')
ax.set_ylabel('Price')

"""the exponential MA provides major thresholds and reverting points while simple and cumulative MA traces the price

adding features- 

*   Moving Averages (MA)
*   Bollinger Bands (region enclosing +- std about MA)
"""

df_copy1['simple_MA_60'] = df_copy1['Close'].rolling(60).mean()

df_copy1['BollingerBand_Up_60_1'] = df_copy1['Close'].rolling(60).mean() + df_copy1['Close'].rolling(60).std()
df_copy1['BollingerBand_Down_60_1'] = df_copy1['Close'].rolling(60).mean() - df_copy1['Close'].rolling(60).std()
df_copy1['BollingerBand_Up_60_2'] = df_copy1['Close'].rolling(60).mean() + 2*df_copy1['Close'].rolling(60).std()
df_copy1['BollingerBand_Down_60_2'] = df_copy1['Close'].rolling(60).mean() - 2*df_copy1['Close'].rolling(60).std()
df_copy1['BollingerBand_Up_20_2'] = df_copy1['Close'].rolling(20).mean() + 2*df_copy1['Close'].rolling(20).std()
df_copy1['BollingerBand_Down_20_2'] = df_copy1['Close'].rolling(20).mean() - 2*df_copy1['Close'].rolling(20).std()
df_copy1['BollingerBand_Up_20_1'] = df_copy1['Close'].rolling(20).mean() + df_copy1['Close'].rolling(20).std()
df_copy1['BollingerBand_Down_20_1'] = df_copy1['Close'].rolling(20).mean() - df_copy1['Close'].rolling(20).std()
df_copy1['BollingerBand_Up_10_1'] = df_copy1['Close'].rolling(10).mean() + df_copy1['Close'].rolling(10).std()
df_copy1['BollingerBand_Down_10_1'] = df_copy1['Close'].rolling(10).mean() - df_copy1['Close'].rolling(10).std()
df_copy1['BollingerBand_Up_10_2'] = df_copy1['Close'].rolling(10).mean() + 2*df_copy1['Close'].rolling(10).std()
df_copy1['BollingerBand_Down_10_2'] = df_copy1['Close'].rolling(10).mean() - 2*df_copy1['Close'].rolling(10).std()
df_copy1 = df_copy1.dropna()

"""Bollinger Bands Visualisation"""

ax = df_copy1[['Close', 'simple_MA_60', 'BollingerBand_Up_60_2', 'BollingerBand_Down_60_2']].plot(label='BollingerBands', figsize=(20,10))
ax.set_xlabel('Date')
ax.set_ylabel('Price')

display(df_copy1)

"""## Analyzing different Models"""

df_copy2 = df.copy()
data = df_copy2['Close'].to_frame()
for lag in [20,40,60]:
    shift = lag
    shifted = df_copy2.shift(shift)
    shifted.columns = [str.format("%s_shifted_by_%d" % (column ,shift)) for column in shifted.columns]
    data = pd.concat((data,shifted),axis=1)

data = data.dropna()
display(data)

data = data.reset_index()
data.shape

date = data['Date'].to_frame()

add_datepart(data, 'Date')
data.drop('Elapsed', axis=1, inplace=True)

display(data)

# Introducing features for Date
data['mon_fri'] = 0
data.loc[data['Dayofweek'] == 0 , 'mon_fri'] = 1
data.loc[data['Dayofweek'] == 4 , 'mon_fri'] = 1
data

new_data = pd.concat((data,date),axis=1)
new_data
display(new_data)

train_size = int(0.7*new_data.shape[0])
test_size = int(0.3*new_data.shape[0])
print(train_size)
print(test_size)

train_data = new_data[:train_size]
train_data = train_data.drop(['Date'], axis=1)
test_data = new_data[train_size:]
test_data = test_data.drop(['Date'], axis=1)
X_train = train_data.drop(['Close'], axis=1)
Y_train = train_data['Close']
X_test = test_data.drop(['Close'], axis = 1)
Y_test = test_data['Close']
print(X_train.shape)
print(Y_train.shape)
print(X_test.shape)
print(Y_test.shape)

"""##Linear Regression

"""

from sklearn.linear_model import LinearRegression
from sklearn.metrics import *
model = LinearRegression()
model.fit(X_train,Y_train)
price_prediction = model.predict(X_test)
rms=np.sqrt(np.mean(np.power((np.array(Y_test)-np.array(price_prediction)),2)))
print(rms)
# print(type(price_prediction))
# print(price_prediction)

# Evaluation metrices RMSE and MAE
import math
print("Train data RMSE: ", math.sqrt(mean_squared_error(Y_train,model.predict(X_train))))
print("Train data MSE: ", mean_squared_error(Y_train,model.predict(X_train)))
print("Train data MAE: ", mean_absolute_error(Y_train,model.predict(X_train)))
print("Test data RMSE: ", math.sqrt(mean_squared_error(Y_test,price_prediction)))
print("Test data MSE: ", mean_squared_error(Y_test,price_prediction))
print("Test data MAE: ", mean_absolute_error(Y_test,price_prediction))
print("Train data explained variance regression score:", explained_variance_score(Y_train, model.predict(X_train)))
print("Test data explained variance regression score:", explained_variance_score(Y_test, price_prediction))
print("Train data R2 score:", r2_score(Y_train, model.predict(X_train)))
print("Test data R2 score:", r2_score(Y_test, price_prediction))
print("Train data MGD: ", mean_gamma_deviance(Y_train, model.predict(X_train)))
print("Test data MGD: ", mean_gamma_deviance(Y_test, price_prediction))
print("Train data MPD: ", mean_poisson_deviance(Y_train, model.predict(X_train)))
print("Test data MPD: ", mean_poisson_deviance(Y_test, price_prediction))

new_data.set_index('Date', inplace=True)
test_data['Predictions'] = 0
test_data['Predictions'] = price_prediction

test_data.index = new_data[train_size:].index
train_data.index = new_data[:train_size].index

pt.figure(figsize=(20,10))
pt.plot(train_data['Close'])
pt.plot(test_data[['Close', 'Predictions']])
pt.xlabel('Date')
pt.ylabel('Price')
pt.legend(['Train_close', 'Actual_close', 'Predicted_close'])



"""##KNN"""

from sklearn import neighbors
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler(feature_range=(0, 1))

X_train_scaled = scaler.fit_transform(X_train)
X_train = pd.DataFrame(X_train_scaled)
X_test_scaled = scaler.fit_transform(X_test)
X_test = pd.DataFrame(X_test_scaled)

#using gridsearch to find the best parameter
params = {'n_neighbors':[4,5,6,7,8,9,10,11]}
knn = neighbors.KNeighborsRegressor()
model = GridSearchCV(knn, params, cv=5)

#fit the model and make predictions,
model.fit(X_train,Y_train)
print(model.best_params_)
price_prediction_KNN = model.predict(X_test)

rms_KNN=np.sqrt(np.mean(np.power((np.array(Y_test)-np.array(price_prediction_KNN)),2)))
rms

# Evaluation metrices RMSE and MAE
import math
print("Train data RMSE: ", math.sqrt(mean_squared_error(Y_train,model.predict(X_train))))
print("Train data MSE: ", mean_squared_error(Y_train,model.predict(X_train)))
print("Train data MAE: ", mean_absolute_error(Y_train,model.predict(X_train)))
print("Test data RMSE: ", math.sqrt(mean_squared_error(Y_test,price_prediction_KNN)))
print("Test data MSE: ", mean_squared_error(Y_test,price_prediction_KNN))
print("Test data MAE: ", mean_absolute_error(Y_test,price_prediction_KNN))
print("Train data explained variance regression score:", explained_variance_score(Y_train, model.predict(X_train)))
print("Test data explained variance regression score:", explained_variance_score(Y_test, price_prediction_KNN))
print("Train data R2 score:", r2_score(Y_train, model.predict(X_train)))
print("Test data R2 score:", r2_score(Y_test, price_prediction_KNN))
print("Train data MGD: ", mean_gamma_deviance(Y_train, model.predict(X_train)))
print("Test data MGD: ", mean_gamma_deviance(Y_test, price_prediction_KNN))
print("Train data MPD: ", mean_poisson_deviance(Y_train, model.predict(X_train)))
print("Test data MPD: ", mean_poisson_deviance(Y_test, price_prediction_KNN))

test_data['Predictions'] = 0
test_data['Predictions'] = price_prediction_KNN

test_data.index = new_data[train_size:].index
train_data.index = new_data[:train_size].index

pt.figure(figsize=(20,10))
pt.plot(train_data['Close'])
pt.plot(test_data[['Close', 'Predictions']])
pt.xlabel('Date')
pt.ylabel('Price')
pt.legend(['Train_close', 'Actual_close', 'Predicted_close'])



"""##Auto-Arima"""

from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error

df_copy3 = df.copy()
df_copy3 = df_copy3.reset_index()
df_copy3.tail()

train_data, test_data = df_copy3[0:int(len(df)*0.7)], df_copy3[int(len(df)*0.7):]
training_data = train_data['Close'].values
test_data = test_data['Close'].values
history = [x for x in training_data]
model_predictions = []
N_test_observations = len(test_data)
for time_point in range(N_test_observations):
    model = ARIMA(history, order=(4,1,0))
    model_fit = model.fit()
    output = model_fit.forecast()
    yhat = output[0]
    model_predictions.append(yhat)
    true_test_value = test_data[time_point]
    history.append(true_test_value)
MSE_error = mean_squared_error(test_data, model_predictions)
print('Testing Mean Squared Error is {}'.format(MSE_error))

test_data = df_copy3[int(len(df)*0.7):]
pt.figure(figsize=(20,10))
pt.plot(train_data['Date'], train_data['Close'])
pt.plot(test_data['Date'], test_data['Close'])
pt.plot(test_data['Date'],model_predictions)
pt.legend(['Train_close', 'Actual_close', 'Predicted_close'])
pt.xlabel('Date')
pt.ylabel('Price')

"""##LSTM

The LSTM model is Recurrent Neural Network which considers the data from past and works through a loop. Neural Network induces non-linearity.
"""

from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM

df_copy4 = df.copy()
data = df_copy4.sort_index(ascending=True, axis=0)

data=data.reset_index()
new_data = pd.DataFrame(index=range(0,len(df)),columns=['Date', 'Close'])
for i in range(0,len(data)):
    new_data['Date'][i] = data['Date'][i]
    new_data['Close'][i] = data['Close'][i]

new_data.index = new_data.Date
new_data.drop('Date', axis=1, inplace=True)
display(new_data)

train_size = int(0.7*new_data.shape[0])
test_size = int(0.3*new_data.shape[0])
print(train_size)
print(test_size)

dataset = new_data.values
dataset

train = dataset[0:train_size,:]
test = dataset[train_size:,:]

#converting dataset into x_train and y_train
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(dataset)

# Training intances are lagged by 100 days here thus providing the hitorical element
x_train, y_train = [], []
for i in range(100,len(train)):
    x_train.append(scaled_data[i-100:i,0])
    y_train.append(scaled_data[i,0])
x_train, y_train = np.array(x_train), np.array(y_train)

x_train = np.reshape(x_train, (x_train.shape[0],x_train.shape[1],1))

# create and fit the LSTM network
model = Sequential()
model.add(LSTM(units=100,activation = 'tanh', return_sequences=True, input_shape=(x_train.shape[1],1)))
model.add(LSTM(units=100))
model.add(Dense(1))

model.compile(loss='mean_squared_error', optimizer='adam')
model.fit(x_train, y_train, epochs=1, batch_size=1, verbose=2)

#predicting 246 values, using past 60 from the train data
inputs = new_data[len(new_data) - len(test) - 100:].values
inputs = inputs.reshape(-1,1)
inputs  = scaler.transform(inputs)

X_test = []
for i in range(100,inputs.shape[0]):
    X_test.append(inputs[i-100:i,0])
X_test = np.array(X_test)

X_test = np.reshape(X_test, (X_test.shape[0],X_test.shape[1],1))
closing_price = model.predict(X_test)
closing_price = scaler.inverse_transform(closing_price)

rms=np.sqrt(np.mean(np.power((test-closing_price),2)))
rms

import math
print("Train data RMSE: ", math.sqrt(mean_squared_error(y_train,model.predict(x_train))))
print("Train data MSE: ", mean_squared_error(y_train,model.predict(x_train)))
print("Test data MAE: ", mean_absolute_error(y_train,model.predict(x_train)))
print("Test data RMSE: ", math.sqrt(mean_squared_error(test, closing_price)))
print("Test data MSE: ", mean_squared_error(test, closing_price))
print("Test data MAE: ", mean_absolute_error(test, closing_price))
print("Train data explained variance regression score:", explained_variance_score(y_train, model.predict(x_train)))
print("Test data explained variance regression score:", explained_variance_score(test, closing_price))
print("Train data R2 score:", r2_score(y_train, model.predict(x_train)))
print("Test data R2 score:", r2_score(test, closing_price))
print("Train data MGD: ", mean_gamma_deviance(y_train, model.predict(x_train)))
print("Test data MGD: ", mean_gamma_deviance(test, closing_price))
print("Train data MPD: ", mean_poisson_deviance(y_train, model.predict(x_train)))
print("Test data MPD: ", mean_poisson_deviance(test, closing_price))

train = new_data[:train_size]
test = new_data[train_size:]
test_copy = test.copy()
test_copy['Prediction'] = closing_price.flatten()


pt.figure(figsize = (20,10))
pt.plot(train['Close'])
pt.plot(test_copy[['Close','Prediction']])
pt.legend(['Train_close', 'Actual_close', 'Predicted_close'])
pt.xlabel('Date')
pt.ylabel('Price')



"""##GRU"""

import pandas as pd
import numpy as np
import math
import datetime as dt
from sklearn.metrics import mean_squared_error, mean_absolute_error, explained_variance_score, r2_score 
from sklearn.metrics import mean_poisson_deviance, mean_gamma_deviance, accuracy_score
from sklearn.preprocessing import MinMaxScaler

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM, GRU

from itertools import cycle

# ! pip install plotly
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Import dataset
df_copy5 = df.copy()
df_copy5 = df_copy5.reset_index()
df_copy5.head()

# Checking null value
df_copy5.isnull().sum()

# Checking na value
df_copy5.isna().any()

df_copy5.dropna(inplace=True)
df_copy5.isna().any()

# Checking Data type of each column
print("Date column data type: ", type(df_copy5['Date'][0]))
print("Open column data type: ", type(df_copy5['Open'][0]))
print("Close column data type: ", type(df_copy5['Close'][0]))
print("High column data type: ", type(df_copy5['High'][0]))
print("Low column data type: ", type(df_copy5['Low'][0]))

# convert date field from string to Date format and make it index
df_copy5['Date'] = pd.to_datetime(df_copy5.Date)
df_copy5.head()

df_copy5.sort_values(by='Date', inplace=True)
df_copy5.head()

df_copy5.shape

print("Starting date: ",df_copy5.iloc[0][0])
print("Ending date: ", df_copy5.iloc[-1][0])
print("Duration: ", df_copy5.iloc[-1][0]-df_copy5.iloc[0][0])

closedf = df_copy5[['Date','Close']]
print("Shape of close dataframe:", closedf.shape)

df_copy5['Date'] = pd.to_datetime(df_copy5.Date, format='%Y-%m-%d')
df_copy5.set_index('Date', inplace=True)
 # plotting
pt.figure(figsize=(20,10))
pt.plot(df_copy5['Close'], label='Close Price movement')
pt.xlabel('Date')
pt.ylabel('Price')

close_stock = closedf.copy()
del closedf['Date']
scaler=MinMaxScaler(feature_range=(0,1))
closedf=scaler.fit_transform(np.array(closedf).reshape(-1,1))
print(closedf.shape)

training_size=int(len(closedf)*0.7)
test_size=len(closedf)-training_size
train_data,test_data=closedf[0:training_size,:],closedf[training_size:len(closedf),:1]
print("train_data: ", train_data.shape)
print("test_data: ", test_data.shape)

# convert an array of values into a dataset matrix
def create_dataset(dataset, time_step=1):
    dataX, dataY = [], []
    for i in range(len(dataset)-time_step-1):
        a = dataset[i:(i+time_step), 0]   ###i=0, 0,1,2,3-----99   100 
        dataX.append(a)
        dataY.append(dataset[i + time_step, 0])
    return np.array(dataX), np.array(dataY)

# reshape into X=t,t+1,t+2,t+3 and Y=t+4
time_step = 15
X_train, y_train = create_dataset(train_data, time_step)
X_test, y_test = create_dataset(test_data, time_step)

print("X_train: ", X_train.shape)
print("y_train: ", y_train.shape)
print("X_test: ", X_test.shape)
print("y_test", y_test.shape)

# reshape input to be [samples, time steps, features] which is required for LSTM
X_train =X_train.reshape(X_train.shape[0],X_train.shape[1] , 1)
X_test = X_test.reshape(X_test.shape[0],X_test.shape[1] , 1)

print("X_train: ", X_train.shape)
print("X_test: ", X_test.shape)

tf.keras.backend.clear_session()
model=Sequential()
model.add(GRU(32,return_sequences=True,input_shape=(time_step,1)))
model.add(GRU(32,return_sequences=True))
model.add(GRU(32,return_sequences=True))
model.add(GRU(32))
model.add(Dense(1))
model.compile(loss='mean_squared_error',optimizer='adam')

model.summary()

model.fit(X_train,y_train,validation_data=(X_test,y_test),epochs=20,batch_size=5,verbose=1)

### Lets Do the prediction and check performance metrics
train_predict=model.predict(X_train)
test_predict=model.predict(X_test)
train_predict.shape, test_predict.shape

# Transform back to original form

train_predict = scaler.inverse_transform(train_predict)
test_predict = scaler.inverse_transform(test_predict)
original_ytrain = scaler.inverse_transform(y_train.reshape(-1,1)) 
original_ytest = scaler.inverse_transform(y_test.reshape(-1,1))

# Evaluation metrices RMSE and MAE
print("Train data RMSE: ", math.sqrt(mean_squared_error(original_ytrain,train_predict)))
print("Train data MSE: ", mean_squared_error(original_ytrain,train_predict))
print("Train data MAE: ", mean_absolute_error(original_ytrain,train_predict))
print("Test data RMSE: ", math.sqrt(mean_squared_error(original_ytest,test_predict)))
print("Test data MSE: ", mean_squared_error(original_ytest,test_predict))
print("Test data MAE: ", mean_absolute_error(original_ytest,test_predict))
print("Train data explained variance regression score:", explained_variance_score(original_ytrain, train_predict))
print("Test data explained variance regression score:", explained_variance_score(original_ytest, test_predict))
print("Train data R2 score:", r2_score(original_ytrain, train_predict))
print("Test data R2 score:", r2_score(original_ytest, test_predict))
print("Train data MGD: ", mean_gamma_deviance(original_ytrain, train_predict))
print("Test data MGD: ", mean_gamma_deviance(original_ytest, test_predict))
print("Train data MPD: ", mean_poisson_deviance(original_ytrain, train_predict))
print("Test data MPD: ", mean_poisson_deviance(original_ytest, test_predict))

# shift train predictions for plotting

look_back=time_step
trainPredictPlot = np.empty_like(closedf)
trainPredictPlot[:, :] = np.nan
trainPredictPlot[look_back:len(train_predict)+look_back, :] = train_predict
print("Train predicted data: ", trainPredictPlot.shape)

# shift test predictions for plotting
testPredictPlot = np.empty_like(closedf)
testPredictPlot[:, :] = np.nan
testPredictPlot[len(train_predict)+(look_back*2)+1:len(closedf)-1, :] = test_predict
print("Test predicted data: ", testPredictPlot.shape)

names = cycle(['Original close price','Train predicted close price','Test predicted close price'])
plotdf = pd.DataFrame({'Date': close_stock['Date'],
                       'original_close': close_stock['Close'],
                      'train_predicted_close': trainPredictPlot.reshape(1,-1)[0].tolist(),
                      'test_predicted_close': testPredictPlot.reshape(1,-1)[0].tolist()})
pt.figure(figsize = (20,10))
pt.plot(plotdf['original_close'])
pt.plot(plotdf['train_predicted_close'])
pt.plot(plotdf['test_predicted_close'])
pt.legend(['Actual_close','Train_close', 'Predicted_close'])
pt.xlabel('Date')
pt.ylabel('Price')

"""##GRU + Hybrid"""

# reshape input to be [samples, time steps, features] which is required for LSTM
X_train =X_train.reshape(X_train.shape[0],X_train.shape[1] , 1)
X_test = X_test.reshape(X_test.shape[0],X_test.shape[1] , 1)

print("X_train: ", X_train.shape)
print("X_test: ", X_test.shape)

model.summary()

model.fit(X_train,y_train,validation_data=(X_test,y_test),epochs=20,batch_size=5,verbose=1)

### Lets Do the prediction and check performance metrics
train_predict=model.predict(X_train)
test_predict=model.predict(X_test)
train_predict.shape, test_predict.shape

# Transform back to original form

train_predict = scaler.inverse_transform(train_predict)
test_predict = scaler.inverse_transform(test_predict)
original_ytrain = scaler.inverse_transform(y_train.reshape(-1,1)) 
original_ytest = scaler.inverse_transform(y_test.reshape(-1,1))

# Evaluation metrices RMSE and MAE
print("Train data RMSE: ", math.sqrt(mean_squared_error(original_ytrain,train_predict)))
print("Train data MSE: ", mean_squared_error(original_ytrain,train_predict))
print("Train data MAE: ", mean_absolute_error(original_ytrain,train_predict))
print("Test data RMSE: ", math.sqrt(mean_squared_error(original_ytest,test_predict)))
print("Test data MSE: ", mean_squared_error(original_ytest,test_predict))
print("Test data MAE: ", mean_absolute_error(original_ytest,test_predict))
print("Train data explained variance regression score:", explained_variance_score(original_ytrain, train_predict))
print("Test data explained variance regression score:", explained_variance_score(original_ytest, test_predict))
print("Train data R2 score:", r2_score(original_ytrain, train_predict))
print("Test data R2 score:", r2_score(original_ytest, test_predict))
print("Train data MGD: ", mean_gamma_deviance(original_ytrain, train_predict))
print("Test data MGD: ", mean_gamma_deviance(original_ytest, test_predict))
print("Train data MPD: ", mean_poisson_deviance(original_ytrain, train_predict))
print("Test data MPD: ", mean_poisson_deviance(original_ytest, test_predict))

# shift train predictions for plotting

look_back=time_step
trainPredictPlot = np.empty_like(closedf)
trainPredictPlot[:, :] = np.nan
trainPredictPlot[look_back:len(train_predict)+look_back, :] = train_predict
print("Train predicted data: ", trainPredictPlot.shape)

# shift test predictions for plotting
testPredictPlot = np.empty_like(closedf)
testPredictPlot[:, :] = np.nan
testPredictPlot[len(train_predict)+(look_back*2)+1:len(closedf)-1, :] = test_predict
print("Test predicted data: ", testPredictPlot.shape)

names = cycle(['Original close price','Train predicted close price','Test predicted close price'])

plotdf = pd.DataFrame({'Date': close_stock['Date'],
                       'original_close': close_stock['Close'],
                      'train_predicted_close': trainPredictPlot.reshape(1,-1)[0].tolist(),
                      'test_predicted_close': testPredictPlot.reshape(1,-1)[0].tolist()})

pt.figure(figsize = (20,10))

pt.plot(plotdf['original_close'])
pt.plot(plotdf['train_predicted_close'])
pt.plot(plotdf['test_predicted_close'])
pt.legend(['Actual_close','Train_close', 'Predicted_close'])
pt.xlabel('Date')
pt.ylabel('Price')