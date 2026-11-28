use v5.42;
use feature 'defer';
no warnings 'experimental::defer';

our $defer_ran = 0;
sub named_sub_ending_in_defer {
    defer { $defer_ran++ }
}

my $result = named_sub_ending_in_defer();
say((!defined($result)) ? "ok" : "not ok");
say $defer_ran;

