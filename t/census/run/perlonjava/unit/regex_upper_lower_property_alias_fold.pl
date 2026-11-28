use v5.42;

for my $property (qw(Upper Uppercase XPosixUpper)) {
    say(('A' =~ qr/\p{$property}/) ? "ok" : "not ok");
    say(('a' !~ qr/\p{$property}/) ? "ok" : "not ok");
    say(('A' =~ qr/\p{$property}/i) ? "ok" : "not ok");
    say(('a' =~ qr/\p{$property}/i) ? "ok" : "not ok");
}

for my $property (qw(Lower Lowercase XPosixLower)) {
    say(('a' =~ qr/\p{$property}/) ? "ok" : "not ok");
    say(('A' !~ qr/\p{$property}/) ? "ok" : "not ok");
    say(('a' =~ qr/\p{$property}/i) ? "ok" : "not ok");
    say(('A' =~ qr/\p{$property}/i) ? "ok" : "not ok");
}

say(('1' !~ /\p{Upper}/i) ? "ok" : "not ok");
say(('1' !~ /\p{Lower}/i) ? "ok" : "not ok");

