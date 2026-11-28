use v5.42;

say "@^";
say "@^foo";

my @array = qw(one two);
say "@array";

my $safe_char = qr|[^\w!%+,\-./:=@^]|;
say(('x' !~ $safe_char) ? "ok" : "not ok");
say(('*' =~ $safe_char) ? "ok" : "not ok");

