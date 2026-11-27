use v5.42;

# Test for scalar flip-flop using two dots (..)
my @left_ops = (0, 1, 0, 0, 0);
my @right_ops = (0, 0, 0, 1, 0);
my $flipflop = 0;
my @expect = ("", "1", "2", "3E0", "");

foreach my $i (0..$#left_ops) {
    $flipflop = $left_ops[$i] .. $right_ops[$i];
    say $flipflop;
}

# Test for scalar flip-flop using three dots (...)
my @three_dot_left_ops = (0, 1, 0, 0, 0);
my @three_dot_right_ops = (0, 0, 0, 1, 0);
my $three_dot_flipflop = 0;
@expect = ("", "1", "2", "3E0", "");

foreach my $i (0..$#three_dot_left_ops) {
    $three_dot_flipflop = $three_dot_left_ops[$i] ... $three_dot_right_ops[$i];
    say $three_dot_flipflop;
}

# Test for sequence number generation in flip-flop
my @left_seq_ops = (0, 1, 0, 0, 0);
my @right_seq_ops = (0, 0, 0, 1, 0);
my $seq_flipflop = 0;
@expect = ("", "1", "2", "3E0", "");

foreach my $i (0..$#left_seq_ops) {
    $seq_flipflop = $left_seq_ops[$i] .. $right_seq_ops[$i];
    say $seq_flipflop;
}

# Test for deferred right operand evaluation in three dots (...)
my @deferred_left_ops = (0, 1, 0, 0, 0);
my @deferred_right_ops = (0, 0, 0, 1, 0);
my $deferred_flipflop = 0;
@expect = ("", "1", "2", "3E0", "");

foreach my $i (0..$#deferred_left_ops) {
    $deferred_flipflop = $deferred_left_ops[$i] ... $deferred_right_ops[$i];
    say $deferred_flipflop;
}

