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
       return 2
    elif 'LEFT' in str(command):
        return 1
    else:
        return 0
    pass


def get_ArkanoidData(filename):
    Frames = []
    Balls = []
    Commands = []
    PlatformPos = []
    log = pickle.load((open(filename, 'rb')))
    for sceneInfo in log:
        if sceneInfo.ball[1] > 250:
            Frames.append(sceneInfo.frame)
            Balls.append([sceneInfo.ball[0],sceneInfo.ball[1]])
            PlatformPos.append(sceneInfo.platform)
            Commands.append(transformCommand(sceneInfo.command))

    commands_ary = np.array([Commands])
    commands_ary = commands_ary.reshape((len(Commands), 1))
    frame_ary = np.array(Frames)
    frame_ary = frame_ary.reshape((len(Frames), 1))
    data = np.hstack((frame_ary, Balls, PlatformPos, commands_ary))
    return data


if __name__ == '__main__':  
    for datanum in range(1,850):
        filename = path.join(path.dirname(__file__), 'dataset/dataset (') + str(datanum) + ').pickle'
        data = get_ArkanoidData(filename)
        data = data[1::]
        Balls = data[:, 1:3]
        Balls_next = np.array(Balls[1:])
        vectors = Balls_next - Balls[:-1]
        direction=[]

        for i in range(len(data)-1):
            if(vectors[i,0]>0 and vectors[i,1]>0):
                direction.append(0) #向右上為0
            elif(vectors[i,0]>0 and vectors[i,1]<0):
                direction.append(1) #向右下為1
            elif(vectors[i,0]<0 and vectors[i,1]>0):
                direction.append(2) #向左上為2
            elif(vectors[i,0]<0 and vectors[i,1]<0):
                direction.append(3) #向左下為3
            else:
                direction.append(4) #not serve yet

        direction = np.array(direction)
        direction = direction.reshape((len(direction),1))
        vectors = np.array(vectors)
        vectors = vectors.reshape((len(vectors),2))
        data = np.hstack((data[1:,:], direction[:,:],vectors[:,:]))

        #mask = [3,6,7,8] #plat_x,direction,vector_x,vector_y
        mask = [1,2,3,6] #ball_x,ball_y,plat_x,direction
        if(datanum == 1):
            X = data[:, mask]
            Y = data[:, 5] #command array
            print (Y)
        else: 
            X = np.concatenate((X, data[:, mask]), axis=0)
            Y = np.concatenate((Y, data[:, 5]), axis=0)

    print(len(X))
    x_train , x_test,y_train,y_test = train_test_split(X,Y,test_size=0.2)
    platform_predict_clf = DecisionTreeClassifier(random_state=0).fit(x_train,y_train)        
    y_predict = platform_predict_clf.predict(x_test)
    print(y_predict)
    accuracy = metrics.accuracy_score(y_test, y_predict)
    print("Accuracy(正確率) ={:8.3f}%".format(accuracy*100))
    
    '''
    ax = plt.subplot(111, projection='3d')  
    ax.scatter(X[Y==0][:,0], X[Y==0][:,1], X[Y==0][:,3], c='#FF0000', alpha = 1)  
    ax.scatter(X[Y==1][:,0], X[Y==1][:,1], X[Y==1][:,3], c='#2828FF', alpha = 1)
    ax.scatter(X[Y==2][:,0], X[Y==2][:,1], X[Y==2][:,3], c='#007500', alpha = 1)
    
    plt.title("KNN Prediction")    
    ax.set_xlabel('Ball_x')
    ax.set_ylabel('Ball_y')
    ax.set_zlabel('Direction')
        
    plt.show()
    '''
    with open('save/clf_KMeans_BallAndDirection.pickle', 'wb') as f:
        pickle.dump(platform_predict_clf, f)

