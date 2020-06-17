"""
The template of the main script of the machine learning process
"""

import games.arkanoid.communication as comm
from games.arkanoid.communication import ( \
    SceneInfo, GameStatus, PlatformAction
)
import random

def ml_loop():
    """
    The main loop of the machine learning process

    This loop is run in a separate process, and communicates with the game process.

    Note that the game process won't wait for the ml process to generate the
    GameInstruction. It is possible that the frame of the GameInstruction
    is behind of the current frame in the game process. Try to decrease the fps
    to avoid this situation.
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here.
    ball_served = False

    # 2. Inform the game process that ml process is ready before start the loop.
    comm.ml_ready()

    randomcounter = 0
    counter = 0
    hight_limit = 250
    senserange = 5
    #line function
    slope = 0
    line_constant = 0
    predict_x = 0
    pre_ball_x = 0
    pre_ball_y = 0
    ball_x = 0
    ball_y = 0
    #random start
    random_start = random.randrange(100) + 20
    radom_serve = random.choice([True, False])
    stay_at = random.randrange(100) + 20
    # 3. Start an endless loop.
    while True:
        # 3.1. Receive the scene information sent from the game process.
        scene_info = comm.get_scene_info()

        # 3.2. If the game is over or passed, the game process will reset
        #      the scene and wait for ml process doing resetting job.
        if scene_info.status == GameStatus.GAME_OVER or \
            scene_info.status == GameStatus.GAME_PASS:
            # Do some stuff if needed
            ball_served = False
            random_start = random.randrange(100) + 20
            stay_at = random.randrange(100) + 20
            radom_serve = random.choice([True, False])
            # 3.2.1. Inform the game process that ml process is ready
            comm.ml_ready()
            continue

        # 3.3. Put the code here to handle the scene information
        platform_x = scene_info.platform[0] + 20
        counter = 0
        pre_ball_x = ball_x
        pre_ball_y = ball_y
        ball_x = scene_info.ball[0]
        ball_y = scene_info.ball[1]
        # 3.4. Send the instruction for this frame to the game process
        if not ball_served:
            if platform_x + senserange < random_start:
                    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
            elif platform_x - senserange > random_start:
                    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
            else:
                if radom_serve:
                    comm.send_instruction(scene_info.frame, PlatformAction.SERVE_TO_LEFT)
                    ball_served = True
                else:
                    comm.send_instruction(scene_info.frame, PlatformAction.SERVE_TO_RIGHT)
                    ball_served = True
        else:
            if(ball_y - pre_ball_y) > 0 and (ball_x - pre_ball_x) != 0:
                slope = (ball_y - pre_ball_y)/(ball_x - pre_ball_x)
                line_constant = ball_y - (slope * ball_x)
                predict_x = (400 - line_constant) / slope
                # if reflect
                while predict_x > 200 or predict_x < 0:
                    if predict_x > 200:
                        predict_x = 200 - (predict_x - 200)
                    elif predict_x < 0:
                        predict_x = -predict_x

            if ball_y > hight_limit and (ball_y - pre_ball_y) > 0: # while falling
                if platform_x  + senserange < predict_x:
                    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
                elif platform_x - senserange > predict_x:
                    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
                else:
                    comm.send_instruction(scene_info.frame, PlatformAction.NONE)
            else:
                if randomcounter > 60:
                    stay_at = random.randrange(100) + 20

                if platform_x  + senserange < stay_at:
                    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
                elif platform_x - senserange > stay_at:
                    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
                else:
                    comm.send_instruction(scene_info.frame, PlatformAction.NONE)
        counter = counter + 1
        randomcounter = randomcounter + 1