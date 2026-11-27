use v5.42;

my $same_line = 'abxx';
say(($same_line =~ /.*?x/) ? "ok" : "not ok");
say $&;
say $-[0];

my $after_newline = "before\nx";
say(($after_newline =~ /.*?x/) ? "ok" : "not ok");
say $&;
say $-[0];

my $alternative = 'ba';
say(($alternative =~ /a|.*?x/) ? "ok" : "not ok");
say $&;
say $-[0];

