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
            cars_view = [100,100,100,100,100,100,100,100,100,100,100,100]
            speed_ahead = 100
            if self.car_pos[0] <= 35: # reach left bound
                cars_view[1] = -100 # can't go 
                cars_view[4] = -100
                cars_view[7] = -100
            elif self.car_pos[0] >= 595: # reach right bound
                cars_view[3] = -100
                cars_view[6] = -100
                cars_view[9] = -100

            for car in scene_info["cars_info"]:
                if car["id"] != self.player_no:
                    x = self.car_pos[0] - car["pos"][0] # x relative position
                    y = self.car_pos[1] - car["pos"][1] # y relative position
                    #middel lanes
                    if x <= 40 and x >= -40 :      
                        if y > 0 and y < 300:
                            cars_view[2] = car["velocity"] - self.car_vel
                            if y < 200:
                                cars_view[5] = car["velocity"] - self.car_vel
                        elif y < 0 and y > -200:
                            cars_view[8] = car["velocity"] - self.car_vel
                    #right lanes
                    if x > -100 and x <= -40 :
                        if y > 80 and y < 250:
                            cars_view[3] = car["velocity"] - self.car_vel
                        elif y < -80 and y > -200:
                            cars_view[9] = car["velocity"] - self.car_vel
                        elif y < 80 and y > -80:
                            if x >= -50 and x <= -40:
                                cars_view[11] = car["velocity"] - self.car_vel
                            else:
                                cars_view[6] = car["velocity"] - self.car_vel
                    #left lanes
                    if x < 100 and x >= 40:
                        if y > 80 and y < 250:
                            cars_view[1] = car["velocity"] - self.car_vel
                        elif y < -80 and y > -200:
                            cars_view[7] = car["velocity"] - self.car_vel
                        elif y < 80 and y > -80:
                            if x <= 50 and x >= 40:
                                cars_view[10] = car["velocity"] - self.car_vel
                            else:
                                cars_view[4] = car["velocity"] - self.car_vel
            if((self.car_pos[0] - 35) % 70 == 0 or (cars_view[5] != 100) or (cars_view[10] != 100) or (cars_view[11] != 100)):#update after change lane or emergency case
                self.command = move(cars_view)
            return self.command
            
        def move(cars_view): 
            feature = [self.car_vel,self.car_pos[0],self.car_pos[1]]
            for i in range(1,12):
                feature.append(cars_view[i])
            feature = np.array(feature)
            feature = feature.reshape((1,14))
            commandcode = self.clf.predict(feature)

            #decode
            if commandcode == 0 :
                return None
            elif commandcode == 1:
                return ["BRAKE"]
            elif commandcode == 2:
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

        return check_grid()

    def reset(self):
        """
        Reset the status
        """
        pass