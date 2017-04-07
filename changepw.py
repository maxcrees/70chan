#!/usr/bin/env python3
from os.path import join as path_join
import re
from sys import exit

from bbs import *
from config import *
from register import *

def changePasswd(passwd, email, changingName, newpw):
    passwd[changingName] = secHash(newpw)

    with open('data/passwd', 'w') as f:
        for name in passwd.keys():
            f.write('{}:{}:{}\n'.format(name, passwd[name], email[name]))

    write('Successfully changed password for "{}"'.format(changingName), ftype='3')
    write('Return to BBS home', config['path']['board'], '1')

if __name__ == '__main__':
    getBBSlock()
    passwd, email = loadPasswd()

    pattern = re.escape(config['path']['changepw'][1:]) + r'(.*)/?'
    queryfinder = re.compile(pattern)
    try: query = re.match(queryfinder, environ['QUERY'])
    except KeyError:
        critError('QUERY is missing. Check gopher server implementation')
    try: name = query.group(1)
    except AttributeError: name = None

    if not query or not name:
        try: name = environ['SEARCH']
        except KeyError:
            write('Enter name', config['path']['changepw'][:-1], '7')
            exit(0)

        nameExists(passwd, name)
        write('Enter old password and new password, separated by a space', path_join(config['path']['changepw'], name), '7')
        write('WARNING: Anything written after a space after the new password will be ignored!')

    else:
        nameExists(passwd, name)

        try: search = environ['SEARCH']
        except KeyError:
            write('Enter old password and new password, separated by a space', path_join(config['path']['changepw'], name), '7')
            write('WARNING: Anything written after a space after the new password will be ignored!')
            exit(0)

        if not search:
            userError('You must enter your old password and new password')

        search = search.split()
        if len(search) == 1:
            userError('You must enter your new password')

        oldpw = search[0]
        checkPasswd(name, oldpw)
        newpw = search[1]
        changePasswd(passwd, email, name, newpw)
