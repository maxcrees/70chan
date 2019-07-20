#!/usr/bin/env python3
from os.path import isfile, join as path_join
import re
import sqlite3
from sys import exit, argv
from textwrap import wrap as _textwrap
from pathlib import Path
from datetime import datetime

from config import *

def sanitize(string):
    """Sanitize strings for gopher printing (remove tabs)"""
    #string = string.strip()
    string = string.replace('\t', ' ')
    string = string.replace('\r', ' ')
    return string

def checkIntLength(i):
    """Check if the given int can be stored in sqlite or raise error"""
    if i.bit_length() > 63:
        userError('Numeric argument too large')

def textwrap(text):
    """Wrap text to ~ 80 columns for gopher output"""
    textRows = []
    paragraphs = text.splitlines()
    for paragraph in paragraphs:
        [textRows.append(line) for line in _textwrap(paragraph, 78)]
    return textRows

def write(tag, selector='', ftype='i', host=config['server']['host'], port=config['server']['port']):
    """Write a line of gopher output"""
    tag = sanitize(tag)
    selector = sanitize(selector)
    ftype = sanitize(ftype)

    print('{}{}\t{}\t{}\t{}'.format(ftype, tag, selector, host, port))

def notice(tag):
    """Use for simple notices to get user's attention"""
    write('>>> ' + tag + ' <<<', ftype='3', selector='fake', host='(NULL)', port=0)

def userError(tag):
    """Use when user tries to perform an invalid action or gives invalid input"""
    write('!!! ' + tag + ' !!!', ftype='3', selector='fake', host='(NULL)', port=0)
    write('Return to BBS home', config['path']['board'], '1')
    exit(1)

def critError(tag):
    """Use when server encounters a problem that isn't the user's fault"""
    write('*** ' + tag + ' ***', ftype='3', selector='fake', host='(NULL)', port=0)
    exit(255)

def connDB():
    """Return sqlite connection and cursor objects"""
    if not isfile(config['file']['db']):
       critError('Database not found')

    db = sqlite3.connect(config['file']['db'])
    # Return sqlite3.Row instead of tuples
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    return db, cursor

def getThreadInfo(cursor, board, thread):
    """Return thread object for given board and thread ID / word or raise error"""
    if type(thread) == int:
        cursor.execute("""
SELECT * FROM posts
WHERE board = ? AND thread = 0 AND id = ?""", (board, thread))
    else:
        cursor.execute("""
SELECT * FROM posts
WHERE board = ? AND thread = 0 AND tword = ?""", (board, thread))

    thread = cursor.fetchone()
    if not thread:
        userError('Thread not found')
    else:
        return thread

def getPostInfo(cursor, board, post):
    """Return post object for given board and post ID or raise error"""
    cursor.execute("""
SELECT * FROM posts
WHERE board = ? AND id = ?""", (board, post))

    post = cursor.fetchone()
    if not post:
        userError('Post not found')
    else:
        return post

def getPostNumber(cursor, board):
    """Get latest post number from given board or raise error"""
    cursor.execute("""
SELECT posts FROM boards
WHERE name = ?""", (board,))

    result = cursor.fetchone()
    if not result:
        userError('Board not found')
    else:
        return int(result['posts'])

def getBBSlock():
    """Check if the lockfile exists raise error if it does"""
    lock = Path(config['file']['lock'])
    if lock.is_file():
        when = datetime.utcfromtimestamp(lock.stat().st_mtime)
        when = when.strftime('%c UTC')
        reason = lock.read_text().strip() or '(no reason given)'
        write(f'*** BBS is currently offline since {when}:***', ftype='3')
        critError(reason)

def getThreadLink(board, thread):
    """Get selector to given thread object with respect to preference between ID and thread words"""
    if boardconf.getboolean(board, 'preferThreadWords'):
        threadSelector = thread['tword']
    else:
        threadSelector = str(thread['id'])
    selector = path_join(config['path']['board'], board, 'thread', threadSelector)
    return selector

def getIP(environ):
    try: ip = environ['PEER']
    except KeyError:
        ip = ''
    if ip == 'unknown':
        ip = ''

    ip = re.sub('^::ffff:', '', ip)
    return ip

def genMap():
    endpoints = ['post', 'del', 'register', 'changepw']

    for endpoint in endpoints:
        endMap = '!dirproc-raw\t{}\t{}'.format(config['path'][endpoint].replace( \
                 '/', ''), path_join(root, endpoint + '.py'))
        print(endMap)


    for board in boardconf.keys():
        if board == 'board': continue

        boardMap = '!dirproc-raw\t{}\t{}'.format(board, path_join(root, 'board.py'))
        print(boardMap)

if __name__ == '__main__' and 'REQUEST' not in environ:
    if len(argv) == 2 and argv[1] == 'genMap':
        genMap()
