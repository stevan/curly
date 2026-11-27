use v5.42;
sub nary_print {
  my $n = shift;
  while (my @next_n = splice @_, 0, $n) {
    say join q{ -- }, @next_n;
  }
}

nary_print(3, qw(a b c d e f g h));
# prints:
#   a -- b -- c
#   d -- e -- f
#   g -- h
