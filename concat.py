import pandas as pd
import os

# a = pd.read_csv('position1.csv', header = [0,1,2])
# b = pd.read_csv('position2.csv', header = [0,1,2])
# c = pd.concat([a,b], sort = True)
# c.to_csv('position3.csv', na_rep = '100', index = False)

def read_first_file(file1,file2):
    data1 = pd.read_csv(file1, header = None)
    labels = {}
    for i in data1.shape[1]:
        if data1.loc[0][i] == 'Relative Position':
            break
        labels[data1.loc[2][i]] = {'ssid': data1.loc[0][i], 'freq': data1.loc[1][i]}
   # for i in len(labels)

if __name__=='__main__':
    files = [file for file in os.listdir() if file.split('.')[-1]=='csv']
    files_csv = [pd.read_csv(file, header=[0,1,2]) for file in files]
    c = pd.concat(files_csv, sort = True)
    c.to_csv('position3.csv', na_rep = '100', index = False)
    
