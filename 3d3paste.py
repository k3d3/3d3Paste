#!/usr/bin/env python2.7

'''
Pasteurl is a paste url thing.
Copyright (C) 2011 Keith 3d3

Pasteurl is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

Pasteurl is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to
the Free Software Foundation, Inc., 
51 Franklin Street, Fifth Floor, Boston, MA
02110-1301, USA.
'''

import socket
import sys
import os
import pwd
import grp
import datetime
import time
import re
from hashlib import sha256

import bottle
import msgpack
import fapws.base
from bottle import route, view, HTTPError, HTTPResponse
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
from fapws import _evwsgi as evwsgi
from cmemcached import Client

formatter = HtmlFormatter(linenos=True, lineanchors="line", anchorlinenos=True)

domain = "3d3.ca"
memcached = ['127.0.0.1:11211']
memcachedb = ['127.0.0.1:21201']
MAX_URL_LENGTH = 2000
MAX_PASTE_TITLE = 200
MAX_PASTE_LENGTH = 200000

data = {'url:nextid': 0,
        #'url:test': msgpack.dumps(["http://www.google.com", time.time(),
        #                          sha256("mypassword").digest(),
        #                          "\xff\xff\xff\x00"]),
        #'url:asdf': msgpack.dumps(["http://www.google.com",
        #                          time.time(), None, "\xff\xff\xff\x00"]),
        'paste:nextid': 0
        #'paste:test': msgpack.dumps(['print "Hello World"\n'*300,
        #                            "Test Title", "python", time.time(),
        #                            sha256("mypassword").digest(),
        #                            "\xff\xff\xff\00"])
       }

# The following portion of code has been taken from
# http://code.google.com/p/pymine/source/browse/trunk/util/base58.py revision 503
# Licenced under the Apache License
        
__b58chars = 'abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ123456789'

def b58encode(value):
    encoded = ''
    while value >= 58:
        div, mod = divmod(value, 58)
        encoded = __b58chars[mod] + encoded # add to left
        value = div
    encoded = __b58chars[value] + encoded # most significant remainder
    return encoded

# End shamelessly stolen code

# This function also works for IPv6 too
def compactIP(ipaddr):
    try:
        return socket.inet_pton(socket.AF_INET, ipaddr)
    except socket.error:
        return socket.inet_pton(socket.AF_INET6, ipaddr)

urlmatch = re.compile("((mailto\:|([a-z]+)\://){1}\S+)")
def validate_url(url):
    if len(url) > MAX_URL_LENGTH:
        return "URL is %d characters long, maximum is %d" % (len(url), MAX_URL_LENGTH), None
    if url.startswith("magnet:?"):
        return None, url
    else:
        if not "://" in url and not url.startswith("mailto:"):
            url = "http://" + url
        if not re.match(urlmatch, url):
            return "%s is not a valid url" % url, url
        else:
            return None, url

def lookup_url(memory, database, url):
    return get_data(memory,database,"lurl:"+sha256(url).hexdigest())

def validate_paste(paste, title):
    if paste == None or len(paste) == 0:
        return ("Paste is empty", None, None)
    if len(paste) > MAX_PASTE_LENGTH:
        return ("Paste is %d characters long, maximum is MAX_PASTE_LENGTH" % len(paste), None, None)
    if title != None and len(title) > MAX_PASTE_TITLE:
        return ("Title is %d characters long, maximum is MAX_PASTE_TITLE" % len(title), None, None)
    return (None, paste, title)

# Memory is a memcached connection
# and database is a memcachedb connection
def get_data(memory, database, name):
    data = memory.get(name)
    if data == None:
        data = database.get(name)
        if data == None:
            return None
        else:
            memory.set(name,data)
    return data

# Sets data in memcache and database
def set_data(memory, database, name, value):
    memory.set(name,value)
    return database.set(name,value)

# Increments data in memcache and database
def incr_data(memory, database, name, default=0):
    data = database.incr(name)
    if data == None:
        database.set(name,0)
        memory.set(name,0)
        return 0
    return data

# Static front page, can be cached by reverse proxy
@route("/")
@view("frontpage")
def root(*args, **kwargs):
    return {}


@route("/", method="POST")
def submitstuff(*args, **kwargs):
    global memcached, memcachedb
    memory = Client(memcached)
    database = Client(memcachedb)
    if bottle.request.environ['HTTP_X_FORWARDED_SSL'] == 'on':
        proto = 'https'
    else:
        proto = 'http'
    if 'url' in bottle.request.params:
        invalid, fixedurl = validate_url(bottle.request.params['url'])
        if invalid:
            if 'button' in bottle.request.params:
                return bottle.template("error", title="URL Submission Error",
                       reason=invalid, url="%://%s"%(proto,domain), rurl=None)
            else:
                bottle.response.content_type = "text/plain"
                return "ERROR: URL Submission Failed.\n%s\n" % invalid
        else:
            if 'p' in bottle.request.params and \
                      bottle.request.params['p'] != "":
                password=bottle.request.params['p']
            else:
                password=None
            old_url = lookup_url(memory, database, fixedurl)
            if old_url and not password:
                b58id = old_url
            else:
                nextid = incr_data(memory,database,"url:nextid")
                b58id = b58encode(nextid)
            
            set_data(memory, database, 'url:'+b58id, msgpack.dumps([fixedurl,
                     time.time(),
                     sha256(password).digest() if password else None,
                     compactIP(bottle.request.environ['HTTP_X_FORWARDED_FOR']\
                     .split(", ")[-1])]))
            if not password:
                digest = "lurl:"+sha256(fixedurl).hexdigest()
                set_data(memory,database,digest,b58id)
                
            if 'button' in bottle.request.params:
                return bottle.template("urlsub", url = "%s://%s/u%s" %
                                       (proto, domain, b58id),
                                       rurl="%s://%s/ru%s" %
                                       (proto, domain, b58id),
                                       source=fixedurl)
            else:
                return "%s:/%s/ru%s\n"%(proto,domain,b58id)
    elif 'paste' in bottle.request.params:
        invalid, fixedpaste, fixedtitle = validate_paste(
                         bottle.request.params['paste'] if 'paste' in
                         bottle.request.params else "",
                         bottle.request.params['title'] if 'title' in
                         bottle.request.params else "")
        if invalid:
            if 'button' in bottle.request.params:
                return bottle.template("error", title="Paste Submission Error",
                                       reason=invalid, url = "%s://%s" %
                                       (proto, domain), rurl=None)
            else:
                bottle.response.content_type = "text/plain"
                return "ERROR: Paste Submission Failed.\n%s\n" % invalid
        else:
            if 'p' in bottle.request.params and \
                      bottle.request.params['p'] != "":
                password = bottle.request.params['p']
            else:
                password = None
            
            nextid = incr_data(memory,database,"paste:nextid")
            b58id = b58encode(nextid)

            lexmode = bottle.request.params['format'] if 'format' in \
                      bottle.request.params else "text"
            lexmode = lexmode[:25]
            if lexmode == "guess":
                lexmode = guess_lexer(fixedpaste).name
            elif lexmode in ["", "none", "nothing"]:
                lexmode = "text"
            
            set_data(memory, database, 'paste:' + b58id,
                     msgpack.dumps([fixedpaste.encode("utf-8"),
                     fixedtitle, lexmode, time.time(),
                     sha256(password).digest() if password else None,
                     compactIP(bottle.request.environ['HTTP_X_FORWARDED_FOR']
                     .split(", ")[-1])]))
            if 'button' in bottle.request.params:
                bottle.redirect("%s://%s/p%s"%(proto,domain,b58id))
            else:
                return "%s://%s/rp%s\n"%(proto,domain,b58id)
    
# It's best to override this with a reverse proxy
@route('/static/:filename')
def server_static(filename):
    return bottle.static_file(filename, root='./static')

@route("/u:urlname")
@route("/u:urlname", method="POST")
def url(urlname):
    global data
    memory = Client(memcached)
    database = Client(memcachedb)
    if bottle.request.environ['HTTP_X_FORWARDED_SSL'] == 'on':
        proto = 'https'
    else:
        proto = 'http'
    url = msgpack.loads(get_data(memory,database,"url:"+urlname) or "")
    if url:
        if not url[2]:
            bottle.response.content_type = "text/plain"
            bottle.redirect(url[0], 301)
        else:
            if 'p' in bottle.request.params:
                if sha256(bottle.request.params['p']).digest() == url[2]:
                    bottle.redirect(url[0], 301)
                else:
                    return bottle.template("urlauth",url="%s://%s/u%s" %
                           (proto, domain, urlname), incorrect = True)
            else:
                return bottle.template("urlauth",url="%s://%s/u%s" %
                       (proto, domain, urlname), incorrect = False)
    else:
        raise HTTPError(404, "URL not in database")

@route("/ru:urlname")
@route("/ru:urlname", method="POST")
def rawurl(urlname):
    global data
    memory = Client(memcached)
    database = Client(memcachedb)
    url = msgpack.loads(get_data(memory,database,"url:"+urlname) or "")
    if url:
        if not url[2]:
            bottle.response.content_type = "text/plain;charset=UTF-8"
            return url[0] + '\n'
        else:
            if 'p' in bottle.request.params:
                if sha256(bottle.request.params['p']).digest() == url[2]:
                    bottle.response.content_type = "text/plain;charset=UTF-8"
                    return url[0] + '\n'
                else:
                    raise HTTPError(403, "Password Incorrect")
            else:
                raise HTTPError(403,
                       "Password required - use the format"\
                       "http://%s/ru%s?p=password" % (domain, urlname))
    else:
        raise HTTPError(404, "URL not in database")

@route("/p:pastename")
@route("/p:pastename", method="POST")
def paste(pastename):
    return paste_lexer(pastename)
    
@route("/p:pastename/:lexmode")
@route("/p:pastename/:lexmode", method="POST")
def paste_lexer(pastename,lexmode=None):
    global data, formatter
    memory = Client(memcached)
    database = Client(memcachedb)
    bottle.response.content_type = "text/html;charset=UTF-8"
    if bottle.request.environ['HTTP_X_FORWARDED_SSL'] == 'on':
        proto = 'https'
    else:
        proto = 'http'
    paste = msgpack.loads(get_data(memory,database,"paste:"+pastename) or "")
    if paste:
        if lexmode:
            url="%s://%s/p%s/%s"%(proto,domain,pastename,lexmode)
        else:
            url="%s://%s/p%s"%(proto,domain,pastename)
        rurl="%s://%s/rp%s"%(proto,domain,pastename)
        if not paste[4]:
            lexer_name = (lexmode or paste[2]).lower()
            try:
                lexer = get_lexer_by_name(lexer_name, stripall=True)
            except:
                lexer = get_lexer_by_name('text', stripall=True)
            hlpaste = memory.get("hlcache:%s:%s" % (pastename, lexer_name))
            if hlpaste == None:
                hlpaste = highlight(paste[0].decode("utf-8"), lexer, formatter)
                memory.set("hlcache:%s:%s" % (pastename, lexer_name),
                           hlpaste.encode("utf-8"))
            else:
                hlpaste = hlpaste.decode("utf-8")
            return bottle.template('paste', paste=hlpaste, title=paste[1],
                   url=url, rurl=rurl, passwd=None, lexmode=lexer.name)
        else:
            if 'p' in bottle.request.params:
                if sha256(bottle.request.params['p']).digest() == paste[4]:
                    lexer_name = (lexmode or paste[2]).lower()
                    try:
                        lexer = get_lexer_by_name(lexer_name, stripall=True)
                    except:
                        lexer = get_lexer_by_name('text', stripall=True)
                    hlpaste = memory.get("hlcache:%s:%s" % (pastename,
                                                            lexer_name))
                    if hlpaste == None:
                        hlpaste = highlight(paste[0].decode("utf-8"), lexer,
                                            formatter)
                        memory.set("hlcache:%s:%s" % (pastename, lexer_name),
                                   hlpaste.encode("utf-8"))
                    else:
                        hlpaste = hlpaste.decode("utf-8")
                    return bottle.template('paste', paste=hlpaste,
                                           title=paste[1], url=url, rurl=rurl,
                                           passwd=bottle.request.params['p'],
                                           lexmode=lexer.name)
                else:
                    return bottle.template("pasteauth", url=url, rurl=rurl,
                                           passwd=None, incorrect=True)
            else:
                return bottle.template("pasteauth", url=url, rurl=rurl,
                                       passwd=None, incorrect=False)
    else:
        raise HTTPError(404, "Paste not in database")

@route("/rp:pastename")
@route("/rp:pastename", method="POST")
def rawpaste(pastename):
    global data
    memory = Client(memcached)
    database = Client(memcachedb)
    paste = msgpack.loads(get_data(memory,database,"paste:"+pastename) or "")
    if paste:
        if not paste[4]:
            bottle.response.content_type = "text/plain"
            return paste[0] + '\n'
        else:
            if 'p' in bottle.request.params:
                if sha256(bottle.request.params['p']).digest() == paste[4]:
                    bottle.response.content_type = 'text/plain'
                    return paste[0] + '\n'
                else:
                    raise HTTPError(403, "Password Incorrect")
            else:
                raise HTTPError(403, "Password required - use the format"\
                                "http://%s/rp%s?p=password"%(domain,pastename))
    else:
        raise HTTPError(404, "Paste not in database")

# Quick way to check your IP address and reverse DNS - not needed for 3d3Paste
@route("/i")
def getip():
    bottle.response.content_type = 'text/plain'
    output = ""
    for i in bottle.request.environ['HTTP_X_FORWARDED_FOR'].split(", "):
        output += "%s - %s\n" % (i, socket.getfqdn(i))
    return output

# drop privileges
pe = pwd.getpwnam("http")
os.setgid(pe.pw_gid)
os.setuid(pe.pw_uid)
        
bottle.debug(True)
bottle.run(host="127.0.0.1", port=55230+int(sys.argv[1]), server="fapws3")
