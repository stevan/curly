use v5.42;

my $replacement = "Terca";
substr($replacement, 3, 1) = chr(0xe7);
utf8::upgrade($replacement);

say((utf8::is_utf8($replacement)) ? "ok" : "not ok");

my $fmt = "%A";
$fmt =~ s/%A/$replacement/e;
say $fmt;
say((utf8::is_utf8($fmt)) ? "ok" : "not ok");

my $source = "%A";
my $result = $source =~ s/%A/$replacement/er;
say $result;
say((utf8::is_utf8($result)) ? "ok" : "not ok");
say((!utf8::is_utf8($source)) ? "ok" : "not ok");

