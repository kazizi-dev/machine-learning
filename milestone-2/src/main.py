import os
import pandas as pd
import numpy as np
import pickle
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt

def split_dataset(df):
    """
    encode string attributes to convert to numeric values using label and one hot encoder
    """
    
    # label encode date_confirmation attribute:
    df['date_confirmation'] = LabelEncoder().fit_transform(df['date_confirmation'].astype(str))

    y_train = df[['outcome']].values
    y_train = y_train.ravel()

    # one hot encode to prevent correlation
    enc = OneHotEncoder()
    x_train = df.drop(['outcome'], axis=1).copy()
    categorical_data = x_train[['sex', 'country', 'province']]   
    binary_data = enc.fit_transform(categorical_data).toarray()
    binary_labels = np.append(enc.categories_[0], enc.categories_[1])
    binary_labels = np.append(binary_labels, enc.categories_[2])

    encoded_df = pd.DataFrame(binary_data, columns=binary_labels)
    x_train = x_train.drop(['sex', 'country', 'province'], axis=1)

    # append converted data and numerical data
    x_train = x_train.join(encoded_df)
    x_train, x_test, y_train, y_test = train_test_split(x_train, y_train, test_size=0.2, random_state=0)
    return x_train, y_train, x_test, y_test


##############################
###### 2.2 Build models ######
##############################
def build_ada_boost_model(x_train, y_train, x_test, y_test):
    """
    build and save a boost model using AdaBoostClassifier from sklearn
    """
    model = AdaBoostClassifier(n_estimators=20, learning_rate=0.8, random_state=0)
    model = model.fit(x_train, y_train)
    
    path = '../models/ada_boost_model.pkl'
    pickle.dump(model, open(path, 'wb'))
    model = pickle.load(open(path, 'rb'))
    
    print('>> Ada Boost Model:')
    print(f'Train Accuracy: {model.score(x_train, y_train)}')
    print(f'Test Accuracy: {model.score(x_test, y_test)}')

    cross_validation_eval(model, x_train, y_train)
    print_classification_report(model, x_train, y_train, x_test, y_test)


def build_random_forest(x_train, y_train, x_test, y_test):
    """
    build random forst classifier using RandomForestClassifier from sklearn
    """

    model = RandomForestClassifier(n_estimators=10, random_state=0)
    model.fit(x_train, y_train)

    path = '../models/random_forst_model.pkl'
    with open(path, 'wb') as f:
        pickle.dump(model, f)

    with open(path, 'rb') as f:
        model = pickle.load(f)

    print('>> Random Forst Model:')
    print(f'Train Accuracy: {model.score(x_train, y_train)}')
    print(f'Test Accuracy: {model.score(x_test, y_test)}')

    cross_validation_eval(model, x_train, y_train)
    print_classification_report(model, x_train, y_train, x_test, y_test)


##############################
####### 2.3 Evaluation #######
##############################
def cross_validation_eval(model, x_train, y_train):
    """
    """
    scores = cross_val_score(model, x_train, y_train, scoring='accuracy', cv = 10)

    print(f'10-fold CV for the model: \n{scores}')
    print(f'CV Accuracy for the model: {scores.mean()*100}')


def print_classification_report(model, x_train, y_train, x_test, y_test):
    # stdsc = StandardScaler()

    # x_train_std = stdsc.fit_transform(x_train)
    print('--- Classification report for train data:')
    y_pred = model.predict(x_train)
    print(classification_report(y_train, y_pred))

    # x_test_std = stdsc.fit_transform(x_test)
    print('--- Classification report for test data:')
    y_pred = model.predict(x_test)
    print(classification_report(y_test, y_pred))


if __name__ == '__main__':
    print('--------------------------')
    import warnings
    warnings.filterwarnings("ignore")

    # setup path for main.py file
    os.chdir(os.getcwd())

    # read the processed data
    df = pd.read_csv('../data/cases_train_processed.csv')

    # split the dataset to train and test data
    print("...splitting and encoding data")
    x_train, y_train, x_test, y_test = split_dataset(df)

    print("...building ADABoost Model")
    build_ada_boost_model(x_train, y_train, x_test, y_test)
    print("...building Random Forest Model")
    build_random_forest(x_train, y_train, x_test, y_test)
