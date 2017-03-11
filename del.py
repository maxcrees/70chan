#!/usr/bin/env python3
from os import remove as file_rm
from os.path import isfile, join as path_join
from sys import exit

from bbs import *
from config import *

def delPost(db, cursor, board, id, ip, password):
    """Delete a post"""

    # Delete post
    cursor.execute('SELECT thread, imageext FROM posts WHERE board = ? AND id = ? AND ip = ? AND password = ? AND deleted = 0', (board, id, ip, password))
    selection = cursor.fetchone()
    if not selection:
        userError('Post not found with that board / ID / IP address / password combination')
    cursor.execute('UPDATE posts SET deleted = 1 WHERE board = ? AND id = ?', (board, id))
    db.commit()
    imageext = selection['imageext']
    filename = path_join(config['file']['upload'], board, str(id) + imageext)
    if imageext and isfile(filename):
        try: file_rm(filename)
        except: pass
    write('Deleted post #{}'.format(id), ftype='3')

    # Delete thread if OP and all replies are deleted
    thread = selection['thread'] or id
    cursor.execute('SELECT COUNT(*) FROM posts WHERE BOARD = ? AND (id = ? OR thread = ?) AND deleted = 0', (board, thread, thread))
    try:
        replies = cursor.fetchone()[0]
        if replies == 0:
            cursor.execute('DELETE FROM posts WHERE BOARD = ? AND (id = ? OR thread = ?)', (board, thread, thread))
            db.commit()
    except: pass

    try:
        thread = getThreadInfo(cursor, board, thread)
        write('Return to thread', getThreadLink(board, thread), '1')
    except SystemExit: pass
    write('Return to board index', path_join(config['path']['board'], board), '1')

if __name__ == '__main__':
    getBBSlock()

    ip = getIP(environ)
    if not ip:
        userError('An IP address is required to delete a post')

    pattern = re.escape(config['path']['del'][1:]) + r'([a-z0-9]+)/?([a-z0-9]+)?'
    queryfinder = re.compile(pattern)
    try: query = re.match(queryfinder, environ['QUERY'])
    except KeyError:
        critError('QUERY is missing. Check gopher server implementation')
    try:
        board = query.group(1)
    except AttributeError:
        userError('A board name is required')

    id = query.group(2)
    if not id:
        try:
            id = int(environ['SEARCH'])
            write('Enter password', path_join(config['path']['del'], board, str(id)), '7')
            exit(0)
        except: pass
        if not id:
            write('Enter numeric post ID', path_join(config['path']['del'], board), '7')
            exit(0)

    else:
        try: password = environ['SEARCH']
        except KeyError:
            userError('No password given')

        db, cursor = connDB()
        try:
            id = int(id)
            checkIntLength(id)
        except: pass
        delPost(db, cursor, board, id, ip, password)
        db.close()
