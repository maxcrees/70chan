#!/usr/bin/env python3
from math import ceil
import re
from os import environ
from os.path import join as path_join

from config import *
from bbs import *

def mapCommand(query):
    env = {}
    if query.group(2) == 'thread':
        # Thread ID
        try: env['thread'] = int(query.group(3))
        except TypeError:
            # No argument given
            userError('Command "thread" requires a thread ID or thread word as an argument')
        except ValueError:
            # Thread word - strip anything that isn't ASCII letters
            badbits = re.compile(r'[^a-zA-Z]+')
            env['thread'] = re.sub(badbits, '', query.group(3)).lower()

        if type(env['thread']) == int:
            checkIntLength(env['thread'])

    elif query.group(2) == 'skip':
        try: env['skip'] = int(query.group(3))
        except TypeError:
            # No argument given
            userError('Command "skip" requires a number of posts to skip as an argument')
        except ValueError:
            # Non-integer argument given
            userError('Command "skip" requires an integer number of posts to skip as an argument')

        checkIntLength(env['skip'])

    elif query.group(2) == 'post':
        try: env['post'] = int(query.group(3))
        except TypeError:
            # No argument given
            userError('Command "post" requires a post ID as an argument')
        except ValueError:
            # Non-integer argument given
            userError('Command "post" requires an integer post ID as an argument')

        checkIntLength(env['post'])

    else:
        userError('Invalid request')

    return env

def showLinkImg(board, id, author, date, imageext, imagename):
    selector = path_join(config['path']['upload'], board, str(id) + imageext)
    author = author.ljust(config.getint('server', 'maxAuthorLength'))
    write('{} #{} @ {} :: {}'.format(author, id, date, imagename), selector, 'I')

def showLinkTxt(board, id, author, date):
    selector = path_join(config['path']['board'], board, 'post', str(id))
    author = author.ljust(config.getint('server', 'maxAuthorLength'))
    write('{} #{} @ {}'.format(author, id, date), selector, '1')

def showText(text, truncate=0):
    textRows = textwrap(text)

    count = 0
    for textRow in textRows:
        count += 1
        if count > boardconf.getint(board, 'showTextLines') and truncate:
            write('~~~ Post truncated... ~~~');
            break
        elif textRow == "":
            write('  ')
        else:
            write('  ' + textRow)

def showThread(cursor, board, thread, replyLimit=0, truncate=0):
    if thread['replies'] == 1:
        replyStr = "reply"
    else:
        replyStr = "replies"

    selector = getThreadLink(board, thread)

    write('=======[ No. {} :: {} ]======= {} {}'.format(thread['id'], thread['tword'], thread['replies'], replyStr), selector, '1')
    showPost(thread, truncate)

    # Show last "replyLimit" replies
    replySkip = int(thread['replies']) - replyLimit
    if replyLimit and replySkip > 0:
        if replySkip == 1: suffix = 'y'
        else: suffix = 'ies'
        write('~~~ Skipping {} repl{}... ~~~'.format(replySkip, suffix))
        cursor.execute("""
SELECT *
FROM posts WHERE thread = ? AND board = ? ORDER by ts LIMIT ?,?""", (thread['id'], board, replySkip, replyLimit))
    else:
        cursor.execute("""
SELECT *
FROM posts WHERE thread = ? AND board = ? ORDER by ts""", (thread['id'], board))

    # Print replies
    replies = cursor.fetchall()
    for reply in replies:
        showPost(reply, truncate)

def showPost(post, truncate=0):
    if post['deleted'] == 1:
        if post['thread'] == 0:
            notice('OP deleted #{} (originally posted @ {})'.format(post['id'], post['ts']))
        else:
            notice('Replier deleted #{} (originally posted @ {})'.format(post['id'], post['ts']))
    elif post['imageext']:
        showLinkImg(board, post['id'], post['author'], post['ts'], post['imageext'], post['imagename'])
        showText(post['text'], truncate)
    else:
        showLinkTxt(board, post['id'], post['author'], post['ts'])
        showText(post['text'], truncate)

def showBoard(cursor, board, env):
    # Set skip, default 0
    if not 'skip' in env:
        skip = 0
    else:
        skip = env['skip']

    cursor.execute('SELECT COUNT(*) FROM posts WHERE board = ? AND thread = 0', (board,))
    try: totalThreads = cursor.fetchone()[0]
    except TypeError:
        critError('Board not found')
    pages = ceil(totalThreads / boardconf.getint(board, 'showThreads'))

    # Paginate
    if skip > 0:
        showThreads = boardconf.getint(board, 'showThreads')
        back = skip - showThreads
        if back < 0:
            back = 0
        page = ceil(back / showThreads) + 1
        if page > 0:
            selector = path_join(config['path']['board'], board, 'skip', str(back))
            write('Previous page ({} of {})'.format(page, pages), selector, '1')
            write('')

    # Retrieve threads
    cursor.execute("""
SELECT * FROM posts
WHERE board = ? AND thread = 0 ORDER BY tdate DESC LIMIT ?,?""", (board, skip, boardconf[board]['showThreads']))

    # Print threads
    threadList = cursor.fetchall()
    threads = len(threadList)
    if not threads:
        critError('No posts found')

    for thread in threadList:
        showThread(cursor, board, thread, replyLimit=boardconf.getint(board, 'showReplies'), truncate=1)
        write('')

    # Paginate
    showThreads = boardconf.getint(board, 'showThreads')
    if totalThreads - skip - showThreads > 0:
        skip += showThreads
        page = ceil(skip / showThreads) + 1
        selector = path_join(config['path']['board'], board, 'skip', str(skip))
        write('Next page ({} of {})'.format(page, pages), selector, '1')

if __name__ == '__main__':
    # Check if BBS is disabled
    getBBSlock()

    # Extract board name and predicate
    queryfinder = re.compile(r'([a-z0-9]+)/?([a-z0-9]+)?/?([a-z0-9]+)?')
    try: query = re.match(queryfinder, environ['QUERY'])
    except KeyError:
        #print(repr(environ))
        critError('QUERY is missing. Check gopher server implementation')
    try:
        board = query.group(1)
    except AttributeError:
        userError('A board name is required')

    if query.group(2):
        env = mapCommand(query)
    else:
        env = {}
    db, cursor = connDB()
    if 'thread' in env:
        thread = getThreadInfo(cursor, board, env['thread'])
        write('~~~ Showing one thread... ~~~')
        selector = path_join(config['path']['post'], board, str(env['thread']))
        write('Reply', selector, '7')
        selector = path_join(config['path']['del'], board)
        write('Delete post by numeric ID', selector, '7')
        selector = path_join(config['path']['board'], board)
        write('Return to board index', selector, '1')
        write('')
        showThread(cursor, board, thread)

    elif 'post' in env:
        post = getPostInfo(cursor, board, env['post'])
        write('~~~ Showing one post... ~~~')
        if post['thread'] == 0:
            thread = post
        else:
            thread = getThreadInfo(cursor, board, int(post['thread']))
        selector = getThreadLink(board, thread)
        write('Show entire thread', selector, '1')
        write('Delete this post (requires matching password and, if Anonymous, IP address)', path_join(config['path']['del'], board, str(post['id'])), '7')
        write('')

        showPost(post)

    else:
        write('~~~ Showing one board... ~~~')
        selector = path_join(config['path']['post'], board)
        write('Create a new thread', selector, '7')
        selector = path_join(config['path']['del'], board)
        write('Delete a post by numeric ID', selector, '7')
        write('Return to BBS home', config['path']['board'], '1')
        write('')
        showBoard(cursor, board, env)
    db.close()
