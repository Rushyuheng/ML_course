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
    if(str(type(command)) == "<class 'NoneType'>"):
        return 0
    elif(len(command) == 1):
        if 'RIGHT' in str(command):
           return 4
        elif 'LEFT' in str(command):
            return 3
        elif 'SPEED' in str(command):
            return 2
        elif 'BRAKE' in str(command):
            return 1
    elif(len(command) == 2):
        if('SPEED' in str(command[0])):
            if 'RIGHT' in str(command[1]): #[SPEED,RIGHT]
               return 5
            elif 'LEFT' in str(command[1]): #[SPEED,LEFT]
                return 6
        elif ('BRAKE' in str(command[0])):
            if 'RIGHT' in str(command[1]): #[BRAKE,RIGHT]
               return 7
            elif 'LEFT' in str(command[1]): #[BRAKE,LEFT]
                return 8           

def get_Data(filename):
    log = pickle.load((open(filename, 'rb')))
    i = 0
    info = log["scene_info"]
    allcommand = log["command"]
    command = []
    allview = []
    allpos =[]
    car_vel = []
    cars_view = [100,100,100,100,100,100,100,100,100,100,100,100]

    #decided best car
    if len(info[-1]["player1"]) > 0:
        best = 0
        bestcarname = "player1"
    elif len(info[-1]["player2"]) > 0:
        best = 1
        bestcarname = "player2"
    elif len(info[-1]["player3"]) > 0:
        best = 2
        bestcarname = "player3"
    elif len(info[-1]["player4"]) > 0:
        best = 3
        bestcarname = "player4"

    for i in range(1,len(info)):
        if(info[i]["status"] == "ALIVE"):
            command.append(transformCommand(allcommand[i][best]))
            #initalize
            car_pos = info[i][bestcarname]
            cars_view = [100,100,100,100,100,100,100,100,100,100,100,100] #all clear

            #feature array
            if car_pos[0] <= 35: # reach left bound
                cars_view[1] = -100 # can't go 
                cars_view[4] = -100
                cars_view[7] = -100
            elif car_pos[0] >= 595: # reach right bound
                cars_view[3] = -100
                cars_view[6] = -100
                cars_view[9] = -100

            for car in info[i]["cars_info"]:
                if car["id"] == best:
                    best_v = car["velocity"]
                if car["id"] != best:
                    x = car_pos[0] - car["pos"][0] # x relative position
                    y = car_pos[1] - car["pos"][1] # y relative position
                    #middel lanes
                    if x <= 40 and x >= -40 :      
                        if y > 0 and y < 300:
                            cars_view[2] = car["velocity"] - best_v
                            if y < 200:
                                cars_view[5] = car["velocity"] - best_v
                        elif y < 0 and y > -200:
                            cars_view[8] = car["velocity"] - best_v
                    #right lanes
                    if x > -100 and x <= -40 :
                        if y > 80 and y < 250:
                            cars_view[3] = car["velocity"] - best_v
                        elif y < -80 and y > -200:
                            cars_view[9] = car["velocity"] - best_v
                        elif y < 80 and y > -80:
                            if x >= -50 and x <= -40:
                                cars_view[11] = car["velocity"] - best_v
                            else:
                                cars_view[6] = car["velocity"] - best_v
                    #left lanes
                    if x < 100 and x >= 40:
                        if y > 80 and y < 250:
                            cars_view[1] = car["velocity"] - best_v
                        elif y < -80 and y > -200:
                            cars_view[7] = car["velocity"] - best_v
                        elif y < 80 and y > -80:
                            if x <= 50 and x >= 40:
                                cars_view[10] = car["velocity"] - best_v
                            else:
                                cars_view[4] = car["velocity"] - best_v
            allview.append(cars_view[1:]) # 0 has no usage 
            allpos.append(car_pos)
            car_vel.append(best_v)

    carvel_ary = np.array(car_vel)
    carvel_ary = carvel_ary.reshape((len(car_vel), 1))        
    command_ary = np.array(command)
    command_ary = command_ary.reshape((len(command), 1))
    data = np.hstack((carvel_ary,allpos,allview,command_ary))
    return data


if __name__ == '__main__':
    start = 1
    end = 160
    X = np.empty([1,1])
    Y = np.empty([1])
    for datanum in range(start,end):
        print(datanum)
        filename = path.join(path.dirname(__file__), 'dataset/dataset (') + str(datanum) + ').pickle'
        data = get_Data(filename)
        mask = [0,1,2,3,4,5,6,7,8,9,10,11,12,13] # features
        target = 14 #command array
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
    

    with open('save/clf.pickle', 'wb') as f:
        pickle.dump(platform_predict_clf, f)

