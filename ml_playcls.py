"""
The template of the script for the machine learning process in game pingpong
"""

# Import the necessary modules and classes
from mlgame.communication import ml as comm
import random
import pickle
from os import path
import numpy as np

def ml_loop(side: str):
    """
    The main loop for the machine learning process
    The `side` parameter can be used for switch the code for either of both sides,
    so you can write the code for both sides in the same script. Such as:
    ```python
    if side == "1P":
        ml_loop_for_1P()
    else:
        ml_loop_for_2P()
    ```
    @param side The side which this script is executed for. Either "1P" or "2P".
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here
    ball_served = False
    filename = path.join(path.dirname(__file__), 'save', 'clf_KMeans_BallAndDirection.pickle')
    with open(filename, 'rb') as file:
        clf = pickle.load(file)
    filename = path.join(path.dirname(__file__), 'save', 'clf_hitblocker.pickle')
    with open(filename, 'rb') as file:
        clf_hitblocker = pickle.load(file)

    def sliceball():
        return random.randrange(0,3) # random slice

    def checkdir(cur,pre):
        if(cur > pre):
            return "RIGHT"
        else:
            return "LEFT"

    def boundaryreflect(pred,leftbound,rightbound):
            while pred > rightbound or pred < leftbound:
                if pred > rightbound:
                    pred = rightbound - (pred - rightbound)
                elif pred < leftbound:
                    pred = -pred
            return pred
    def hit_blocker(player):
        '''
        if blockdir == "RIGHT":
            direction = 3
        else:
            direction = -3
        reaction_time = 155 / abs(scene_info["ball_speed"][1])

        i = 0
        y_range = 20 // abs(scene_info["ball_speed"][1]) # chance to hit side of blocker
        while i < y_range:
            reaction_time = reaction_time + i
            blocker_pred = scene_info["blocker"][0] + direction * reaction_time
            blocker_pred = boundaryreflect(blocker_pred,0,180)
            ball_pred = scene_info["ball"][0] + (scene_info["ball_speed"][0] * (reaction_time))
            ball_pred = boundaryreflect(ball_pred,0,200)

            if(ball_pred <= blocker_pred + 30 and ball_pred + 5 >= blocker_pred):
                print("hit blocker")
                return True
            i = i + 1
        '''

        feature = []
        feature.append(scene_info["ball"][0])
        feature.append(scene_info["ball"][1])
        feature.append(scene_info["ball_speed"][0])
        feature.append(scene_info["ball_speed"][1])
        feature.append(scene_info["platform_1P"][0])
        feature.append(scene_info["platform_2P"][0])
        feature.append(scene_info["blocker"][0])
        feature = np.array(feature)
        feature = feature.reshape((-1,7))
        predhitblock = clf_hitblocker.predict(feature)
        if(predhitblock == 1):
            return True
        elif(predhitblock == 2):
            return True


    def move_to(player, pred) :
    #parameter
    #move platform to predicted position to catch ball 
        pred = (pred // 5) * 5
        if player == '1P':
            if scene_info["platform_1P"][0] + 20 < pred : 
                return 1 # goes right
            elif scene_info["platform_1P"][0] + 20  > pred : 
                return 2  # goes left
            else : 
                return 0 # None
        else :
            if scene_info["platform_2P"][0] + 20  < pred : return 1 # goes right
            elif scene_info["platform_2P"][0] + 20  > pred : return 2 # goes left
            else : return 0 # None

    def ml_loop_for_1P(stay_at_P1,speed_pre_x,speed_pre_y):
        if(scene_info["platform_1P"][1] - (scene_info["ball"][1] + 5 ) < abs(scene_info["ball_speed"][1])):
            if(hit_blocker('1P')):
                return sliceball()
        
        if scene_info["ball_speed"][1] > 0 : # 球正在向下 # ball goes down
            if(scene_info["frame"]) < 1200:
            
                x = ( scene_info["platform_1P"][1] - scene_info["ball"][1] ) / scene_info["ball_speed"][1] # 幾個frame以後會需要接  # x means how many frames before catch the ball
                pred = scene_info["ball"][0] + (scene_info["ball_speed"][0]*x)  # 預測最終位置 # pred means predict ball landing site 
                #bound = pred // 200 # Determine if it is beyond the boundary
                pred = boundaryreflect(pred,0,200)
                return move_to(player = '1P',pred = pred)
            else:
                feature = []
                feature.append(scene_info["ball"][0])
                feature.append(scene_info["ball"][1])
                feature.append(scene_info["ball_speed"][0])
                feature.append(scene_info["ball_speed"][1])
                feature.append(scene_info["platform_1P"][0])
                feature.append(scene_info["platform_2P"][0])
                feature.append(scene_info["blocker"][0])
                #detect hit blocker
                if(speed_pre_y * scene_info["ball_speed"][1] < 0 and scene_info["ball"][1] != 80 and scene_info["ball"][1] != 415 and scene_info["ball"][0] != 0 and scene_info["ball"][0] != 195):
                    feature.append(1)
                elif(speed_pre_x* scene_info["ball_speed"][0] < 0 and scene_info["ball"][0] != 0 and scene_info["ball"][0] != 195 and scene_info["ball"][1] != 80 and scene_info["ball"][1] != 415):
                    feature.append(2)
                else:
                    feature.append(0)
                feature = np.array(feature)
                feature = feature.reshape((-1,8))
                return clf.predict(feature)

        elif scene_info["ball_speed"][1] < 0: # 球正在向上 # ball goes up
            return move_to(player = '1P',pred = 100)



    def ml_loop_for_2P(stay_at_P2):  # as same as 1P
        if(scene_info["ball"][1] - (scene_info["platform_2P"][1] + 30) <= abs(scene_info["ball_speed"][1]) ):
            #if(hit_blocker('2P')):
            return sliceball()


        if scene_info["ball_speed"][1] > 0 : 
            return move_to(player = '2P',pred = stay_at_P2)
        else:
            x = ( scene_info["ball"][1] - (scene_info["platform_2P"][1] + 30)) / -scene_info["ball_speed"][1] 
            pred = scene_info["ball"][0] + (scene_info["ball_speed"][0]*x) 
            #bound = pred // 200 
            pred = boundaryreflect(pred,0,200)
            return move_to(player = '2P',pred = pred)

    # 2. Inform the game process that ml process is ready
    comm.ml_ready()

    #random start
    random_start = random.randrange(50,150)
    radom_serve = random.choice([True, False])
    stay_at_P1 = random.randrange(50,150)
    stay_at_P2 = random.randrange(50,150)
    speed_pre_x = 7
    speed_pre_y = 7

    # 3. Start an endless loop
    while True:
        # 3.1. Receive the scene information sent from the game process
        scene_info = comm.recv_from_game()

        # 3.2. If either of two sides wins the game, do the updating or
        #      resetting stuff and inform the game process when the ml process
        #      is ready.
        if scene_info["status"] != "GAME_ALIVE":
            # Do some updating or resetting stuff
            ball_served = False
            random_start = random.randrange(50,150)
            radom_serve = random.choice([True, False])
            stay_at_P1 = random.randrange(50,150)
            stay_at_P2 = random.randrange(50,150)

            # 3.2.1 Inform the game process that
            #       the ml process is ready for the next round
            comm.ml_ready()
            continue

        # 3.3 Put the code here to handle the scene information
        # 3.4 Send the instruction for this frame to the game process
        if not ball_served:

            if radom_serve:
                comm.send_to_game({"frame": scene_info["frame"], "command": "SERVE_TO_LEFT"})
                ball_served = True
            else:
                comm.send_to_game({"frame": scene_info["frame"], "command": "SERVE_TO_RIGHT"})
                ball_served = True
        else:

            if side == "1P":
                command = ml_loop_for_1P(stay_at_P1,speed_pre_x,speed_pre_y)
            else:
                command = ml_loop_for_2P(stay_at_P2,)

            if command == 0:
                comm.send_to_game({"frame": scene_info["frame"], "command": "NONE"})
            elif command == 1:
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
            elif command == 2:
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})
            speed_pre_x = scene_info["ball_speed"][0] #update speed
            speed_pre_y = scene_info["ball_speed"][1]
