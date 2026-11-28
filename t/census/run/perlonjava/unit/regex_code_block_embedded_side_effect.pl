use v5.42;

my $count = 0;
my $regex = qr/f(?{ ++$count })oo/;

say(('foo' =~ $regex) ? "ok" : "not ok");
say(($count > 0) ? "ok" : "not ok");

