# t/models/file.py 6405
# file: here.txt=h\n
use v5.42;
if (open(my $h1, '<', "nope.txt")) { say "opened nope.txt" } else { say "no nope.txt: $!" }
if (open(my $h2, '<', "here.txt")) { say "opened here.txt" } else { say "no here.txt: $!" }
my $h3;
say defined(open($h3, '<', "nope.txt")) ? "defined" : "undef";
say "[$!]";
say ref($h3), " ", defined($h3) ? "defined" : "undef", " ", $h3 ? "true" : "false";
say "e1: $!.";
say "e2: " . $! . "!";
say "e3: $!::x $!->";
my $why = $!; say length($why), " ", $why eq "No such file or directory" ? "the words" : "others", " ", $! ? "true" : "false";
my @whys = ($!, "$!");
say scalar(@whys), " ", $whys[0] eq $whys[1] ? "same" : "differ";
unless (open(my $d, '<', "no/such/dir/x.txt")) { say "unless: $!" }
my $h5; my $r = open($h5, '<', 'nope.txt'); say defined $r ? "defined" : "undef", " ", ref($h5);
open($h5, '<', 'here.txt') or die "no\n"; my $l = <$h5>; print $l; close($h5);
open(my $w, '>', "no/such/dir/x.txt");
say "[$!]";
if (open(my $ap, '>>', "no/such/dir/x.txt")) { say "opened x.txt" } else { say "no x.txt: $!" }
say "[$!]";
