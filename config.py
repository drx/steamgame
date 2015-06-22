day = 11

win_games = {
    46100: (1, '19 Jun @ 12:48am'),
    45931: (2, '19 Jun @ 6:17am'),
    46120: (3, '19 Jun @ 6:44am'),
    46550: (4, '19 Jun @ 7:20am'),

    47321: (5, '19 Jun @ 8:17pm'),
    47365: (6, '20 Jun @ 1:56am'),
    47051: (7, '20 Jun @ 4:11am'),
    47075: (8, '20 Jun @ 6:41am'),
    47686: (9, '20 Jun @ 6:43am'),
    47020: (10, '20 Jun @ 8:24am'),

    48520: (11, '20 Jun @ 8:27pm'),
    48581: (12, '21 Jun @ 1:54am'),
    48275: (13, '21 Jun @ 2:20am'),
    48583: (14, '21 Jun @ 2:35am'),
    48595: (15, '21 Jun @ 3:43am'),
    48273: (16, '21 Jun @ 4:36am'),
    48625: (17, '21 Jun @ 4:55am'),
    48294: (18, '21 Jun @ 6:30am'),
    48293: (19, '21 Jun @ 8:04am'),

    49659: (20, '21 Jun @ 6:56pm'),
    49666: (21, '21 Jun @ 9:00pm'),
    49645: (22, '21 Jun @ 9:14pm'),
    }

server_timezone = '0400'

def get_game_list():
    game_list = []
    lines = open('./games.txt').read().split('\n')
    for line in lines[:-1]:
        game_id, game_name = line.split(',')
        game_id = int(game_id)
        game_name = game_name.strip()
        game_list.append((game_id, game_name))

    return game_list

def get_game_dict():
    return dict(get_game_list())

colors = '#a6cee3 #1f78b4 #b2df8a #33a02c #fb9a99 #e31a1c #fdbf6f #ff7f00 #cab2d6 #6a3d9a #cccc66 #b15928 #000000 #999999'.split(' ')
