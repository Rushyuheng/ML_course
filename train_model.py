import pickle
import numpy as np
from os import path
from matplotlib import pyplot as plt

from sklearn.neighbors import KNeighborsClassifier
from sklearn.cluster import KMeans
from sklearn.tree import DecisionTreeClassifier

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
    Commands = []
    PlatformPos = []
    Obstacle = []
    hitblocker = []
    data = []
    log = pickle.load((open(filename, 'rb')))
    i = 0
    if(len(log) > 1200):
        for sceneInfo in log:
            if(sceneInfo["ball_speed"][1] > 0):
                Frames.append(sceneInfo["frame"])
                Balls.append([sceneInfo["ball"][0],sceneInfo["ball"][1]])
                Speed.append([sceneInfo["ball_speed"][0],sceneInfo["ball_speed"][1]])
                PlatformPos.append([sceneInfo["platform_1P"][0],sceneInfo["platform_2P"][0]])
                Obstacle.append(sceneInfo["blocker"][0])
                Commands.append(transformCommand(sceneInfo["command_1P"]))
                if(Speed[i - 1][1] * Speed[i][1] < 0 and Balls[i][1] != 80 and Balls[i][1] != 415 and Balls[i][0] != 0 and Balls[i][0] != 195):
                    hitblocker.append(1)
                elif(Speed[i - 1][0]* Speed[i][0] < 0 and Balls[i][0] != 0 and Balls[i][0] != 195 and Balls[i][1] != 80 and Balls[i][1] != 415):
                    hitblocker.append(2)
                else:
                    hitblocker.append(0)
                i = i + 1
        frame_ary = np.array(Frames)
        frame_ary = frame_ary.reshape((len(Frames), 1))
        commands_ary = np.array([Commands])
        commands_ary = commands_ary.reshape((len(Commands), 1))
        obstacle_ary = np.array(Obstacle)
        obstacle_ary = obstacle_ary.reshape((len(Obstacle), 1))
        hitblocker_ary = np.array(hitblocker)
        hitblocker_ary = hitblocker_ary.reshape((len(hitblocker), 1))
        data = np.hstack((frame_ary, Balls, Speed, PlatformPos,obstacle_ary,commands_ary,hitblocker_ary))

    return data


if __name__ == '__main__':
    start = 2200
    X = np.empty([1,8])
    Y = np.empty([1])
    for datanum in range(start,4120): #1-700 no slice 700-2194 will slice
        print(datanum)
        filename = path.join(path.dirname(__file__), 'dataset/dataset (') + str(datanum) + ').pickle'
        data = get_Data(filename)
        if(data != []):
            data = data[1::]
        
            mask = [1,2,3,4,5,6,7,9]#ball_x,ball_y,1P_x,2P_x,blocker_x
            target = 8 #command array
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
    platform_predict_clf = DecisionTreeClassifier(random_state=0).fit(x_train,y_train)        
    y_predict = platform_predict_clf.predict(x_test)
    print(y_predict)
    accuracy = metrics.accuracy_score(y_test, y_predict)
    print("Accuracy(正確率) ={:8.3f}%".format(accuracy*100))
    

    with open('save/clf_KMeans_BallAndDirection.pickle', 'wb') as f:
        pickle.dump(platform_predict_clf, f)
    
