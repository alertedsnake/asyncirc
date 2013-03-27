
import datetime, re, sys
from asyncirc import IRCClient

class Client(IRCClient):

    def on_connect(self):
        print("*** connected to {0}:{1}".format(self.host, self.port))

    def on_ctcp_action(self, prefix, args):
        target, msg = args[0], args[1]
        print('* {0}/{1} {2}'.format(prefix['nick'], target, msg))


    def on_ctcp_version(self, prefix, args):
        nick = prefix['nick']
        print('*** CTCP Version request from {0}'.format(nick))
        self.ctcp_reply(nick, 'VERSION', 'irssi v0.8.15 - running on OpenBSD x86_64')


    def on_error(self, prefix, params):
        print("*** Error: {0}".format(' '.join(params)))


    def on_join(self, prefix, args):
        nick = prefix['nick']
        target = args[0]

        if nick == self.nickname:
            print('*** joined channel {0}'.format(target))
        else:
            print('*** {0} has joined channel {1}'.format(nick, target))


        # TODO run some tests upon joining #test
        if (nick == self.nickname and target == '#test'):
            self.run_tests(target)


    def on_kick(self, prefix, args):
        target, who, msg = args

        print("*** {0} was kicked from {1} by {2} [{3}]".format(who, target, prefix['nick'], msg))


    def on_mode(self, prefix, args):
        target = args.pop(0)
        mode   = ' '.join(args)

        changer = prefix['nick']
        if target.startswith('#'):
            print('*** {0} sets mode {1} {2}'.format(changer, target, mode))
        else:
            print('*** {0} sets mode {1} {0}'.format(changer, mode))


    def on_notice(self, prefix, params):
        print("*** NOTICE: {0}".format(' '.join(params)))


    def on_part(self, prefix, args):
        print('*** {0} has left channel {1}'.format(prefix['nick'], args[0]))


    def on_privmsg(self, prefix, args):
        nick = prefix['nick']
        target, msg = args[0], args[1].strip()

        print('<{0}/{1}> {2}'.format(nick, target, msg))


        # TODO handle commands and such
        if nick == 'michael' and msg.startswith(self.nickname + ':'):
            msg = msg.lstrip(self.nickname + ':').lstrip()

            if msg.startswith('quit'):
                self.privmsg(target, "Okay, {0}.  Seeya.".format(nick))
                self.quit()

            elif msg.startswith('join'):
                m = re.match('join\s+(#\S+)')
                if m:
                    self.join(m.group(0))

            elif msg.startswith('part'):
                m = re.match('part\s+(#\S+)')
                if m:
                    self.part(m.group(0))



    def on_welcome(self, prefix, args):
        self.join('#test')


    ## overload stuff for logging outgoing messages
    def action(self, target, action):
        print('* {0}/{1} {2}'.format(self.nickname, target, action))
        super().action(target, action)

    def privmsg(self, target, text):
        print('<{0}/{1}> {2}'.format(self.nickname, target, text))
        super().privmsg(target, text)


    ### testing routines ###
    def run_tests(self, target):

        # test some delayed/at methods
        self.privmsg_delayed(60, target, "test 01: delayed message")
        self.privmsg_at(datetime.datetime.now() + datetime.timedelta(minutes=2), target, "test 02: at message")



if __name__ == '__main__':
    conn = Client(sys.argv[1], int(sys.argv[2]))
    try:
        conn.run()
    except KeyboardInterrupt:
        conn.disconnect("Caught SIGINT")
        sys.exit(0)

