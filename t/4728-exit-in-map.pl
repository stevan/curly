# t/models/io.py 4728
use v5.42;
sub f($n) { exit 5 if $n == 2; return $n }
my @a = map { f($_) } 1 .. 3;
say "no";
