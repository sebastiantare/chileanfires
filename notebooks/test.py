# Load xgb json classification model and use it to predict some data
import xgboost as xgb
import pandas as pd
import numpy as np
import json
import os

# Load model
model = xgb.XGBClassifier()
model.load_model('xgb_model.json')

# Load data
new_data = pd.read_json('test_data.json')

print(new_data.head())

features = ['frp', 'track', 'daynight', 'confidence', 'latitude', 'longitude']

new_data = new_data[features]

if 'daynight' in new_data.columns:
    new_data['daynight'] = new_data['daynight'].apply(lambda x: 1 if x != 'D' else 0)
    new_data['daynight'] = new_data['daynight'].astype(int)
if 'confidence' in new_data.columns:
    new_data['confidence'] = new_data['confidence'].apply(lambda x: 0 if x == 'l' else 1 if x == 'n' else 2 if x == 'h' else 3)
    new_data['confidence'] = new_data['confidence'].astype(int)

# Predict
preds = model.predict(new_data)
# Preds to 0, 1s
preds = np.where(preds > 0.5, 1, 0)

new_data['ftype'] = preds

print(new_data.head())

#new_data.to_csv('test_data_result.csv', index=False)

print(preds)
