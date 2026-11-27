# t/models/io.py 4709
# stdin: one\ntwo
use v5.42;
say eof(STDIN) ? "end" : "more";
my $a1 = <STDIN>;
say eof(STDIN) ? "end" : "more";
my $a2 = <STDIN>;
say eof(STDIN) ? "end" : "more";
print $a1, $a2, "\n";
say "still" unless eof(STDIN);
say "at the end" if eof(STDIN);
my $more = 0;
until (eof(STDIN)) { my $l = <STDIN>; $more++; }
say $more;
