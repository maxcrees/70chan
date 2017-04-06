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
        'port': 70
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
        'register': '/register/'
    },
    'board': {
        'showThreads': 10,
        'showReplies': 3,
        'showTextLines': 3,
        'preferThreadWords': True,
        'prune': 50,
        'maxAuthorLength': 16,
        'defaultPassword': 'password'
    },
    'post': {
        'throttle': 120
    }
}
config = ConfigParser()
config.read_dict(configDefaults)
config.read(path_join(getcwd(), 'data/config.ini'))

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
try: config.getboolean('board', 'preferThreadWords')
except ValueError:
    print('3*** configuration error: board.preferThreadWords must be "yes" or "no" ***\tfake\t(NULL)\t0')
    exit(255)
try:
    config.getint('board', 'showThreads')
    config.getint('board', 'showReplies')
    config.getint('board', 'showTextLines')
    config.getint('board', 'prune')
    config.getint('post', 'throttle')
    config.getint('board', 'maxAuthorLength')
except ValueError:
    print('3*** configuration error: board.{showThreads, showReplies, showTextLines, prune, maxAuthorLength} and post.throttle must be integers ***\tfake\t(NULL)\t0')
    exit(255)

if __name__ == '__main__' and 'REQUEST' not in environ:
   if len(argv) > 2:
       try: print(config[argv[1]][argv[2]])
       except KeyError:
           print('Unknown configuration option')
           exit(1)
