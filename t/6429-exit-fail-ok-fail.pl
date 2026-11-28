# t/models/file.py 6429
# kind: warns
# file: in.txt=a\nb\nc\n
use v5.42;
if (open(my $h1, '<', "nope.txt")) { say "opened nope.txt" } else { say "no nope.txt: $!" }
if (open(my $h2, '<', "in.txt")) { say "opened in.txt" } else { say "no in.txt: $!" }
if (open(my $h3, '<', "nope.txt")) { say "opened nope.txt" } else { say "no nope.txt: $!" }
die "the last open failed\n";
