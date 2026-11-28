# t/models/file.py 6408
use v5.42;
sub save($name, $text) { open(my $out, '>', $name) or die "no $name\n"; print $out $text; }
sub slurp($name) { open(my $in, '<', $name) or die "no $name\n"; my @lines = <$in>; return join("", @lines); }
save("kept.txt", "kept\n");
print slurp("kept.txt");
save("kept.txt", "again\n");
print slurp("kept.txt"), slurp("kept.txt");
sub add($name, $text) { open(my $out, '>>', $name) or die "no $name\n"; print $out $text; return; }
for my $i (1 .. 5) { add("log.txt", "line $i\n"); }
print slurp("log.txt");
sub first_line($name) { open(my $in, '<', $name) or die "no $name\n"; my $l = <$in>; return $l; }
print first_line("log.txt");
add("log.txt", "last\n");
my @all = (slurp("log.txt"));
say length($all[0]);
