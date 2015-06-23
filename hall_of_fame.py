import json
import re
import glob
import bleach
import time
import requests
from collections import defaultdict
from datetime import datetime
from template import *

start_time = datetime.now()

fns = glob.glob('./data/final_game_data_*.json')
data = defaultdict(list)


f = open('player_data_cache.txt')
cache_lines = f.read().split('\n')
f.close()
cache = [json.loads(line) for line in cache_lines if line]
cache_dict = dict([(int(row['response']['players'][0]['steamid']), row) for row in cache])

cache_file= open('player_data_cache.txt', 'a')


dt = datetime.now()

def get_ordinal(n):
    if 4 <= n <= 20 or 4 <= n%10 <= 9 or n%10 == 0:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][n % 10 - 1]

    return '{}{}'.format(n, suffix)

def get_player_data(steamid):
    if steamid in cache_dict:
        return cache_dict[steamid]['response']['players'][0]

    url = 'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=74124D319E4FDDEC264929A8B12AFF04&steamids={}'.format(steamid)

    for try_i in range(10):
        try:
            r = requests.get(url)
            response = r.json()['response']
            player = response['players'][0]
            cache_file.write(r.text.encode('utf-8').replace('\n','')+'\n')
            return response['players'][0]
        except Exception as e:
            print e, url, r.text
            time.sleep(2)

    return None

content = ''
content += '<h2>Thanks</h2>'
content += '<p>I would to thank Valve for setting up this incredibly fun event, MSG2015 Steam Group Staff for sleeping 2 hours a day on average, tirelessly working on coordinating over 20000 people as well as everyone who played with us, or against us. Thanks guys.</p>'
content += 'Rooms 46550 (4th) and 47686 (9th) have about 200-300 people missing each, because I was not tracking them at the moment they hit 100M. If anyone has the data, please message me on Steam and I will add it.'

content += '<h2>MSG2015 Steam Group Staff & Guests</h2>'
content += '<div class="row">'

staff_content = []
staff = open('./staff.txt').read().split('\n')[:-1]
for player_id in staff:
    player_data = get_player_data(int(player_id)+76561197960265728)
    player_name = player_data['personaname']
    player_name = bleach.clean(player_name)
    player_name = player_name.replace('<', '&lt').replace('&', '&and;')
    player_name = re.sub('\[.*\]', '', player_name).strip()
    staff_content.append((player_name, '<div class="col-md-3" style="padding-bottom: 5px"><a href="{}"><img src="{}" height="32" width="32"> {}</a></div>'.format(player_data['profileurl'], player_data['avatarmedium'], player_name.encode('utf-8'))))

staff_content.sort(key=lambda x: x[0].lower())
content += '\n'.join([line[1] for line in staff_content])

content += '</div>'


win_games_list = list(win_games.items())
win_games_list.sort(key=lambda x: x[1])


i = 1
for game_id, game_info in win_games_list:
    j = 0
    try:
        f = open('./data/final_game_data_{}.json'.format(game_id))
        snapshot = json.load(f)
        f.close()
    except IOError:
        continue

    players = snapshot['players']

    room_content = '<div class="row"><h2>Room {} <small>({}, {})</small></h2>'.format(game_id, get_ordinal(i), game_info[1])

    for player in players:
        player_name = bleach.clean(player['player_name'])
        player_name = player_name.replace('<', '&lt').replace('&', '&and;')
        player_data = get_player_data(player['id'])
        if player_data is None:
            raise Exception('a')
        if i <= 3:
            room_content += '<a href="{0}"><img src="{1}" height="32" width="32" title="{2}" alt="{2}"></a>'.format(player_data['profileurl'], player_data['avatar'], player_name.encode('utf-8'))
        else:
            room_content += '<div class="col-md-3" style="padding-bottom: 5px"><a href="{}">{}</a></div>'.format(player_data['profileurl'], player_name.encode('utf-8'))

        j += 1
        if j % 100 == 0:
            print i, j

    room_content += "</div>"
    content += room_content
    i += 1


context = {
    'tbody': '',
    'thead': '',
    'tfoot': '',
    'title': '<img src="http://steamcommunity-a.akamaihd.net/public/images/badges/23_towerattack/wormhole.png"> <span style="vertical-align: middle">Hall Of Fame</span>',

    'container-padding': '50',
    'date': '<abbr class="timeago" title="{0}-{2}">{1}</abbr>'.format(dt.isoformat(), dt, server_timezone),
    'extra_content': '',
    'run_time': str((datetime.now() - start_time).seconds),
    'long': True,
    'graphs': content,
    'nav': '',
    }

render_template('hall_of_fame.html', context)
