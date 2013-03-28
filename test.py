
import datetime, re, sys
from asyncirc import IRCClient

class Client(IRCClient):

    def on_connect(self):
        print("*** connected to {0}:{1}".format(self.host, self.port))


    def on_ctcp_action(self, event):
        print('* {0}/{1} {2}'.format(event.source, event.target, event.args[0]))


    def on_ctcp_version(self, event):
        print('*** CTCP Version request from {0}'.format(event.source))
        self.ctcp_reply(event.source, 'VERSION', 'irssi v0.8.15 - running on OpenBSD x86_64')


    def on_error(self, event):
        print("*** Error: {0}".format(' '.join(event.args)))


    def on_join(self, event):

        if event.source == self.nickname:
            print('*** joined channel {0}'.format(event.target))
        else:
            print('*** {0} has joined channel {1}'.format(event.source, event.target))


        # TODO run some tests upon joining #test
        if (event.source == self.nickname and event.target == '#test'):
            self.run_tests(event.target)


    def on_kick(self, event):
        print("*** {0} was kicked from {1} by {2} [{3}]".format(
                event.args[0], event.target, event.source, event.args[1]))


    def on_mode(self, event):
        mode  = ' '.join(event.args)

        if event.target.startswith('#'):
            print('*** {0} sets mode {1} {2}'.format(event.source, event.target, mode))
        else:
            print('*** {0} sets mode {1} {0}'.format(event.source, mode))


    def on_notice(self, event):
        print("*** NOTICE: {0}".format(' '.join(event.args)))


    def on_part(self, event):
        print('*** {0} has left channel {1}'.format(event.source, event.target))


    def on_privmsg(self, event):

        print('<{0}/{1}> {2}'.format(event.source, event.target, event.message))

        # TODO handle commands and such
        if event.source == 'michael' and event.message.startswith(self.nickname + ':'):
            msg = event.message.lstrip(self.nickname + ':').lstrip()

            if msg.startswith('quit'):
                self.privmsg(event.target, "Okay, {0}.  Seeya.".format(event.source))
                self.quit()

            elif msg.startswith('join'):
                m = re.match('join\s+(#\S+)')
                if m:
                    self.join(m.group(0))

            elif msg.startswith('part'):
                m = re.match('part\s+(#\S+)')
                if m:
                    self.part(m.group(0))


    def on_topic(self, event):
        print('*** Topic change for {0} by {1}: {2}'.format(
                event.target, event.source, event.args[0]))


    def on_welcome(self, event):
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
        self.privmsg_at(datetime.datetime.now() + datetime.timedelta(minutes=2),
                        target, "test 02: at message")



if __name__ == '__main__':
    conn = Client(sys.argv[1], int(sys.argv[2]))
    try:
        conn.run()
    except KeyboardInterrupt:
        conn.quit("Caught SIGINT")
        sys.exit(0)

