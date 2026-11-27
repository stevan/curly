# perl runs the block before the first test. It is not a loop to perl
# (T64): D58 left it out, and D253 takes it in, with no last or next of
# its own.
use v5.42;
my $i = 0;
do {
    $i++;
} while ($i < 3);
say $i;
