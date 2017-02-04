#!/usr/bin/env python3
from configparser import ConfigParser
from os import environ, getcwd
from os.path import isfile, join as path_join
from sys import argv, exit

# Setup config
configDefaults = {
    'server': {
        'host': 'localhost',
        'port': 70
    },
    'file': {
        'db': 'database.sqlite3',
        'lock': 'lock',
        'gopher': '.gopher',
        'wordlist': '/usr/share/dict/words',
        'words': 'words'
    },
    'path': {
        'board': '/',
        'post': '/post/',
        'del': '/del/',
        'upload': '/upload/'
    },
    'board': {
        'showThreads': 10,
        'showReplies': 3,
        'showTextLines': 3,
        'preferThreadWords': True
    },
    'post': {
        'throttle': 120
    }
}
config = ConfigParser()
config.read_dict(configDefaults)
config.read(path_join(getcwd(), 'config.ini'))

# Path resolution
for f, path in config['file'].items():
    if not path.startswith('/'):
        config['file'][f] = path_join(getcwd(), config['file'][f])
        path = config['file'][f]

    if f != 'words' and f != 'lock' and not isfile(path):
        print('3*** configuration error: "{}" does not exist ***\tfake\t(NULL)\t0'.format(path))
        exit(255)

# Type assertions
try: config.getboolean('board', 'preferThreadWords')
except ValueError:
    print('3*** configuration error: board.preferThreadWords must be "yes" or "no" ***\tfake\t(NULL)\t0')
    exit(255)
try:
    config.getint('board', 'showThreads')
    config.getint('board', 'showReplies')
    config.getint('board', 'showTextLines')
    config.getint('post', 'throttle')
except ValueError:
    print('3*** configuration error: board.{showThreads, showReplies, showTextLines} and post.throttle must be integers ***\tfake\t(NULL)\t0')
    exit(255)

if __name__ == '__main__' and 'REQUEST' not in environ:
   if len(argv) > 2:
       try: print(config[argv[1]][argv[2]])
       except KeyError:
           print('Unknown configuration option')
           exit(1)
