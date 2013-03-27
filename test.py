
import re, sys
from asyncirc import IRCClient, prefix_nick

class Client(IRCClient):

    def on_connect(self):
        print("*** connected to {0}:{1}".format(self.host, self.port))

    def on_ctcp_action(self, prefix, args):
        nick = prefix_nick(prefix)
        target, msg = args[0], args[1]
        print('* {0}/{1} {2}'.format(nick, target, msg))


    def on_ctcp_version(self, prefix, args):
        nick = prefix_nick(prefix)
        print('*** CTCP Version request from {0}'.format(nick))
        self.ctcp_reply(nick, 'VERSION', 'irssi v0.8.15 - running on OpenBSD x86_64')


    def on_error(self, prefix, params):
        print("*** Error: {0}".format(' '.join(params)))


    def on_join(self, prefix, args):
        nick = prefix_nick(prefix)
        target = args[0]

        if nick == self.nick:
            print('*** joined channel {0}'.format(target))
        else:
            print('*** {0} has joined channel {1}'.format(nick, target))


    def on_kick(self, prefix, args):
        nick = prefix_nick(prefix)
        target, who, msg = args

        print("*** {0} was kicked from {1} by {2} [{3}]".format(who, target, nick, msg))


    def on_mode(self, prefix, args):
        target = args.pop(0)
        mode   = ' '.join(args)

        changer = prefix_nick(prefix)
        if target.startswith('#'):
            print('*** {0} sets mode {1} {2}'.format(changer, target, mode))
        else:
            print('*** {0} sets mode {1} {0}'.format(changer, mode))


    def on_notice(self, prefix, params):
        print("*** NOTICE: {0}".format(' '.join(params)))


    def on_part(self, prefix, args):
        nick = prefix_nick(prefix)
        target = args[0]

        print('*** {0} has left channel {1}'.format(nick, target))


    def on_privmsg(self, prefix, args):
        nick = prefix_nick(prefix)
        target, msg = args[0], args[1]

        print('<{0}/{1}> {2}'.format(nick, target, msg))


    def on_welcome(self, prefix, args):
        self.join('#test')



    ## overload stuff for logging
    def action(self, target, action):
        print('* {0}/{1} {2}'.format(self.nickname, target, action))
        super().action(target, action)

    def privmsg(self, target, text):
        print('<{0}/{1}> {2}'.format(self.nickname, target, text))
        super().privmsg(target, text)



if __name__ == '__main__':
    conn = Client(sys.argv[1], int(sys.argv[2]))
    try:
        conn.run()
    except KeyboardInterrupt:
        conn.disconnect("Caught SIGINT")
        sys.exit(0)

