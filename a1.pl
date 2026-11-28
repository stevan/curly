use v5.42;
my $r = open(my $fh, '<', 'in.txt'); say defined $r ? "[$r]" : 'undef'; say 0+$!; 
my $r2 = open(my $g, '<', 'nope.txt'); say defined $r2 ? "[$r2]" : 'undef'; say 0+$!; say "$!";
say defined $g ? "def" : "undef"; say ref($g); say ref(\$g);
my $l = <$fh>; print $l;
die "x";
