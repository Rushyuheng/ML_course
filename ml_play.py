import random
import pickle
from os import path
import numpy as np

class MLPlay:
    def __init__(self, player):
        filename = path.join(path.dirname(__file__), 'save', 'clf.pickle')
        with open(filename, 'rb') as file:
            self.clf = pickle.load(file)
        self.player = player
        if self.player == "player1":
            self.player_no = 0
        elif self.player == "player2":
            self.player_no = 1
        elif self.player == "player3":
            self.player_no = 2
        elif self.player == "player4":
            self.player_no = 3
        self.car_vel = 0                            # speed initial
        self.car_pos = (0,0)                        # pos initial
        self.car_lane = self.car_pos[0] // 70       # lanes 0 ~ 8
        self.lanes = [35, 105, 175, 245, 315, 385, 455, 525, 595] # lanes center
        self.rand_dir_seq = 1
        self.command = []

        pass

    def update(self, scene_info):
        """
        9 grid relative position
        |    |    |    |
        |  1 |  2 |  3 |
        |    |  5 |    |
        |  4 10 c 11 6 |
        |    |    |    |
        |  7 |  8 |  9 |
        |    |    |    |       
        """
        def check_grid():
            detect_n = 8
            cars_view = np.zeros(shape=(2 * detect_n + 1,2 * detect_n + 1))
            coin_view = np.zeros(shape=(2 * detect_n + 1,2 * detect_n + 1))

            for car in scene_info["cars_info"]:
                if car["id"] != self.player_no:
                    x = self.car_pos[0] - car["pos"][0] # x relative position
                    y = self.car_pos[1] - car["pos"][1] # y relative position
                    if(x < detect_n * 100 and x > detect_n * -100) and(y < detect_n * 100 and y > detect_n * -100): # detect range is 1600 * 1600
                        index_x =  detect_n - (x // 100)
                        index_y =  detect_n - (y // 100)
                        cars_view[index_y][index_x] = car["velocity"]
            
            for coin in scene_info["coins"]:
                coin_x = self.car_pos[0] - coin[0] # relative position from car to coin
                coin_y = self.car_pos[1] - coin[1]
                if(coin_x < detect_n * 100 and coin_x > detect_n * -100) and(coin_y < detect_n * 100 and coin_y > detect_n * -100): # detect range is 1600 * 1600
                    index_cx =  detect_n - (coin_x // 100)
                    index_cy =  detect_n - (coin_y // 100)
                    coin_view[index_cy][index_cx] = 15

            return move(cars_view.flatten(),coin_view.flatten())
            
        def move(cars_view,coin_view): 
            feature = [self.car_vel,self.car_pos[0],self.car_pos[1]]

            for i in range(0,len(cars_view)):
                feature.append(cars_view[i])
            for i in range(0,len(coin_view)):
                feature.append(coin_view[i])

            feature_np = np.array(feature)
            feature_np = feature_np.reshape((1,len(feature)))
            commandcode = self.clf.predict(feature_np)

            #decode
            if commandcode == 0 or commandcode == 9:
                return None
            elif commandcode == 1:
                return ["BRAKE"]
            elif commandcode == 2 or commandcode == 10:
                return ["SPEED"]
            elif commandcode == 3:
                return ["MOVE_LEFT"]
            elif commandcode == 4:
                return ["MOVE_RIGHT"]
            elif commandcode == 5:
                return ["SPEED","MOVE_RIGHT"]
            elif commandcode == 6:
                return ["SPEED","MOVE_LEFT"]
            elif commandcode == 7:
                return ["BRAKE","MOVE_RIGHT"]
            elif commandcode == 8:
                return ["BRAKE","MOVE_LEFT"]
            
                        
                    
        if len(scene_info[self.player]) != 0:
            self.car_pos = scene_info[self.player]

        for car in scene_info["cars_info"]:
            if car["id"]==self.player_no:
                self.car_vel = car["velocity"]

        if scene_info["status"] != "ALIVE":
            return "RESET"
        self.car_lane = self.car_pos[0] // 70

        if(scene_info["frame"] < 100):
            return ["SPEED"]
        else:
            return check_grid()

    def reset(self):
        """
        Reset the status
        """
        pass