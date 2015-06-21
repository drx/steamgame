from config import *
import time
import subprocess
from threading import Timer
import sys

games = set()

def popen(game_id, delay):
    while True:
        subprocess.Popen(["python", "roomranking.py", str(game_id)])
        time.sleep(delay)

def popen_leaderboard():
    while True:
        subprocess.Popen(["python", "leaderboard.py"])
        time.sleep(10)


t = Timer(0, popen_leaderboard)
t.start()

i = 0
no_delay = False
while True:
    for game_id, game_name in get_game_list():
        if game_id in games:
            continue

        games.add(game_id)
        delay = 5*60

        start_delay = i*20
        if '-f' in sys.argv:
            start_delay = i*2

        if no_delay:
            start_delay = 1
            print 'New room: {}'.format(game_id)

        t = Timer(start_delay, popen, [game_id, delay])
        t.start()

        i += 1
    time.sleep(10)
    no_delay = True
