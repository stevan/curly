"""POD, __END__ and __DATA__ at every line's start of programs written a
token to a line, and the lines that may begin or end POD (D255)."""

BASES = [
    ['my', '$x', '=', '5', ';', 'say', '$x', ';', 'my', '@a', '=', '(', '1', ',', '2', ')', ';', 'say', '"@a"', ';'],
    ['sub f', '(', '$p', ')', '{', 'return', '$p', '+', '1', ';', '}', 'say', 'f(1)', ';'],
    ['my $i = 0;', 'if', '(', '$i', '==', '0', ')', '{', 'say "a";', '}', 'elsif', '(', '$i', ')', '{', 'say "b";', '}', 'else', '{', 'say "c";', '}', 'say "d";'],
    ['my $i = 0;', 'L:', 'for', 'my', '$k', '(', '1', '..', '2', ')', '{', '$i++', ';', 'next', 'L', 'if', '$k', ';', '}', 'say $i;'],
    ['my $i = 0;', 'do', '{', '$i++', ';', '}', 'while', '(', '$i < 2', ')', ';', 'say $i;'],
    ['my $h =', '{', 'a', '=>', '1', ',', '}', ';', 'my @l =', 'map', '{', '$_ * 2', '}', '1, 2', ';', 'say "@l";', 'try', '{', 'die "x\\n";', '}', 'catch', '($e)', '{', 'print $e;', '}'],
    ['my $i = 0;', 'for', '(', '$i = 0', ';', '$i < 2', ';', '$i++', ')', '{', '}', 'while', '(', '$i < 4', ')', '{', '$i++;', '}', 'say $i;', 'my $f =', 'sub', '{', 'return 7;', '}', ';', 'say $f->();', '{', 'say "bare";', '}', 'say "end"', ';'],
]

INSERTS = [
    ('p', '=pod\n\ntext\n\n=cut\n'),
    ('e', '__END__\n'),
    ('d', '__DATA__\n'),
]

STARTS = ['=pod', '=head1 X', '=cut', '=a', '=A', '=z9', '=_x', '=9', '=é', '= pod', '==pod', '=pod=cut', '=begin', '=end', '=for x', '=encoding utf8', '=item *', '=over', '=back', '=x_y', '=X-', '=x=']
ENDS = ['=cut', '=cut ', '=cut\t', '=cut x', '=cut9', '=cut_', '=cutx', '=cut-', '=cut=', '=cut;', '=CUT', '=Cut', ' =cut', '=cu', '=cut\r', '=cuté', '=cut.', '=cut#', '=cut say 9;']


def cases():
    for b, base in enumerate(BASES):
        for at in range(len(base) + 1):
            for tag, text in INSERTS:
                lines = base[:at] + [text.rstrip('\n')] + base[at:]
                yield ('b%d-%s%02d' % (b, tag, at), '\n'.join(lines) + '\n')
    for n, s in enumerate(STARTS):
        yield ('start%02d' % n, 'say 1;\n%s\nsay 2;\n=cut\nsay 3;\n' % s)
        yield ('startb%02d' % n, 'say 1;\n%s\nsay 2;\n' % s)
    for n, e in enumerate(ENDS):
        yield ('end%02d' % n, 'say 1;\n=pod\nsay 2;\n%s\nsay 3;\n=cut\nsay 4;\n' % e)
        yield ('endb%02d' % n, 'say 1;\n=pod\nsay 2;\n%s\nsay 3;\n' % e)
    for n, e in enumerate(['__END__', '__DATA__', '__END__ x', '__END__;', '__END__#c', ' __END__', '__END__\r', '__END', '__END___', '__end__', '__DATA__ 5', 'say 2; __END__', '__END__ say 2;', '__DATA__;']):
        yield ('fin%02d' % n, 'say 1;\n%s\nsay 3;\n' % e)
    # no newline at the file's end
    yield ('nonl-pod', 'say 1;\n=pod')
    yield ('nonl-cut', 'say 1;\n=pod\n=cut')
    yield ('nonl-end', 'say 1;\n__END__')
    yield ('crlf-pod', 'say 1;\r\n=pod\r\nsay 2;\r\n=cut\r\nsay 3;\r\n')
