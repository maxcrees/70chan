#!/usr/bin/env python3
from datetime import datetime
from os import environ

from config import *
from bbs import *

def newPost(db, cursor, board, thread, ip, text):
   """Create a new post"""
   text = sanitize(text)
   if not text:
       userError('Rejecting empty post')
   text = '\n'.join(textwrap(text))
   id = getPostNumber(cursor, board) + 1
   cursor.execute("""
INSERT INTO posts (board, thread, id, ip, text)
VALUES (?, ?, ?, ?, ?)
""", (board, thread['id'], id, ip, text))
   db.commit()

   getPostInfo(cursor, board, id)
   write('Posted #{} to /{}/'.format(id, board), ftype='3')
   write('')
   selector = getThreadLink(board, thread)
   write('Return to thread', selector, ftype='1')
   selector = path_join(config['path']['board'], board)
   write('Return to board index', selector, ftype='1')

def getBoardThrottling(cursor, board):
    """Check if post throttling needs to be applied"""
    # Using UTC
    cursor.execute('SELECT ts FROM boards WHERE name = ?', (board,))
    try: ts = cursor.fetchone()[0]
    except TypeError:
        critError('Board not found')
    try: ts = datetime.strptime(ts, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        critError('Board timestamp could not be parsed')

    diff = datetime.now() - ts
    remaining = int(config.getint('post', 'throttle') - diff.total_seconds())
    if remaining > 0:
        userError('No posts will be accepted to this board for {} more seconds'.format(remaining))

if __name__ == '__main__':
    getBBSlock()

    pattern = re.escape(config['path']['post'][1:]) + r'([a-z0-9]+)/?([a-z0-9]+)?'
    queryfinder = re.compile(pattern)
    try: query = re.match(queryfinder, environ['QUERY'])
    except KeyError:
        critError('QUERY is missing. Check gopher server implementation')
    try:
        board = query.group(1)
    except AttributeError:
        userError('A board name is required')
    try: text = environ['SEARCH']
    except KeyError:
        userError('No text to post given')
    ip = getIP(environ)

    db, cursor = connDB()
    thread = query.group(2)
    getBoardThrottling(cursor, board)
    if thread:
        try:
            thread = int(thread)
            checkIntLength(thread)
        except: pass
        thread = getThreadInfo(cursor, board, thread)
        newPost(db, cursor, board, thread, ip, text)
    # TODO: support OPs
    #else:
    #    newPost(cursor, board, 0, text)
    db.close()
