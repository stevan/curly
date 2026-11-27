use v5.42;

my $v = version->parse('5.14.0');

say ref($v);
say "$v";
say((version->parse($^V) >= version->parse('5.14.0')) ? "ok" : "not ok");

