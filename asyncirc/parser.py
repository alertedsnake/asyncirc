__author__ = 'Kiyoshi Aman'

def parse(input):
    """Parse an IRC message.

    >>> parse('@foo=bar :lol!lol@example.com PRIVMSG #lol :lol')
    ({u'@foo': u'bar'}, u':lol!lol@example.com', u'PRIVMSG', [u'#lol', u':lol'])
    """
    if isinstance(input, bytes):
        input = input.decode('UTF-8', 'replace')

    string = input.split(' ')

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

    if string[0].startswith(':'):
        prefix = string[0][1:]
        string = string[1:]
    else:
        prefix = ''

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
