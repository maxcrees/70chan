#!/usr/bin/env python3
from configparser import ConfigParser
from os import environ, getcwd, chdir
from os.path import isdir, isfile, join as path_join
from sys import argv, exit

try: root = INSTALLATION_PATH
except NameError:
    print('3*** configuration error: you must run scripts/setup.sh first! ***\tfake\t(NULL)\t0')
    exit(255)

chdir(root)

# Setup config
configDefaults = {
    'server': {
        'host': 'localhost',
        'port': 70,
        'maxAuthorLength': 16,
    },
    'file': {
        'db': 'data/database.sqlite3',
        'lock': 'data/lock',
        'gopher': '.gopher',
        'wordlist': '/usr/share/dict/words',
        'words': 'data/words',
        'upload': '../upload'
    },
    'path': {
        'board': '/',
        'post': '/post/',
        'del': '/del/',
        'upload': '/upload/',
        'register': '/register/',
        'changepw': '/changepw/'
    },
}
boardconfDefaults = {
    'board': {
        'showThreads': 10,
        'showReplies': 3,
        'showTextLines': 3,
        'preferThreadWords': True,
        'prune': 50,
        'defaultPassword': 'password',
        'throttle': 120,
        'anonPost': True
    },
}
config = ConfigParser()
config.read_dict(configDefaults)
config.read(path_join(getcwd(), 'data/config.ini'))

boardconf = ConfigParser(default_section='board')
boardconf.read_dict(boardconfDefaults)
boardconf.read(path_join(getcwd(), 'data/boards.ini'))

# Path resolution
for f, path in config['file'].items():
    if not path.startswith('/'):
        config['file'][f] = path_join(getcwd(), config['file'][f])
        path = config['file'][f]

    if f == 'words':
        pass
    elif f == 'lock':
        pass
    elif f == 'upload':
        if not isdir(path):
            print('3*** configuration error: "{}" does not exist ***\tfake\t(NULL)\t0'.format(path))
    elif not isfile(path) and len(argv) < 4:
        print('3*** configuration error: "{}" does not exist ***\tfake\t(NULL)\t0'.format(path))
        exit(255)

config['file']['root'] = root

# Type assertions
try:
    boardconf.getboolean('board', 'preferThreadWords')
    boardconf.getboolean('board', 'anonPost')
except ValueError:
    print('3*** configuration error: board.{preferThreadWords, anonPost} must be "yes" or "no" ***\tfake\t(NULL)\t0')
    exit(255)
try:
    boardconf.getint('board', 'showThreads')
    boardconf.getint('board', 'showReplies')
    boardconf.getint('board', 'showTextLines')
    boardconf.getint('board', 'prune')
    boardconf.getint('board', 'throttle')
    config.getint('server', 'maxAuthorLength')
except ValueError:
    print('3*** configuration error: board.{showThreads, showReplies, showTextLines, prune, maxAuthorLength, throttle} and server.maxAuthorLength must be integers ***\tfake\t(NULL)\t0')
    exit(255)

if __name__ == '__main__' and 'REQUEST' not in environ:
   if len(argv) > 2:
       try: print(config[argv[1]][argv[2]])
       except KeyError:
           print('Unknown configuration option')
           exit(1)
