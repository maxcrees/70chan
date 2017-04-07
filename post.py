#!/usr/bin/env python3
from datetime import datetime
from mimetypes import guess_extension as guess_fn_ext
from os import environ
from os.path import join as path_join
from subprocess import PIPE, run
from urllib.request import urlopen

from config import *
from bbs import *
from register import checkPasswd

def pruneBoard(db, cursor, board):
    # XXX images will also need to be deleted

    cursor.execute('SELECT COUNT(*) FROM posts WHERE board = ? AND thread = 0 AND deleted = 0', (board,));
    try: activeThreads = cursor.fetchone()[0]
    except TypeError:
        critError('Board not found')

    deathRow = activeThreads - boardconf.getint(board, 'prune')
    if deathRow > 0:
        # delete OPs on death row
        cursor.execute("""
DELETE FROM posts WHERE rowid IN (SELECT rowid FROM posts
WHERE board = ? AND thread = 0 AND deleted = 0 ORDER BY datetime(tdate) LIMIT ?)""", (board, deathRow));
        # delete orphaned replies
        cursor.execute("""
DELETE FROM posts WHERE board = ? AND thread != 0
AND thread NOT IN (SELECT id FROM posts WHERE board = ? AND thread = 0)""", (board, board))
        db.commit()

def getNewThreadWord(cursor, board):
    result = run(['./scripts/threadword.sh', board], stdout=PIPE)
    word = result.stdout.decode()

    if result.returncode == 1:
        if word.startswith('!'):
            critError(word[2:])
    else:
        if word:
            word = word.strip()
            return word

    critError('Unknown error encountered while trying to generate new thread word')

def eliminateThreadWord(board, word):
    with open(config['file']['words'] + '.' + board, 'a') as words:
        words.write(word + '\n')

def getImage(board, id, url):
    # XXX
    maxsize = 1048576 # 1 MiB in bytes
    chunksize = 16 * 1024 # bytes

    try: response = urlopen(url)
    except: userError('Could not load image URL')
    headers = response.info()

    try: size = int(headers['Content-Length'])
    except: userError('Could not load URL / get image size')
    # XXX Content-Length is in octets, which is 1:1 with bytes on most systems
    if size > maxsize:
        userError('Image size is greater than 1 MiB')

    try: mime = headers['Content-Type']
    except: userError('Could not get image Content-Type')
    if not mime.startswith('image/'):
        userError('Content-Type does not start with image/')
    extension = guess_fn_ext(mime) or userError('Could not guess filename extension')

    try:
        filename = path_join(config['file']['upload'], board, str(id) + extension)
        with open(filename, 'wb') as dump:
            size = 0
            while size < maxsize:
                chunk = response.read(chunksize)
                if not chunk: break
                dump.write(chunk)
                size += chunksize

    except: critError('Could not save image')

    return extension

def handleLogin(login):
    login = login.split('!')
    if len(login) == 1:
        userError('You must supply a password to use a name')

    author = login[0]
    pw = '!'.join(login[1:])
    checkPasswd(author, pw)

    return author

def newPost(db, cursor, board, thread, ip, text):
    """Create a new post"""
    id = getPostNumber(cursor, board) + 1

    text = sanitize(text)
    if not text:
        userError('Rejecting empty post')

    # Authentication
    if text.startswith('!'):
        text = text.split()
        login = text[0][1:]
        if not login:
            author = 'Anonymous'
        else:
            author = handleLogin(login)
        text = ' '.join(text[1:])
        if not text:
            userError('Rejecting empty post')
    else:
        if boardconf.getboolean(board, 'anonPost'):
            author = 'Anonymous'
        else:
            userError('Anonymous posting is not allowed')

    # Authorization
    if 'whitelist' in boardconf[board].keys():
        authorizedList = boardconf[board]['whitelist'].strip()
        if authorizedList and not author in authorizedList.split():
            prettyList = ', '.join(authorizedList.split())
            userError('Only the following users may post to this board: ' + prettyList)

    # Image uploading
    if text.startswith('http'):
        text = text.split()
        url = text[0]
        text = ' '.join(text[1:])
        if not text:
            userError('Rejecting empty post')
        imageext = getImage(board, id, url)
        imagename = '[image uploaded via URL]'
    else:
        imageext = ''
        imagename = ''

    # Text-wrapping
    text = re.sub(r'( *<!< *)* *<< *( *<!< *)*', '\n', text)
    text = '\n'.join(textwrap(text))

    if type(thread) == int:
        threadID = thread
    else:
        threadID = thread['id']

    if threadID == 0:
        tword = getNewThreadWord(cursor, board)
        cursor.execute("""
INSERT INTO posts (board, thread, tdate, tword, id, author, ip, text, imagename, imageext)
VALUES (?, 0, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?, ?, ?)
        """, (board, tword, id, author, ip, text, imagename, imageext))
    else:
        cursor.execute("""
INSERT INTO posts (board, thread, id, author, ip, text, imagename, imageext)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (board, threadID, id, author, ip, text, imagename, imageext))

    db.commit()

    # Check if successful
    if threadID == 0:
        thread = getThreadInfo(cursor, board, id)
        eliminateThreadWord(board, tword)

        if boardconf[board]['prune']:
            pruneBoard(db, cursor, board)

    else:
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
        # Board timestamp could not be parsed, assume this is a new board
        # and let it go
        return

    diff = datetime.now() - ts
    remaining = int(boardconf.getint(board, 'throttle') - diff.total_seconds())
    if remaining > 0:
        userError('No posts will be accepted to this board for {} more seconds'.format(remaining))

def checkBans(cursor, board, ip):
    """Check if poster is banned before proceeding"""
    cursor.execute('SELECT board, reason FROM bans WHERE ip = ?', (ip,))
    bans = cursor.fetchall()

    for ban in bans:
        if ban['board'] == board:
            userError('You are banned from posting to this board: {}'.format(ban['reason']))
        elif not ban['board']:
            userError('You are banned from posting to all boards: {}'.format(ban['reason']))

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
    getBoardThrottling(cursor, board)
    if ip:
        checkBans(cursor, board, ip)

    thread = query.group(2)
    if thread:
        try:
            thread = int(thread)
            checkIntLength(thread)
        except: pass
        thread = getThreadInfo(cursor, board, thread)
        newPost(db, cursor, board, thread, ip, text)

    else:
        newPost(db, cursor, board, 0, ip, text)

    db.close()
