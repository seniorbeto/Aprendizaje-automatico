import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV, RandomizedSearchCV  
from sklearn.ensemble import RandomForestRegressor
from sklearn import metrics
import numpy as np
import time


# definicion de constantes usadas a lo largo del proyecto
SEED = 100472050 # la semilla debe ser el NIA de uno de los integrantes
wind_ava = pd.read_csv("data/wind_ava.csv", index_col=0)
aux = wind_ava[wind_ava.columns[wind_ava.columns.str.endswith('13')]]
# añadir la columna energy a wind_ava
aux.insert(0, "energy", wind_ava["energy"])     
wind_ava = aux
print(wind_ava.head())

# Primero, dividiremos los datos en entrenamiento y test
X = wind_ava.drop(columns='energy')
y = wind_ava['energy']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=SEED)
# como el anterior mejor es 'n_estimators': 150, 'min_samples_split': 10, 'min_samples_leaf': 2, 'max_depth': 30, 'bootstrap': True
# vamos a ampliar el rango de valores para n_estimators y max_depth

# iteracion 2: n_estimators': 250, 'min_samples_split': 10, 'min_samples_leaf': 2, 'max_depth': None, 'bootstrap': True
param_dist = {
    'n_estimators': [250, 300, 350],
    'max_depth': [None],
    'min_samples_split': [8 ,10, 12],
    'min_samples_leaf': [1, 2, 3],
    'bootstrap': [True]
}

# hacer una busqueda aleatoria
random_search = RandomizedSearchCV(RandomForestRegressor(), param_distributions=param_dist, n_iter=100, cv=5, scoring='neg_root_mean_squared_error', n_jobs=-1, verbose=4)
print("Iniciando búsqueda de hiperparámetros...")
t1 = time.time()
random_search.fit(X_train, y_train)
t2 = time.time()
print("Búsqueda de hiperparámetros finalizada.")
dt_rf_cv = t2 - t1

print("Mejores hiperparámetros encontrados:")
print(random_search.best_params_)
print("Mejor RMSE encontrado (train):")
print(-random_search.best_score_)
print("Tiempo de entrenamiento:")
print(dt_rf_cv)

# Calcular métricas
best_model = random_search.best_estimator_

# Predecir los valores de test
y_test_pred = best_model.predict(X_test)

# Calcular métricas
rmse_rf_cv = np.sqrt(metrics.root_mean_squared_error(y_test, y_test_pred))
r2_rf_cv = best_model.score(X_test, y_test)

print(f"RMSE: {rmse_rf_cv}")
print(f"R2: {r2_rf_cv}")

# exportar el modelo
import pickle
filename = 'models/random_forest_model.pkl'
with open(filename, 'wb') as file:
    pickle.dump(best_model, file)
