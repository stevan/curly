# sort with its bracket hard against the word: the bracketed list, sorted, as without them (D262).
use v5.42;
my @x = (3, 1, 2);
my %h = (b => 1, a => 2);
say join "", sort(@x);
say join "", sort(@x, 0);
say join ",", sort(keys %h);
say join ",", sort(values %h);
say join "", sort({ $b <=> $a } @x);
say join ",", sort(reverse @x);
say join ",", sort(map { $_ * 2 } @x);
my @s = (sort(@x), 9);
say "@s";
@x = sort(@x);
say "@x";
for my $k (sort(keys %h)) {
    say $k;
}
