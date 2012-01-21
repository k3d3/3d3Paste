# 3d3Paste
3d3Paste is a simple, basic pastebin solution. It provides syntax highlighting and the ability to protect pastes with passwords.
Paste URLs are also encded with base58 to ensure the URLs are short and memorable

# Technologies
We use Python 2, Bottlepy (transitioning to Flask), Pygments for syntax highlighting, and currently Fapws3 as a web server.
For the storage of pastes and URLs, we use memcachedb and memcached with the cmemcached python plugin, however we are working to make this more modular.
All pastes and URLs are serialized with MsgPack.

# Installation and configuration
Currently you need Python 2.7 along with the Bottlepy, Pygments, MsgPack, cmemcached and FapWS3 modules. FapWS3 can be replaced with any WSGI server given some work. The majority of these, if not all of them, can be installed through pip.
Along with those modules, you need memcached and memcachedb servers running. Again, we are working to make this more modular.

We have a configuration that load balances among 4 instances, therefore we have included 3 scripts, start_3d3p.sh, kill_3d3p.sh and watch_3d3p.sh, as examples of how to use 3d3Paste.
You may also need to create an http user and group.

# Demo
We have a live 3d3Paste running at http://3d3.ca/

# Usage
Usage for 3d3Paste is simple. You can visit the website, enter a URL or paste, set the desired settings, and submit. That paste will now be available to anyone you give the link to, unless you set a password.

In addition to the web interface, it's also possible to submit pastes via cURL. To submit a paste:
`$ cat testing.txt | curl http://3d3.ca/ -F "paste=<-" -F "format=text" -F "p=mypassword" -F "title=mytitle"`
`http://3d3.ca/rpa`
This will return a link to the paste in raw form. You may also remove the initial r to access the web version of the paste, for example `http://3d3.ca/pa`
The format, password and title are all optional. You may also remove the initial r to access the web version of the paste.

To submit a URL to shorten:
`$ echo http://www.example.com | curl http://3d3.ca -F "url=<-" -F "p=mypassword"`
`http://3d3.ca/ruv`
This will return a shortened link in raw form. A URL in raw form will be returned in plaintext rather than automatically forwarding.
You can be redirected by removing the initial r, for example `http://3d3.ca/uv`

# Additional Features
We have also included a simple page to show your IP and reverse DNS, at `http://3d3.ca/i`
You may remove this in the code if you feel the need.

# License
3d3Paste is released under the GPLv2. Absolutely no warranty, explicit or implied, is available. Read the header in 3d3paste.py for more information.
