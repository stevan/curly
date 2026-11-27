# kind: refused
# perl leaves the for each time next runs, and prints 'end 7' (T64).
use v5.42;
my $i = 0;
for my $k (1 .. 3) {
    do {
        $i++;
        next if $i == 2;
    } until ($i > 5);
}
say "end $i";
