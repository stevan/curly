use v5.42;
{ open(my $fh, '<', 'in.txt') or die "cannot: $!";
my $l = <$fh>; }
warn "w";
open(my $fh, '<', 'in.txt') or die "cannot: $!";
my $l = <$fh>; $l = <$fh>;
warn "w";
my $g = $fh;
my $e = eof(STDIN);
warn "w2";
$l = <$g>;
warn "w3";
say 0+$!;
die "x";
