from config import *
from collections import namedtuple
import re

Header = namedtuple('Header', 'key, name, full_name, options')

theaders = [
    Header('i', '#', '#', ['short']),
    Header('player_name', 'Name', 'Name', ['short']),
    Header('game_level', 'Level', 'Level', ['leaderboard', 'short', 'chart']),
    Header('completed', 'Completed', 'Completed', ['leaderboard']),
    Header('game_players', 'Players', 'Players', ['leaderboard', 'short']),
    Header('game_active', 'Active', 'Active Players', ['leaderboard', 'short', 'chart']),
    Header('game_abilities', 'Abilities', 'Abilities Activated', ['leaderboard']),
    Header('game_clicks', 'Clicks', 'Clicks', ['leaderboard']),
    Header('wormholes', 'Whs', 'Wormholes', ['short', 'chart']),
    Header('like_new', 'LN', 'Like New', ['chart']),
    Header('feeling_lucky', 'FL', 'Feeling lucky', []),
    Header('damage_per_click', 'DPC', 'Damage Per Click', ['chart']),
    Header('edps', 'EDPS', 'Expected DPS', ['short', 'chart']),
    Header('gold', 'Gold', 'Gold', ['chart']),
    Header('max_hp', 'HP', 'Hit Points', ['chart']),
    Header('crit_percentage', 'Crit&nbsp;%', 'Critical percentage', []),
    Header('dps', 'Auto&nbsp;DPS', 'Auto DPS', []),
    Header('boss_loot_drop_percentage', 'Drop&nbsp;%', 'Boss loot drop percentage', []),
    Header('elemental', 'Elem', 'Maximum elemental damage', []),
    Header('upgrade_7', 'LS', 'Lucky Shot', []),
    Header('upgrade_2', 'APR', 'Armor Piercing Round', []),
    Header('upgrade_10', 'ER', 'Explosive Rounds', []),
    Header('upgrade_22', 'Rg', 'Railgun', []),
    Header('upgrade_25', 'NMB', 'New Mouse Button', []),
    Header('upgrade_28', 'TMB', 'Titanium Mouse Button', []),
    Header('upgrade_31', 'DBM', 'Double-Barrelled Mouse', []),
    Header('upgrade_34', 'BF', 'Bionic Finger', []),
    Header('updated', 'Updated', 'Updated', ['leaderboard']),
    ]

ks = [header.key for header in theaders]

def generate_nav(tab):
    nav = []

    active = ''
    if tab == 'leaderboard':
        active = 'class="active"'
    nav.append('<li role="presentation" {}><a href="/steamgame/">Leaderboard</a></li>'.format(active))

    for game, game_name in get_game_list():
        active = ''
        if game == tab:
            active = 'class="active"'
        if game_name:
            link = '{} ({})'.format(game, game_name)
        else:
            link = str(game)
        nav.append('<li role="presentation" {}><a href="./ranking_{}.html">{}</a></li>'.format(active, game, link))
    return '\n'.join(nav)

def generate_thead(page):
    thead = []
    thead.append('<tr>')
    for header in theaders:
        if page not in ('leaderboard', 'leaderboard_short') and 'leaderboard' in header.options:
            continue
        if page == 'leaderboard_short' and 'short' not in header.options:
            continue
        thead.append('<th alt="{1}" title="{1}">{0}</th>'.format(header.name, header.full_name))
    thead.append('</tr>')
    return thead

units = ' KMBTqQsSONdUD!@#$%^&*'

def show_int(n):
    return '{:,}'.format(n)

def show_unit_int(n):
    for i in range(len(units)):
        if n < 10**(3*(i+1)-2):
            return '{:.1f}{}'.format(float(n)/10**(3*i), units[i]).strip()
        if n < 10**(3*(i+1)):
            return '{}{}'.format(int(float(n)/10**(3*i)), units[i]).strip()

def render_template(filename, context):
    template = open('./template.html').read()

    for key, value in context.items():
        if key == 'long':
            continue
        if key == 'title':
            value = re.sub('<.*?>', '', value)
        template = template.replace('{'+key+'}', value)

    if context['long']:
        template = template.replace('{% if long %}', '')
        template = template.replace('{% endif %}', '')
    else:
        template = re.sub('{% if long %}(.*?){% endif %}', '', template, flags=re.S)

    f = open(filename, 'w')
    f.write(template)
    f.close()
