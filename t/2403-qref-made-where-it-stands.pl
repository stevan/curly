# model: t/models/qref.py
use v5.42;
my $i = 1;
my $j = -1;
my $k = "k";
my $w = "w";
my @a = ([1, 2, [3, 4]], {k => "ak", w => [5]}, "a2");
my %h = (k => [6, 7], w => {k => "hk", w => {k => "hkk"}});
my $r = [8, [9, 10, [11]], {k => "rk", w => [12, 13]}];
my $q = {k => "qk", w => [14, {k => "qwk"}], x => {k => [15, 16]}};
my $v = "sv";
my $s = \$v;
my $n = [\$v, {k => \$v}];
my $m = [3, [4]];
my $g = {k => "a"};
say "$m->[0]", ($m->[0] = 5);
say "<$m->[0]>" . ($m->[0] = 6);
say "@{$m->[1]}-" . push($m->[1]->@*, 9);
say "$g->{k}|", ($g->{k} = "b"), "|$g->{k}";
sub bump($c) {
    $c->[0] += 1;
    return $c->[0];
}
say "$m->[0]:", bump($m), ":$m->[0]";
say "$m->[1]->$#*" + bump($m);
my @seen;
for my $t ("$m->[0]", "@{$m->[1]}", "$#{$m}") {
    push $m->[1]->@*, 0;
    $m->[0] = 0;
    push @seen, $t;
}
say join("|", @seen), " ", $m->[1]->$#*;
say join(",", map { "$m->[1][$_]" } 0 .. 1);
my @l = map { $m->[0]++; "$m->[0]" } (1, 2);
say "@l";
my %by = ("$g->{k}" => 1, "$m->[1][0]x" => 2);
say join(",", map { "$_=$by{$_}" } sort keys %by);
sub tag($c) {
    return "<$c->{k}>";
}
say tag($g), tag({k => "z"});
my $z = [3];
say "$z->[0]", ($z = [5])->[0];
my @y = ("@{$z}", ($z = [7, 8])->[1]);
say "@y";
