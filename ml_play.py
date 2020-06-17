import random
import pickle
from os import path
import numpy as np

class MLPlay:
    def __init__(self, player):
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
            grid = set()
            speed_ahead = 100
            if self.car_pos[0] <= 35: # reach left bound
                grid.add(1)
                grid.add(4)
                grid.add(7)
            elif self.car_pos[0] >= 595: # reach right bound
                grid.add(3)
                grid.add(6)
                grid.add(9)

            for car in scene_info["cars_info"]:
                if car["id"] != self.player_no:
                    x = self.car_pos[0] - car["pos"][0] # x relative position
                    y = self.car_pos[1] - car["pos"][1] # y relative position
                    #middel lanes
                    if x <= 40 and x >= -40 :      
                        if y > 0 and y < 300:
                            grid.add(2)
                            if y < 200:
                                speed_ahead = car["velocity"]
                                grid.add(5) 
                        elif y < 0 and y > -200:
                            grid.add(8)
                    #right lanes
                    if x > -100 and x <= -40 :
                        if y > 80 and y < 250:
                            grid.add(3)
                        elif y < -80 and y > -200:
                            grid.add(9)
                        elif y < 80 and y > -80:
                            if x >= -50 and x <= -40:
                                grid.add(11)
                            else:
                                grid.add(6)
                    #left lanes
                    if x < 100 and x >= 40:
                        if y > 80 and y < 250:
                            grid.add(1)
                        elif y < -80 and y > -200:
                            grid.add(7)
                        elif y < 80 and y > -80:
                            if x <= 50 and x >= 40:
                                grid.add(10)
                            else:
                                grid.add(4)
            if((self.car_pos[0] - 35) % 70 == 0 or (5 in grid) or (10 in grid) or (11 in grid)):#update after change lane or emergency case
                self.command = move(grid= grid, speed_ahead = speed_ahead)
            return self.command
            
        def move(grid, speed_ahead): 
            # if self.player_no == 0:
            #print(grid)
            if len(grid) == 0:
                return ["SPEED"]
            else:
                if (2 not in grid): # Check forward
                    #try to stay in middle lane
                    if (4 not in grid) and (1 not in grid and self.car_pos[0] >= 455): # turn left 
                        return ["SPEED", "MOVE_LEFT"]
                    elif (6 not in grid) and (3 not in grid and self.car_pos[0] <= 175): # turn right
                        return ["SPEED", "MOVE_RIGHT"]
                    
                    else:# Back to lane center
                        if self.car_pos[0] > self.lanes[self.car_lane]:
                            return ["SPEED", "MOVE_LEFT"]
                        elif self.car_pos[0] < self.lanes[self.car_lane]:
                            return ["SPEED", "MOVE_RIGHT"]
                        else :return ["SPEED"]

                else:
                    if (5 in grid): # NEED to BRAKE
                        
                        if((self.car_pos[0] - 35) % 70 == 0):#update after change lane
                            if(self.car_pos[0] >= 315):# keep in middle
                                self.rand_dir_seq = 0
                            else:
                                self.rand_dir_seq = 1
                        
                        if(self.rand_dir_seq == 0):#left > right
                            if (4 not in grid) and (1 not in grid): # turn left 
                                if self.car_vel < speed_ahead:
                                    return ["SPEED", "MOVE_LEFT"]
                                else:
                                    return ["BRAKE", "MOVE_LEFT"]
                            elif (6 not in grid) and (3 not in grid): # turn right
                                if self.car_vel < speed_ahead:
                                    return ["SPEED", "MOVE_RIGHT"]
                                else:
                                    return ["BRAKE", "MOVE_RIGHT"]
                            else : 
                                if self.car_vel < speed_ahead:  # BRAKE
                                    return ["SPEED"]
                                else:
                                    return ["BRAKE"]
                        else:
                            if (6 not in grid) and (3 not in grid): # turn right
                                if self.car_vel < speed_ahead:
                                    return ["SPEED", "MOVE_RIGHT"]
                                else:
                                    return ["BRAKE", "MOVE_RIGHT"]
                            elif (4 not in grid) and (1 not in grid): # turn left
                                if self.car_vel < speed_ahead:
                                    return ["SPEED", "MOVE_LEFT"]
                                else:
                                    return ["BRAKE", "MOVE_LEFT"]
                            else : 
                                if self.car_vel < speed_ahead:  # BRAKE
                                    return ["SPEED"]
                                else:
                                    return ["BRAKE"]

                    elif(10 in grid): # NEED avoid to right
                        if (6 not in grid) and (3 not in grid): # turn right and speed up
                            return ["SPEED", "MOVE_RIGHT"]
                        elif (3 not in grid):
                            return ["MOVE_RIGHT"]
                        else:
                            return ["BRAKE"]

                    elif(11 in grid): # NEED avoid to left
                        if (1 not in grid) and (4 not in grid): # turn left speed up
                            return ["SPEED", "MOVE_LEFT"]
                        elif (4 not in grid):
                            return ["MOVE_LEFT"]
                        else:
                            return ["BRAKE"]

                    else:            
                        if (self.car_pos[0] <= 35 ):
                            return ["SPEED", "MOVE_RIGHT"]
                        if(self.car_pos[0] >= 595):
                            return ["SPEED", "MOVE_LEFT"]
                        
                        if((self.car_pos[0] - 35) % 70 == 0):#update after change lane
                            if(self.car_pos[0] >= 315):# keep in middle
                                self.rand_dir_seq = 0
                            else:
                                self.rand_dir_seq = 1
                        
                        if(self.rand_dir_seq == 0):#left > right
                            if (1 not in grid) and (4 not in grid): # turn left and speedup
                                return ["SPEED", "MOVE_LEFT"]
                            elif (3 not in grid) and (6 not in grid): # turn right and speedup
                                return ["SPEED", "MOVE_RIGHT"]

                            elif (4 not in grid) : # turn left 
                                return ["MOVE_LEFT"]    
                            elif (6 not in grid) : # turn right
                                return ["MOVE_RIGHT"]
                        else:
                            if (3 not in grid) and (6 not in grid): # turn right and speedup
                                return ["SPEED", "MOVE_RIGHT"]
                            elif (1 not in grid) and (4 not in grid): # turn left and speedup
                                return ["SPEED", "MOVE_LEFT"]

                            elif (6 not in grid) : # turn right
                                return ["MOVE_RIGHT"]
                            elif (4 not in grid) : # turn left 
                                return ["MOVE_LEFT"]    
                        
                    
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