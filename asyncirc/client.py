__author__ = 'Michael Stella <asyncirc@thismetalsky.org>'
__version__ = '0.1'

__all__ = ['IRCClient']

import re, sys
import tulip

from . import buffer
from . import events

class IRCError(Exception): pass
class InvalidCharacters(ValueError): pass
class MessageTooLong(ValueError): pass
class NotConnected(IRCError): pass

rfc_1459_command_regexp = re.compile("^(:(?P<prefix>[^ ]+) +)?(?P<command>[^ ]+)( *(?P<argument> .+))?")

class IRCClient(object):
    """IRC Client object"""

    def __init__(self, host, port=6667, ssl=False,
                 nickname='monkey', username=None, ircname=None):
        assert isinstance(port, int)

        self.host = host
        self.port = port
        self.ssl = ssl

        self.nickname = nickname
        self.username = username or nickname
        self.ircname  = ircname or nickname

        self.real_server_name = None

        self.buffer = buffer.LineBuffer()

        self.loop = tulip.get_event_loop()


    def run(self):
        tulip.Task(self.loop.create_connection(lambda: self, self.host, self.port, ssl=self.ssl))
        self.loop.run_forever()


    def disconnect(self, message=''):
        self.connected = False
        self.quit(message)
        self.loop.stop()


    ### Tulip responses ###

    def connection_made(self, transport):
        self.transport = transport
        self.on_connect()

        # logon to IRC
        self.nick(self.nickname)
        self.user(self.username, self.ircname)



    def connection_refused(self, exc):
        print('*** connection refused: {0}'.format(exc))


    def connection_lost(self, exc):
        print('*** connection lost: {0}'.format(exc))
        self.on_disconnect()
        self.loop.stop()


    def data_received(self, data):
        self.buffer.feed(data.decode())
        for line in self.buffer:
            if not line:
                continue
            self._handle_line(line)


    def eof_received(self):
        print('*** connection closed')
        self.on_disconnect()
        self.loop.stop()

    ### Process IRC messages ###

    def _handle_line(self, line):
        """Handle an incoming IRC message"""

        prefix=None
        command=None
        args=None

        m = rfc_1459_command_regexp.match(line)
        if m.group('prefix'):
            prefix=m.group('prefix')
            if not self.real_server_name:
                self.real_server_name = prefix

        if m.group('command'):
            command = m.group('command').lower()

        if m.group('argument'):
            a = m.group('argument').split(' :', 1)
            args = a[0].split()
            if len(a) == 2:
                args.append(a[1])


        command = events.numeric.get(command, command)
        if not command:
            return

        # record the nickname
        if command == 'welcome':
            self.real_nickname = args[0]

        # handle privmsg/notice special to split out the CTCP stuff
        if command in ('privmsg', 'notice'):
            self._on_message(command, prefix, args)

        # otherwise, find a handler, and call it
        else:

            response = None
            handler = getattr(self, 'on_%s' % command.lower(), None)
            if handler:
                response = handler(prefix, args)

                if response:
                    self._send(response)

            else:
                print('?? p: {0} c:{1} a: {2}'.format(prefix, command, args))


    def _send(self, msg):
        """Raw message send"""

        if '\n' in msg:
            raise InvalidCharacters()

        if len(msg) > 510:
            raise MessageTooLong()

        if not self.transport:
            raise NotConnected()

        print("D** {0}".format(msg))
        msg = msg + '\r\n'
        self.transport.write(msg.encode())

    ### Special IRC Handlers ###
    def _on_message(self, command, prefix, args):
        """Handle private messages by stripping out the CTCP stuff first
            msg: ['#test', 'yo']
            action: ['#test', '\x01ACTION yawns\x01']
        """

        # ahh, CTCP here, we'll strip it
        if '\x01' in args[1]:
            line = args[1].strip('\x01')
            command = ''
            msg = ''
            if ' ' in line:
                command, msg = line.split(' ', 1)
            else:
                command = line

            args[1] = msg

            self._on_ctcp(command, prefix, args)

        # normal messages
        else:
            handler = getattr(self, 'on_%s' % command.lower(), None)
            if handler:
                handler(prefix, args)


    def _on_ctcp(self, command, prefix, args):
        """Handle common CTCP messages"""

        handler = getattr(self, 'on_ctcp_%s' % command.lower(), None)
        if handler:
            handler(prefix, args)




    ### Default IRC Handlers ###
    def on_connect(self, *args):
        print("*** connected to {0}:{1}".format(self.host, self.port))

    def on_error(self, prefix, params):
        print("*** Error: {0}".format(' '.join(params)))

    def on_notice(self, prefix, params):
        print("*** NOTICE: {0}".format(' '.join(params)))


    def on_ctcp_ping(self, prefix, args):
        nick = prefix_nick(prefix)
        print('*** CTCP PING request from {0}'.format(nick))
        self.ctcp_reply(nick, 'PING', args[1])

    def on_ctcp_version(self, prefix, args):
        nick = prefix_nick(prefix)
        print('*** CTCP Version request from {0}'.format(nick))
        self.ctcp_reply(nick, 'VERSION', 'AsyncIRC {0}'.format(__version__))


    # you probably will overload these
    def on_disconnect(self):                    pass
    def on_privmsg(self, prefix, args):         pass
    def on_ctcp_action(self, prefix, args):     pass
    def on_ctcp_version(self, prefix, args):    pass



    ### IRC Actions ###
    def action(self, target, action):
        self.ctcp('ACTION', target, action)

    def ctcp(self, target, ctcptype, param=''):
        ctcptype = ctcptype.upper()
        self.privmsg(target, '\001{0}{1}\001'.format(ctcptype, param and (' ' + param) or ''))

    def ctcp_reply(self, target, ctcptype, param=''):
        #self.notice(target, '\001{0}\001'.format(param))
        ctcptype = ctcptype.upper()
        self.notice(target, '\001{0}{1}\001'.format(ctcptype, param and (' ' + param) or ''))

    def join(self, channel, key=''):
        self._send('JOIN {0}{1}'.format(channel, (key and (' ' + key))))

    def mode(self, target, cmd):
        self._send('MODE {0} {1}'.format(target, cmd))

    def names(self, channels=None):
        self._send('NAMES' + (channels and (' ' + ','.join(channels))))

    def nick(self, newnick):
        """Set nickname"""
        self._send('NICK ' + newnick)

    def notice(self, target, text):
        self._send('NOTICE {0} :{1}'.format(target, text))

    def passwd(self, password):
        self._send('PASS ' + password)

    def ping(self, target, t2=''):
        self._send('PING {0}{1}'.format(target, target2 and (' ' + target2)))

    def pong(self, target, t2=''):
        self._send('PONG {0}{1}'.format(target, target2 and (' ' + target2)))

    def privmsg(self, target, text):
        self._send('PRIVMSG {0} :{1}'.format(target, text))

    def quit(self, message=''):
        self._send('QUIT' + (message and (' :' + message)))

    def user(self, username, realname):
        self._send('USER {0} 0 * :{1}'.format(username, realname))

    def userhost(self, nicks):
        self._send('USERHOST ' + ','.join(nicks))

    def version(self, server=""):
        self._send('VERSION' + (server and (' ' + server)))