# t/models/io.py 4707
# stdin: \0303\0251\n\0351\n\0000A\nA\0015\n\0377
use v5.42;
while (my $line = <STDIN>) {
    my @ords;
    for my $i (0 .. length($line) - 1) { push @ords, ord(substr($line, $i, 1)); }
    say length($line), ": @ords";
}
