import time
import pyautogui as pag
pag.PAUSE = 0

if __name__ == '__main__':
    time.sleep(2)
    pag.press('f4')
    time.sleep(1)
    for _ in range(2000):
        # pag.press('q', presses=2)
        # pag.press('left', presses=4)
        pag.press('space')
