import pickle
import numpy as np
from os import path
from matplotlib import pyplot as plt
import random

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

def oversample(skew,counter,supplement,data):
    i = 0
    while i < (skew - 1) * counter:
        data = np.insert(data, random.randrange(1,len(data)), supplement[random.randrange(0,len(supplement)),:], 0)
        i = i + 1
    return data

def get_Data(filename):
    Frames = []
    Balls = []
    Speed = []
    PlatformPos = []
    Obstacle = []
    hitblocker = []
    log = pickle.load((open(filename, 'rb')))
    for sceneInfo in log:
        Frames.append(sceneInfo["frame"]) #data[0]
        Balls.append([sceneInfo["ball"][0],sceneInfo["ball"][1]]) #data[1],data[2]
        Speed.append([sceneInfo["ball_speed"][0],sceneInfo["ball_speed"][1]]) #data[3],data[4]
        PlatformPos.append([sceneInfo["platform_1P"][0],sceneInfo["platform_2P"][0]]) #data[5],data[6]
        Obstacle.append(sceneInfo["blocker"][0]) #data[7]
        hitblocker.append(0) #data[8] 
    frame_ary = np.array(Frames)
    frame_ary = frame_ary.reshape((len(Frames), 1))
    obstacle_ary = np.array(Obstacle)
    obstacle_ary = obstacle_ary.reshape((len(Obstacle), 1))
    hitblocker_ary = np.array(hitblocker)
    hitblocker_ary = hitblocker_ary.reshape((len(hitblocker), 1))
    data = np.hstack((frame_ary, Balls, Speed, PlatformPos,obstacle_ary,hitblocker_ary))

    i = 0
    hitface = 0
    hitside = 0
    hitplatform = 0
    newdata = []
    hitfacelist = []
    hitsidelist = []
    while i + 1 < len(hitblocker_ary):
        if(data[i,2] == 80 or data[i,2] + 5 == 420 and data[i + 1,2] > 80 and data[i + 1,2] + 5 < 420):
            # hit platform and did not fall through
            hitplatform = hitplatform + 1
            reachmiddle = 0
            while (data[i + reachmiddle,2] < 230 and data[i + reachmiddle,4] > 0) or (data[i + reachmiddle,2] > 270 and data[i + reachmiddle,4] < 0):
                reachmiddle = reachmiddle + 1
            j = 0
            while j < 5:
                if(data[i + reachmiddle + j - 1,4] * data[i + reachmiddle + j,4] < 0):
                    data[i - 1,8] = 1 #hitblocker face and predict one frame before hit platform
                    hitfacelist.append(data[i - 1,:])
                    hitface = hitface + 1
                    break
                elif(data[i + reachmiddle + j - 1,3] * data[i + reachmiddle + j,3] < 0 and data[i + reachmiddle + j,1] != 0 and data[i + reachmiddle + j,1] != 200):
                    data[i - 1,8] = 2 #hitblocker side
                    hitsidelist.append(data[i - 1,:])
                    hitside = hitside + 1
                    break
                j = j + 1

            newdata.append(data[i - 1,:])  

        i = i + 1
    newdata_ary = np.array(newdata)
    newdata_ary = newdata_ary.reshape((len(newdata), 9))
    if(hitface > 0):
        hitface_ary = np.array(hitfacelist)
        hitface_ary = hitface_ary.reshape((len(hitface_ary), 9))
        hitfaceskew = (hitplatform - hitface - hitside) // hitface
        newdata_ary = oversample(hitfaceskew,hitface,hitface_ary,newdata_ary)

    if(hitside > 0):
        hitside_ary = np.array(hitsidelist)
        hitside_ary = hitside_ary.reshape((len(hitside_ary), 9))
        hitsideskew = (hitplatform - hitface - hitside) // hitside
        newdata_ary = oversample(hitsideskew,hitside,hitside_ary,newdata_ary)

    return newdata_ary[1:,:]


if __name__ == '__main__':
    start = 1
    for datanum in range(start,4120):
        print(datanum)
        filename = path.join(path.dirname(__file__), 'dataset/dataset (') + str(datanum) + ').pickle'
        data = get_Data(filename)

    
        mask = [1,2,3,4,5,6,7]#ball_x,ball_y,ball_speed_x,ball_speed_y,1P_x,2P_x,blocker_x
        target = 8 #hitblocker or not
        if(datanum == start):
            X = data[:, mask]
            Y = data[:, target] 
        else: 
            X = np.concatenate((X, data[:, mask]), axis=0)
            Y = np.concatenate((Y, data[:, target]), axis=0)
    print(Y)
    print(len(X))
    x_train , x_test,y_train,y_test = train_test_split(X,Y,test_size=0.2)
    platform_predict_clf = DecisionTreeClassifier(random_state=0).fit(x_train,y_train)        
    y_predict = platform_predict_clf.predict(x_test)
    print(y_predict)
    accuracy = metrics.accuracy_score(y_test, y_predict)
    print("Accuracy(正確率) ={:8.3f}%".format(accuracy*100))
    

    with open('save/clf_hitblocker.pickle', 'wb') as f:
        pickle.dump(platform_predict_clf, f)

    
