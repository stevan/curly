use v5.42;
my (@colors);
# Return value is the number of items in the updated array
my $color_count = unshift(@colors, ("yellow", "purple"));

say "There are $color_count colors in the updated array";
