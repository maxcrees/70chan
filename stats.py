#!/usr/bin/env python3
from os.path import join as path_join

from bbs import *
from config import *

if __name__ == '__main__':
    db, cursor = connDB()
    cursor.execute('SELECT * FROM boards ORDER BY name')
    boards = cursor.fetchall()
    if not boards:
        critError('No boards found')

    for board in boards:
        selector = path_join(config['path']['board'], board['name'])
        if board['description']:
            write('/{}/: {}'.format(board['name'], board['description']),
                  selector, ftype='1')
        else:
            write('/{}/'.format(board['name']), selector, ftype='1')

        if board['threads'] == 1:
            pluralThread = ''
        else:
            pluralThread = 's'
        if board['posts'] == 1:
            pluralPost = ''
        else:
            pluralPost = 's'
        write('  history:      {} post{} in {} thread{}'.format(board['posts'], pluralPost,
              board['threads'], pluralThread))
        write('  last post on: {} UTC'.format(board['ts']))
