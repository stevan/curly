use v5.42;
use utf8;

my $upper = chr 0xC0;
my $lower = chr 0xE0;
my $upper_bytes = $upper;
my $lower_bytes = $lower;
utf8::downgrade($upper_bytes);
utf8::downgrade($lower_bytes);
my $upper_utf8 = $upper;
my $lower_utf8 = $lower;
utf8::upgrade($upper_utf8);
utf8::upgrade($lower_utf8);

say(($lower_bytes =~ qr/(?u:\xC0)/i) ? "ok" : "not ok");
say(($upper_bytes =~ qr/(?u:\xE0)/i) ? "ok" : "not ok");
say(($lower_utf8 =~ qr/(?u:\xC0)/i) ? "ok" : "not ok");
say(($upper_utf8 =~ qr/(?u:\xE0)/i) ? "ok" : "not ok");
say(($lower_bytes =~ qr/\xC0/iu) ? "ok" : "not ok");
say(($upper_bytes =~ qr/\xE0/iu) ? "ok" : "not ok");

say(($lower_bytes !~ qr/(?d:\xC0)/i) ? "ok" : "not ok");
say(($lower_bytes =~ qr/(?a:\xC0)/i) ? "ok" : "not ok");
say(($lower_bytes =~ qr/(?aa:\xC0)/i) ? "ok" : "not ok");

say((chr(0xD7) =~ qr/(?u:\xD7)/i) ? "ok" : "not ok");
say((chr(0xF7) =~ qr/(?u:\xF7)/i) ? "ok" : "not ok");
say((chr(0xD7) !~ qr/(?u:\xF7)/i) ? "ok" : "not ok");
say((chr(0xDF) =~ qr/(?u:\xDF)/i) ? "ok" : "not ok");

