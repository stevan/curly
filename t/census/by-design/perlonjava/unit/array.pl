use v5.42;

# Array creation and assignment
my @array = (1, 2, 3, 4, 5);
say scalar @array;
say $array[0];
say $array[4];

# Array length
my $length = scalar @array;
say $length;

# Push operation
push @array, 6;
say $array[-1];
say scalar @array;

# Pop operation
my $popped = pop @array;
say $popped;
say scalar @array;

# Shift operation
my $shifted = shift @array;
say $shifted;
say scalar @array;
say $array[0];

# Unshift operation
unshift @array, 0;
say $array[0];
say scalar @array;

# Splice operation
splice @array, 2, 1, (10, 11);
say scalar @array;
say $array[2];
say $array[3];

# Slice operations
{
    my @slice = @array[1..3];
    say scalar @slice;
    say $slice[0];
    say $slice[2];
}

{
    my $array = \@array;
    my @slice = @$array[1..3];
    say scalar @slice;
    say $slice[0];
    say $slice[2];
}

# Negative indexing
say $array[-1];
say $array[-2];

# Array to scalar context
my $scalar = @array;
say $scalar;

# Foreach loop
my $sum = 0;
foreach my $elem (@array) {
    $sum += $elem;
}
say $sum;

# Map operation
my @doubled = map { $_ * 2 } @array;
say scalar @doubled;
say $doubled[0];
say $doubled[-1];

# Grep operation
my @evens = grep { $_ % 2 == 0 } @array;
say scalar @evens;
say $evens[0];
say $evens[-1];

# Sort operation
my @sorted = sort { $a <=> $b } @array;
say scalar @sorted;
say $sorted[0];
say $sorted[-1];

# Reverse operation
my @reversed = reverse @array;
say scalar @reversed;
say $reversed[0];
say $reversed[-1];

# Array of arrays
my @matrix = ([1, 2], [3, 4], [5, 6]);
say $matrix[1][0];
say $matrix[2][1];

# Autovivification
$matrix[3][0] = 7;
say $matrix[3][0];

# Join operation
my $joined = join ", ", @array;
say $joined;

# Split operation
my @split = split ", ", $joined;
say scalar @split;
say $split[0];
say $split[-1];

# Slice assignment
@array[1, 3, 5] = (20, 30, 40);
say $array[1];
say $array[3];
say $array[5];

# Verify slice assignment
my @new_slice = @array[1, 3, 5];
say scalar @new_slice;
say $new_slice[0];
say $new_slice[2];
