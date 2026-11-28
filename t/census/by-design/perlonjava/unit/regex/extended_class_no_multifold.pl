use v5.42;
use utf8;

no warnings 'experimental::regex_sets';

my $sharp_s = qr/\A(?[ [\x{00df}] ])\z/iu;
say(("\x{00df}" =~ $sharp_s) ? "ok" : "not ok");
say(("\x{1e9e}" =~ $sharp_s) ? "ok" : "not ok");
say(('ss' !~ $sharp_s) ? "ok" : "not ok");

my $ligature = qr/\A(?[ [\x{fb03}] ])\z/iu;
say(("\x{fb03}" =~ $ligature) ? "ok" : "not ok");
say(('ffi' !~ $ligature) ? "ok" : "not ok");

my $ordinary = qr/\A\x{00df}\z/iu;
say(('ss' =~ $ordinary) ? "ok" : "not ok");

