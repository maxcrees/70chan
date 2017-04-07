#!/usr/bin/env python3
from crypt import crypt, METHOD_SHA512
from hmac import compare_digest as compare_hash
from os.path import join as path_join
import re
from sys import exit

from bbs import *
from config import *

def nameExists(passwd, name):
    if not name in passwd.keys():
        userError('That name is not registered')

def secHash(text):
    return crypt(text, METHOD_SHA512)

def checkPasswd(name, plainPW):
    passwd, email = loadPasswd()
    nameExists(passwd, name)

    if passwd[name] == 'REVOKED':
        userError('This name is banned')

    hash = crypt(plainPW, passwd[name])
    # XXX
    if not hash:
        from bcrypt import hashpw as crypt_blowfish
        hash = crypt_blowfish(plainPW.encode('utf-8'), passwd[name].encode('utf-8'))
        hash = hash.decode('utf-8')

    if not compare_hash(passwd[name], hash):
        userError('Password does not match')

def loadPasswd():
    passwd = {}
    email = {}
    with open('data/passwd') as f:
        for line in f:
            line = line.strip().split(':')
            passwd[line[0]] = line[1]
            email[line[0]] = line[2]

    return passwd, email

def register(passwd, name, pw):
    hash = secHash(pw)
    with open('data/passwd', 'a') as f:
        f.write(name + ':' + hash + ':gopher@bbs.sick.bike\n')

    write('Registered name "{}"'.format(name), ftype='3')
    write('Return to BBS home', config['path']['board'], '1')

def nameCheck(name, names):
    validName = r'^[A-Za-z0-9_-]+$'
    validLen = config.getint('board', 'maxAuthorLength')

    if not re.match(validName, name):
        userError('Name can only be alphanumeric with dashes and underscores')
    if len(name) > validLen:
        userError('Name is too long (max {} characters)'.format(validLen))
    if name.lower() in names:
        userError('Name already in use')
    if name.lower() == 'anonymous':
        userError('Name cannot be "Anonymous"')

if __name__ == '__main__':
    getBBSlock()
    passwd, email = loadPasswd()
    names = [name.lower() for name in passwd.keys()]

    pattern = re.escape(config['path']['register'][1:]) + r'(.*)/?'
    queryfinder = re.compile(pattern)
    try: query = re.match(queryfinder, environ['QUERY'])
    except KeyError:
        critError('QUERY is missing. Check gopher server implementation')
    try: name = query.group(1)
    except AttributeError: name = None

    if not query or not name:
        try: name = environ['SEARCH']
        except KeyError:
            write('Enter name', config['path']['register'][:-1], '7')
            exit(0)

        nameCheck(name, names)
        write('Enter password', path_join(config['path']['register'], name), '7')

    else:
        nameCheck(name, names)

        try: pw = environ['SEARCH']
        except KeyError:
            write('Enter password', path_join(config['path']['register'], name), '7')
            exit(0)

        if pw.find(' ') != -1:
            userError('Password cannot contain spaces')

        register(passwd, name, pw)
