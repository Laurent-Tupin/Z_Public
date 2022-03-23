# How to keep your computer active so your boss does not notice you are away

import time
import pyautogui
pyautogui.FAILSAFE = False


i_turn = 1
bl_loop = True
time.sleep(3)

while bl_loop:
    print(i_turn)
    time.sleep(3 * i_turn)
    
    # move mouse
    for i in range(30):
        o_pos = pyautogui.position()
        if o_pos.y > 1000:      pyautogui.moveTo(o_pos.x , 0)
        elif o_pos.x > 1000:    pyautogui.moveTo(0 , o_pos.y)
        else:                   pyautogui.moveTo(o_pos.x + 10, o_pos.y + 50)
        # print(o_pos.x, o_pos.y)
    
    # Press Shift
    pyautogui.press('shift')
    # print('------------------')
    
    # END
    if i_turn > 2:
        bl_loop = False
    i_turn = i_turn + 1
    