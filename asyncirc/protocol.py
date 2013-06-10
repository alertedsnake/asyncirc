"""
IRC message parser by Aerdan, used with permission.
parse_prefix() added by me.

"""
__author__ = ['Kiyoshi Aman', 'Michael Stella']

commands_without_target = ['quit','ping','squit','error']

def parse(input):
    """Parse an IRC message.

    >>> parse('@foo=bar :lol!lol@example.com PRIVMSG #lol :lol')
    ({'@foo': 'bar'}, ':lol!lol@example.com', 'PRIVMSG', ['#lol', ':lol'])
    """
    if isinstance(input, bytes):
        input = input.decode('UTF-8', 'replace')

    string = input.split(' ')

    # handle tags
    if string[0].startswith('@'):
        tag_str = string[0][1:]
        string = string[1:]

        tag_str = tag_str.split(',')
        tags = {}

        for tag in tag_str:
            k, v = tag.split('=', 1)
            tags[k] = v
    else:
        tags = {}

    # handle prefix
    if string[0].startswith(':'):
        prefix = string[0][1:]
        string = string[1:]
    else:
        prefix = ''

    # handle verb and arguments
    verb = string[0]
    args = string[1:]

    for arg in args:
        if arg.startswith(':'):
            idx  = args.index(arg)
            arg  = ' '.join(args[idx:])
            arg  = arg[1:]
            args = args[:idx]

            args.append(arg)

            break

    return (tags, prefix, verb, args)


def parse_prefix(prefix):
    """Split up the prefix into parts"""

    # server messages won't have user info
    if not prefix or '!' not in prefix:
        return (None, None, None)

    nick, userhost = prefix.lstrip('~').split('!')
    user, host = userhost.split('@')

    return (nick, user, host)


def create_prefix(nick, user, host):
    """Create a prefix from nick, user, host"""
    return '{0}!{1}@{2}'.format(nick, user, host)

