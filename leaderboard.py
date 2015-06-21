from template import *
from datetime import datetime, timedelta
from config import *
from graphs import *
from collections import defaultdict
import glob
import requests
import json
import time
import fileinput
import calendar

game_list = get_game_list()
game_list_dict = get_game_dict()

start_time = datetime.now()

def get_game_data(game_id):
    success = False
    for try_i in range(5):
        try:
            url = 'http://steamapi-a.akamaihd.net/ITowerAttackMiniGameService/GetGameData/v0001/?gameid={}&include_stats=1'.format(game_id)
            r = requests.get(url)
            response = r.json()['response']
            game_data = response['game_data']
            success = True
            break
        except:
            time.sleep(2)
    if not success:
        print game_id, url
        return None

    return response

tbody = []
tbody_s = [] 

rows = []
for game_id, game_name in game_list:
    try:
        f = open('data/game_totals_{}.json'.format(game_id))
        rows.append(json.load(f))
        f.close()
    except IOError:
        pass

for row in rows:
    row['skip'] = False
    response = get_game_data(row['game_id'])
    if response is None:
        row['skip'] = True
        continue

    totals = row['totals']
    totals['completed'] = ''
    totals['place'] = 99
    if row['game_id'] in win_games:
        totals['place'], totals['completed'] = win_games[row['game_id']]
    totals['game_level'] = response['game_data']['level']
    totals['game_players'] = int(response['stats']['num_players'])
    totals['game_active'] = int(response['stats']['num_active_players'])
    totals['game_abilities'] = int(response['stats']['num_abilities_activated'])
    totals['game_clicks'] = int(response['stats']['num_clicks'])

rows = [row for row in rows if not row['skip']]
rows.sort(key=lambda x: (x['totals']['game_level'], -x['totals']['place']), reverse=True)
game_list = [(row['game_id'], game_list_dict[row['game_id']]) for row in rows]

dt = datetime.now()

game_stats = {
    'games': {},
    'last_updated': '{}-{}'.format(dt.isoformat(), server_timezone),
    }

for row in rows:
    totals = row['totals']
    game_stats['games'][row['game_id']] = {
            'level': totals['game_level'],
            'players': totals['game_players'],
            'active': totals['game_active'],
            'abilities': totals['game_abilities'],
            'clicks': totals['game_clicks'],
        }


for fn in ('data/game_stats.json'.format(),
           'data/game_stats_{}.json'.format(dt.isoformat())):
    f = open(fn, 'w')
    json.dump(game_stats, f)
    f.close()

i = 1
for row in rows:
    totals = row['totals']
    row_100 = totals['game_level'] == 100000000

    tbody.append('<tr>')
    tbody.append('<td>{}</td>'.format(i))
    if not row_100:
        tbody_s.append('<tr>')
        tbody_s.append('<td>{}</td>'.format(i))

    

    for header in theaders:
        k = header.key
        if k == 'i':
            continue
        if k == 'player_name':
            game_id = row['game_id']
            game_name = game_list_dict[row['game_id']]
            if game_name:
                name = '{}&nbsp;({})'.format(game_id, game_name)
            else:
                name = str(game_id)

            line = '<td style="text-align: left; padding-left: 5px; padding-right: 5px"><a href="/steamgame/ranking_{}.html">{}</a></td>'.format(game_id, name)
        elif k == 'completed':
            line = '<td style="white-space: nowrap; text-align: left">{}</td>'.format(totals[k])
        elif k in ('damage_per_click', 'edps', 'dps'):
            line = '<td data-sort-value="{}">{}</td>'.format(totals[k], show_int(totals[k]))
        elif k in ('gold', 'max_hp', 'game_abilities', 'game_clicks'):
            line = '<td data-sort-value="{}">{}</td>'.format(totals[k], show_unit_int(totals[k]))
        elif k == 'updated':
            dt_ = row['last_updated']
            line = '<td><abbr class="timeago-short" title="{0}">{0}</abbr></td>'.format(dt_)

        else:
            line = '<td>{}</td>'.format(totals.get(k, 0))

        tbody.append(line)
        if 'short' in header.options and not row_100:
            tbody_s.append(line)
    tbody.append('</tr>')
    if not row_100:
        tbody_s.append('</tr>')
    i += 1


def iso8601_to_epoch(date_string):
    return calendar.timegm((datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%f-"+server_timezone)+timedelta(hours=4)).timetuple())


chart_keys = [header.key for header in theaders if 'chart' in header.options]

stat_game_data = defaultdict(dict)
fns = glob.glob('./data/game_stats_*.json'.format())
data = defaultdict(list)
i = 0
for fn in fns:
    f = open(fn)
    snapshot = json.load(f)
    f.close()

    x = iso8601_to_epoch(snapshot['last_updated'])
    for game_id in snapshot['games']:
        game_id = int(game_id)
        if game_id not in stat_game_data:
            stat_game_data[game_id] = defaultdict(list)
        for key in ('level', 'active'):
            y = snapshot['games'][str(game_id)][key]
            stat_game_data[game_id][key].append((x,y))

for game_id in stat_game_data:
    for key in ('level', 'active'):
        stat_game_data[game_id][key].sort()
        stat_game_data[game_id][key] = stat_game_data[game_id][key][0::10]

def get_graph_data(game_id):
    fns = glob.glob('./data/game_totals_{}_*.json'.format(game_id))
    data = defaultdict(list)
    i = 0
    for fn in fns:
        f = open(fn)
        snapshot = json.load(f)
        f.close()

        x = iso8601_to_epoch(snapshot['last_updated'])
        for key in chart_keys:
            if 'game_' in key:
                continue
            try:
                y = snapshot['totals'][key]
                data[key].append((x, y)) 
            except KeyError:
                pass

        i += 1

    for key in data:
        data[key].sort()

    return data

def get_derivative(data, minutes):
    d_data = []
    for i in range(len(data)):
        x1, y1 = data[i]
        if i <= minutes*6*2:
            d_data.append((x1,0))
            continue
        x0, y0 = data[i-minutes*6]
        if x1-x0 > (minutes+2)*60:
            continue
        y = abs(y1-y0)/(x1-x0)
        d_data.append((x1,y))

    return d_data

graph_data = {}
series = defaultdict(list)
i = 0
series_names = []
for game_id, game_name in game_list:
    graph_data[game_id] = get_graph_data(game_id)

    for key in chart_keys:
        if key in ('game_level', 'game_active'):
            try:
                series[key].append(stat_game_data[game_id][key.replace('game_', '')])
                if key == 'game_level':
                    series['d_level'].append(get_derivative(stat_game_data[game_id][key.replace('game_', '')], 15))
                    series['d_level_60'].append(get_derivative(stat_game_data[game_id][key.replace('game_', '')], 60))
            except KeyError:
                pass
        else:
            series[key].append(graph_data[game_id][key])

    series_names.append('{} ({})'.format(game_id, game_name))
    i += 1
    if i >= len(colors):
        break

graphs = ''
msg_graphs = ''
for header in theaders:
    if 'chart' not in header.options:
        continue
    key = header.key
    graphs += render_graph(key, header.full_name, series[key], series_names)

msg_graphs += render_graph('d_level', 'Levels/s (15 min)', series['d_level'], series_names)
msg_graphs += render_graph('d_level_60', 'Levels/s (60 min)', series['d_level_60'], series_names)


extra = []
extra.append('<b>EDPS</b> (Expected DPS) = <b>E</b>[DPS] = 20*(CritMult*DPC*Crit%+DPC*(1-Crit%)) + AutoDPS. Crit% is capped at 100%.')
extra.append('<p>Damage values are hypothetical totals assuming 100% player activity.</p>')
extra.append('<p><b>Note:</b> Wormhole counts are updated when the game stats update, which is every 5-20 minutes.')

context = {
    'tbody': '\n'.join(tbody),
    'thead': '\n'.join(generate_thead('leaderboard')),
    'tfoot': '',
    'title': 'Day {} Leaderboard'.format(day),
    'container-padding': '20',
    'date': '<abbr class="timeago" title="{0}-{2}">{1}</abbr>'.format(dt.isoformat(), dt, server_timezone),
    'nav': generate_nav('leaderboard'),
    'extra_content': '\n'.join(extra),
    'run_time': str((datetime.now() - start_time).seconds),
    'long': True,
    'graphs': graphs,
    }

render_template('index.html', context)

context['graphs'] = msg_graphs + graphs
render_template('msg.html', context)

# render short.html for twitch
extra = []
extra.append('<script>setTimeout(function(){location.reload();}, 1000*10);</script>')
extra.append('''
        <style>
        body, table, td
        {
            background: black;
            color: #ccc;
            font-family: Consolas, monospace;
            font-size: 20px !important;
        }
        body
        {
            font-size: 20px;
        }
        a
        {
            color: #ccc;
        }
        .table>thead>tr>th
        {
            background: #222;
            text-align: center;
        }
        .table-bordered>tbody>tr>td, .table-bordered>tbody>tr>th, .table-bordered>tfoot>tr>td, .table-bordered>tfoot>tr>th, .table-bordered>thead>tr>td, .table-bordered>thead>tr>th, .table-bordered
        {
            border-color: #222;
        }
        .table-condensed>tbody>tr>td, .table-condensed>tbody>tr>th, .table-condensed>tfoot>tr>td, .table-condensed>tfoot>tr>th, .table-condensed>thead>tr>td, .table-condensed>thead>tr>th {
            padding: 1px;
        }
        </style>
        ''')

context['extra_content'] = '\n'.join(extra)
context['long'] = False
context['thead'] = '\n'.join(generate_thead('leaderboard_short'))
context['tbody'] = '\n'.join(tbody_s).replace('(WH', '(MSG2015 WH').replace('(#', '(MSG2015 #')
context['container-padding'] = '0'

render_template('./short.html', context)
