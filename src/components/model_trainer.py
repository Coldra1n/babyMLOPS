import os
import sys

sys.path.append('C:\\Users\\Nick\\Desktop\\23\\mlproject\\src') # unco
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from dataclasses import dataclass

from catboost import CatBoostRegressor
from sklearn.ensemble import (
    AdaBoostRegressor,
    GradientBoostingRegressor,
    RandomForestRegressor,
)
from sklearn.svm import SVR
from sklearn.linear_model import Ridge, Lasso
from sklearn.linear_model import ElasticNet
#from sklearn.linear_model import BayesianRidge
#from lightgbm import LGBMRegressor

from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor

from src.exception import CustomException
from src.logger import logging

from src.utils import save_object,evaluate_models

@dataclass
class ModelTrainerConfig:
    trained_model_file_path=os.path.join("artifacts","model.pkl")

class ModelTrainer:
    def __init__(self):
        self.model_trainer_config=ModelTrainerConfig()


    def initiate_model_trainer(self,train_array,test_array):
        try:
            logging.info("Split training and test input data")
            X_train,y_train,X_test,y_test=(
                train_array[:,:-1],
                train_array[:,-1],
                test_array[:,:-1],
                test_array[:,-1]
            )
            models = {
                "Random Forest": RandomForestRegressor(),
                "Decision Tree": DecisionTreeRegressor(),
                "Gradient Boosting": GradientBoostingRegressor(),
                "Linear Regression": LinearRegression(),
                "XGBRegressor": XGBRegressor(),
                "CatBoosting Regressor": CatBoostRegressor(verbose=False),
                "AdaBoost Regressor": AdaBoostRegressor(),
                #"LGBMRegressor": LGBMRegressor(),
                #"BayesianRidge": BayesianRidge(),
                "ElasticNet": ElasticNet(),
                "Ridge": Ridge(),
                "Lasso": Lasso(),
                "SVR": SVR(),

            }
            params={
                "Decision Tree": {
                    'criterion':['squared_error', 'friedman_mse', 'absolute_error', 'poisson'],
                    # 'splitter':['best','random'],
                    # 'max_features':['sqrt','log2'],
                },
                "Random Forest":{
                    # 'criterion':['squared_error', 'friedman_mse', 'absolute_error', 'poisson'],
                 
                    # 'max_features':['sqrt','log2',None],
                    'n_estimators': [8,16,32,64,128,256]
                },
                "Gradient Boosting":{
                    # 'loss':['squared_error', 'huber', 'absolute_error', 'quantile'],
                    'learning_rate':[.1,.01,.05,.001],
                    'subsample':[0.6,0.7,0.75,0.8,0.85,0.9],
                    # 'criterion':['squared_error', 'friedman_mse'],
                    # 'max_features':['auto','sqrt','log2'],
                    'n_estimators': [8,16,32,64,128,256]
                },
                "Linear Regression":{},
                "XGBRegressor":{
                    'learning_rate':[.1,.01,.05,.001],
                    'n_estimators': [8,16,32,64,128,256]
                },
                "CatBoosting Regressor":{
                    'depth': [6,8,10],
                    'learning_rate': [0.01, 0.05, 0.1],
                    'iterations': [30, 50, 100]
                },
                "AdaBoost Regressor":{
                    'learning_rate':[.1,.01,0.5,.001],
                    # 'loss':['linear','square','exponential'],
                    'n_estimators': [8,16,32,64,128,256]
                },
                #"LGBMRegressor": {
                    #'learning_rate': [0.01, 0.05, 0.1],
                    #'n_estimators': [8,16,32,64,128,256],
                    #'num_leaves': [31, 62],
                    #'subsample': [0.6, 0.7, 0.8, 0.9],
                    #'colsample_bytree': [0.6, 0.7, 0.8, 0.9]
                #},
                #" BayesianRidge": {
                 #   'alpha_1': [1e-6, 1e-5, 1e-4],
                  #  'alpha_2': [1e-6, 1e-5, 1e-4],
                   # 'lambda_1': [1e-6, 1e-5, 1e-4],
                    #'lambda_2': [1e-6, 1e-5, 1e-4]
                #},
                "ElasticNet": {
                    'alpha': [0.1, 0.5, 1, 1.5, 2],
                    'l1_ratio': [0.1, 0.3, 0.5, 0.7, 0.9]
                },
                 "Ridge": {
                    'alpha': [0.1, 0.5, 1, 1.5, 2]
                },
                 "Lasso": {
                    'alpha': [0.1, 0.5, 1, 1.5, 2]
                },
                 "SVR": {
                    'kernel': ['linear', 'poly', 'rbf', 'sigmoid'],
                    'C': [0.1, 1, 10, 100],
                    'epsilon': [0.01, 0.1, 0.5, 1, 2]
                }
                
            }

            model_report:dict=evaluate_models(X_train=X_train,y_train=y_train,X_test=X_test,y_test=y_test,
                                             models=models,param=params)
            
            ## To get best model score from dict
            best_model_score = max(sorted(model_report.values()))

            ## To get best model name from dict

            best_model_name = list(model_report.keys())[
                list(model_report.values()).index(best_model_score)
            ]
            best_model = models[best_model_name]

            if best_model_score<0.6:
                raise CustomException("No best model found")
            logging.info(f"Best found model on both training and testing dataset")

            save_object(
                file_path=self.model_trainer_config.trained_model_file_path,
                obj=best_model
            )

            predicted=best_model.predict(X_test)

            r2_square = r2_score(y_test, predicted)
            return best_model_name, r2_square
            



            
        except Exception as e:
            raise CustomException(e,sys)