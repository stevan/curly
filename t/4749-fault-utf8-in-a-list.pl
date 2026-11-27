# t/models/io.py 4749
# kind: fault
# stdin: one\ntwo\n\0377\n
use v5.42;
use open ':std', ':encoding(UTF-8)';
say "start";
my @all = <STDIN>;
say "not reached";
