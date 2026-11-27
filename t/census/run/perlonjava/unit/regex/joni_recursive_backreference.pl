use v5.42;

my $match = 'abbaccaddedcb' =~ /(?:\1|a)([bcd])\1(?:(?R)|e)\1/ ? $& : undef;
say $match;

