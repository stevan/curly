# What step 19 first faulted at (T568): a match that fails after a repeat,
# on a long string. perl says no at once, and so does the matcher since it
# remembers where it has been (D240): each is far past ten million steps
# for a machine that tries every start and every length.
use v5.42;
my $x = "x" x 300000;
say $x =~ /x+y/ ? 1 : 0;
say $x =~ /x*y/ ? 1 : 0;
say $x =~ /x+?y/ ? 1 : 0;
say $x =~ /(x+)y/ ? 1 : 0;
say $x =~ /(?:x|y)+z/ ? 1 : 0;
say $x =~ /x{2,}y/ ? 1 : 0;
say $x =~ /[a-z]+\d/ ? 1 : 0;
say $x =~ /\w+\./ ? 1 : 0;
say $x =~ /.*b/ ? 1 : 0;
say $x =~ /.+?b/ ? 1 : 0;
say $x =~ /.*b/s ? 1 : 0;
say $x =~ /(x+)+y/ ? 1 : 0;
say $x =~ /(?:x+)+y/ ? 1 : 0;
say $x =~ /^(?:x|xx)*y/ ? 1 : 0;
say $x =~ /(?:x|xx)*y/ ? 1 : 0;
my $blanks = (" " x 300000) . "x";
say $blanks =~ /\s+$/ ? 1 : 0;
say $blanks =~ /\s+\z/ ? 1 : 0;
say $blanks =~ / +\t/ ? 1 : 0;
my $digits = "7" x 300000;
say $digits =~ /\d+\./ ? 1 : 0;
say $digits =~ /(\d+)\.(\d+)/ ? 1 : 0;
say $digits =~ /\b\d+\b,/ ? 1 : 0;
# And the lists are empty.
my @l = ($x =~ /(x+)y/);
say scalar(@l);
@l = ($x =~ /x+y/g);
say scalar(@l);
@l = ($blanks =~ /(\s+)$/g);
say scalar(@l);
# perl's answer is no for each of these too, and each match is one that
# a matcher with no memory takes for ever over (T555).
my $as = ("a" x 5000) . "b";
say $as =~ /^(?:a|aa)*$/ ? 1 : 0;
say $as =~ /^(?:a|aa)+$/ ? 1 : 0;
say $as =~ /^(a+)+$/ ? 1 : 0;
say $as =~ /^(?:a*)a*a*a*a*c/ ? 1 : 0;
say $as =~ /^(?:a|a)+$/ ? 1 : 0;
say $as =~ /^(?:a|aa)*b$/ ? 1 : 0;
# Forty choices of two, each a place more than one way leads to.
my $forty = "a" x 40;
say $forty =~ /^(?:a|a){40}c/ ? 1 : 0;
say $forty =~ /^a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?c/ ? 1 : 0;
say $forty =~ /^(?:a{1,3}){14}c/ ? 1 : 0;
