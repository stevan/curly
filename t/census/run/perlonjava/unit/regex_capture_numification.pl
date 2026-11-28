use v5.42;

sub chr_from_shift {
    return chr(shift);
}

my $text = '#65';
say(($text =~ /^#([0-9]+)$/) ? "ok" : "not ok");
say chr($1);
say chr_from_shift($1);
say $1 << 1;

