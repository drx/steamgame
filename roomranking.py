import requests
import time
import bleach
import sys
import json
from datetime import datetime, timedelta
from config import *
from collections import defaultdict
from template import *

start_time = datetime.now()

try:
    game_id = int(sys.argv[1])
except IndexError:
    game_id = get_game_list()[0][0]

try:
    game_name = get_game_dict()[game_id]
except KeyError:
    game_name = ''

try:
    n_max = int(sys.argv[2])
except IndexError:
    n_max = 1500

most_recent_update = {'dt': datetime(2000, 1, 1, 0, 0)}

def get_player_names(game_id):
    url = 'http://steamapi-a.akamaihd.net/ITowerAttackMiniGameService/GetPlayerNames/v0001/?input_json=%7B%22gameid%22:%22{0}%22,%22accountids%22:[]%7D'.format(game_id)
    r = requests.get(url)
    player_names = []
    for row in r.json()['response']['names']:
        steamid64 = row['accountid']+76561197960265728
        player_names.append((steamid64, row['name']))

    return player_names

def get_player_data(game_id, steam_id):
    success = False
    for try_i in range(5):
        try:
            url = 'http://steamapi-a.akamaihd.net/ITowerAttackMiniGameService/GetPlayerData/v0001/?gameid={0}&steamid={1}&include_tech_tree=1'.format(game_id, steam_id)
            r = requests.get(url)
            response = r.json()['response']
            tech_tree = response['tech_tree']
            success = True
            break
        except:
            #print 'get_player_data fail #{}'.format(try_i+1), r.text
            time.sleep(2)
    if not success:
        raise Exception('welp')
    last_updated = datetime.now()

    most_recent_update['dt'] = max(last_updated, most_recent_update['dt'])

    return response


tbody = []

player_names = get_player_names(game_id)


players = []
i = 0
n_players = 0
for player_id, player_name in reversed(player_names):
    try:
        player_data = get_player_data(game_id, player_id)
    except:
        continue
    player = {'player_name': player_name}

    for k in ('damage_per_click', 'crit_percentage', 'boss_loot_drop_percentage', 'max_hp', 'dps'):
        value = player_data['tech_tree'][k]
        if k in ('max_hp', 'dps', 'damage_per_click'):
            value = int(value)
        elif k in ('crit_percentage', 'boss_loot_drop_percentage'):
            value = int(value*100)
        player[k] = value

    try:
        player['gold'] = int(player_data['player_data']['gold'])
    except KeyError:
        player['gold'] = 0 
    player['wormholes'] = 0
    player['like_new'] = 0
    player['feeling_lucky'] = 0
    try:
        for item in player_data['tech_tree']['ability_items']:
            if item['ability'] == 25:
                player['feeling_lucky'] = item['quantity']
            if item['ability'] == 26:
                player['wormholes'] = item['quantity']
            if item['ability'] == 27:
                player['like_new'] = item['quantity']
    except KeyError:
        pass

    player['elemental'] = 0
    for upgrade in player_data['tech_tree']['upgrades']:
        upgrade_id = upgrade['upgrade']
        if upgrade_id in (2, 7, 10, 22, 25, 28, 31, 34):
            player['upgrade_{}'.format(upgrade_id)] = upgrade['level']

        elif upgrade_id in (3, 4, 5, 6):
            player['elemental'] = max(player['elemental'], upgrade['level'])

    crit = min(1.0, player_data['tech_tree']['crit_percentage'])
    crit = float(max(0.0, crit))
    dpc = player['damage_per_click']
    crit_dpc = dpc*player_data['tech_tree']['damage_multiplier_crit']

    edpc = dpc*(1-crit) + crit_dpc*crit
    edps = edpc*20 + player['dps']

    player['edps'] = int(edps)
    player['id'] = player_id


    players.append(player)

    n_players += 1
    if n_players % 100 == 0:
        print >>sys.stderr, '{} ({}): {}'.format(game_id, game_name, n_players)

    if n_players >= n_max: break

players.sort(key=lambda x: x['edps'], reverse=True)

thead = generate_thead('game')
tfoot = []

i = 1
sums = defaultdict(int)
for player in players:
    player['i'] = i
    tbody.append('<tr>')
    #tbody.append('<td>{}</td>'.format(i))

    for k in ks:
        if k.startswith('game_') or k in ('updated', 'completed'):
            continue
        if k == 'player_name':
            name = bleach.clean(player[k])
            name = name.replace('<', '&lt').replace('&', '&and;')
            tbody.append('<td style="text-align: left">{}</td>'.format(name.encode('utf-8')))
        elif k in ('damage_per_click', 'edps', 'dps'):
            tbody.append('<td data-sort-value="{}">{}</td>'.format(player[k], show_int(player[k])))
        elif k in ('gold', 'max_hp'):
            tbody.append('<td data-sort-value="{}">{}</td>'.format(player[k], show_unit_int(player[k])))
        else:
            tbody.append('<td>{}</td>'.format(player.get(k, 0)))

        if k != 'player_name':
            sums[k] += player.get(k, 0)
    tbody.append('<td>{}</td>'.format(player['id']))
    tbody.append('</tr>')
    i += 1

dt = datetime.now()

game_totals = {
    'game_id': game_id,
    'n_players': n_players,
    'totals': sums,
    'last_updated': '{}-{}'.format(dt.isoformat(), server_timezone),
    }

for fn in ('data/game_totals_{}.json'.format(game_id),
           'data/game_totals_{}_{}.json'.format(game_id, dt.isoformat())):
    f = open(fn, 'w')
    json.dump(game_totals, f)
    f.close()

game_data = {
    'game_id': game_id,
    'n_players': n_players,
    'players': players,
    'last_updated': '{}-{}'.format(dt.isoformat(), server_timezone),
    }

f = open('data/game_data_{}_{}.json'.format(game_id, dt.isoformat()), 'w')
json.dump(game_data, f)
f.close()

tfoot = thead[:]
tfoot.append('<tr><td style="visibility: hidden"></td><th style="text-align: right">Total</th>')
for k in ks:
    if k in ('i', 'player_name'): 
        continue
    if k.startswith('game_') or k == 'updated':
        continue
    elif k in ('damage_per_click', 'edps', 'dps'):
        tfoot.append('<td data-sort-value="{}">{}</td>'.format(player[k], show_int(sums[k])))
    elif k in ('gold', 'max_hp'):
        tfoot.append('<td data-sort-value="{}">{}</td>'.format(player[k], show_unit_int(sums[k])))
    else:
        tfoot.append('<td>{}</td>'.format(sums[k]))

tfoot.append('</tr>')
tfoot.append('<tr><td style="visibility: hidden"></td><th style="text-align: right">Mean</th>')
for k in ks:
    if k in ('i', 'player_name'): 
        continue
    if k.startswith('game_') or k == 'updated':
        continue
    elif k in ('damage_per_click', 'edps', 'dps'):
        tfoot.append('<td data-sort-value="{}">{}</td>'.format(player[k], show_int(sums[k]/(i-1))))
    elif k in ('gold', 'max_hp'):
        tfoot.append('<td data-sort-value="{}">{}</td>'.format(player[k], show_unit_int(sums[k]/(i-1))))
    else:
        tfoot.append('<td>{}</td>'.format(sums[k]/(i-1)))

tfoot.append('</tr>')

dt = most_recent_update['dt']

context = {
    'tbody': '\n'.join(tbody),
    'thead': '\n'.join(thead),
    'tfoot': '\n'.join(tfoot),
    'title': str('Room {} Ranking'.format(game_id)),
    'container-padding': '90',
    'date': '<abbr class="timeago" title="{0}-{2}">{1}</abbr>'.format(dt.isoformat(), dt, server_timezone),
    'nav': generate_nav(game_id),
    'extra_content': '',
    'run_time': str((datetime.now() - start_time).seconds),
    'long': True,
    }

render_template('./ranking_{}.html'.format(game_id), context)

print >>sys.stderr, '{} ({}): finished'.format(game_id, game_name)
