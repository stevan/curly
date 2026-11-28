# stdin: a\nb\nc\n
# A sub that ends in chomp(my $x = EXPR), called for nothing, is as perl
# has it (T522).
use v5.42;
my @seen;
sub take() { chomp(my $l = <STDIN>); push @seen, $l; chomp(my $m = <STDIN>) }
take();
say "@seen";
print <STDIN>;
