#!/usr/bin/env python3
from configparser import ConfigParser
from os import environ, getcwd
from os.path import isfile as os_isfile, join as path_join
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
if not config['file']['db'].startswith('/'):
    config['file']['db'] = path_join(getcwd(), config['file']['db'])
if not config['file']['lock'].startswith('/'):
    config['file']['lock'] = path_join(getcwd(), config['file']['lock'])
if not config['file']['wordlist'].startswith('/'):
    config['file']['wordlist'] = path_join(getcwd(), config['file']['wordlist'])
if not config['file']['words'].startswith('/'):
    config['file']['words'] = path_join(getcwd(), config['file']['words'])
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
           exit(255)
