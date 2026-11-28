use v5.42;
my $a = {
   tiny   => -2,
   small  => -1,
   normal => 0,
   big    => 1,
   huge   => 2
};

say sort { $a->{our $a} <=> $a->{our $b} }
    qw{ huge normal tiny small big};

# prints tinysmallnormalbighuge
