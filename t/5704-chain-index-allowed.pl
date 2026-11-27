# By hand, with perl's answers (make oracle): the indexes and keys of a
# chain that D246 lets be, since they let go of no container it holds.
use v5.42;
my $r = {};
my $n = 0;
sub nid() { $n++; return "id$n" }
$r->{nid()} = 1;
$r->{nid()} = 2;
say join(",", map { "$_=$r->{$_}" } sort keys $r->%*);
my $l = [10, 20, 30];
my $i = 0;
say $l->[$i++], " ", $l->[$i++], " ", $l->[$i];
my $count = {};
sub tick() { $count->{n}++; return 1 }
$l->[tick()] = 99;
say join(",", $l->@*), " ", $count->{n};
my @a = (1, 2);
sub grow() { push(@a, 3); return 2 }
say $a[grow()];
my %h = (k => [5, 6]);
my $j = 0;
$h{k}[$j++] = 7;
say join(",", $h{k}->@*), " ", $j;
