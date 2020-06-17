import pickle
import numpy as np
import random
from os import path
from matplotlib import pyplot as plt

from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVR
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from sklearn.model_selection import train_test_split
from sklearn import metrics

def transformCommand(command):
    if 'RIGHT' in str(command):
       return 1
    elif 'LEFT' in str(command):
        return 2
    else:
        return 0
    pass


def get_Data(filename):
    Frames = []
    Balls = []
    Speed = []
    catch = []
    PlatformPos = []
    Obstacle = []
    hitblocker = []
    data = []

    log = pickle.load((open(filename, 'rb')))
    i = 0
    memory = random.randrange(0,200)
    if(len(log) > 1200):
        for sceneInfo in reversed(log):
            if(sceneInfo["ball"][1] <= 415 and (sceneInfo["ball_speed"][1] > 0 or sceneInfo["ball"][1] == 415)):
                Frames.append(sceneInfo["frame"])
                Balls.append([sceneInfo["ball"][0],sceneInfo["ball"][1]])
                Speed.append([sceneInfo["ball_speed"][0],sceneInfo["ball_speed"][1]])
                PlatformPos.append([sceneInfo["platform_1P"][0],sceneInfo["platform_2P"][0]])
                Obstacle.append(sceneInfo["blocker"][0])
                if(sceneInfo["ball"][1] == 415):
                    memory = sceneInfo["ball"][0]
                catch.append(memory)
                if(Speed[i - 1][1] * Speed[i][1] < 0 and Balls[i][1] != 80 and Balls[i][1] != 415 and Balls[i][0] != 0 and Balls[i][0] != 195):
                    hitblocker.append(1)
                elif(Speed[i - 1][0]* Speed[i][0] < 0 and Balls[i][0] != 0 and Balls[i][0] != 195 and Balls[i][1] != 80 and Balls[i][1] != 415):
                    hitblocker.append(2)
                else:
                    hitblocker.append(0)
                i = i + 1
        frame_ary = np.array(Frames)
        frame_ary = frame_ary.reshape((len(Frames), 1))
        catch_ary = np.array([catch])
        catch_ary = catch_ary.reshape((len(catch), 1))
        obstacle_ary = np.array(Obstacle)
        obstacle_ary = obstacle_ary.reshape((len(Obstacle), 1))
        hitblocker_ary = np.array(hitblocker)
        hitblocker_ary = hitblocker_ary.reshape((len(hitblocker), 1))
        data = np.hstack((frame_ary, Balls, Speed, PlatformPos,obstacle_ary,catch_ary,hitblocker_ary))

    return data


if __name__ == '__main__':
    start = 2200
    X = np.empty([1,8])
    Y = np.empty([1])
    for datanum in range(start,2600): #1-700 no slice 700-2194 will slice
        filename = path.join(path.dirname(__file__), 'dataset/dataset (') + str(datanum) + ').pickle'
        data = get_Data(filename)
        if (type(data).__module__ == np.__name__):
            data = data[1::]
        
            mask = [1,2,3,4,5,6,7,9]#ball_x,ball_y,1P_x,2P_x,blocker_x
            target = 8 #catch array
            if(datanum == start):
                X = data[:, mask]
                Y = data[:, target] 
            else: 
                X = np.concatenate((X, data[:, mask]), axis=0)
                Y = np.concatenate((Y, data[:, target]), axis=0)
    X = X[1:,:]
    Y = Y[1:]
    print(Y)
    print(len(X))
    x_train , x_test,y_train,y_test = train_test_split(X,Y,test_size=0.2)
    platform_predict_clf = SVR(C=1.0, epsilon=0.2).fit(x_train,y_train,sample_weight=None)        
    accuracy = platform_predict_clf.score(x_train,y_train,sample_weight=None)
    print("Accuracy(正確率) ={:8.3f}%".format(accuracy*100))
    

    with open('save/clf_reg.pickle', 'wb') as f:
        pickle.dump(platform_predict_clf, f)
    
