"""Case files written by hand share this: a block of text, programs parted
by a line of `----`, each named by its place."""


def split(prefix, text):
    n = 0
    for part in text.split('\n----\n'):
        part = part.strip('\n')
        if part:
            n += 1
            yield ('%s%03d' % (prefix, n), part + '\n')
