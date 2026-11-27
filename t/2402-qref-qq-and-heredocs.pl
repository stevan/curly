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
say qq{$r->[2]{k} @{$r->[1][2]} $q->{w}[1]{k}};
say qq[$r->[1][1] $a[0][2][0]];
say qq<@{$h{k}} $h{w}{w}{k} $a[1]{w}[0]>;
say qq($r->[1]->$#* ${$s});
print <<"END";
$r->[0] $q->{k}
@{$r->[2]{w}} $r->[2]{w}->@[1, 0]
$#{$q->{w}} $s->$*
END
print <<~EOT;
    $a[1]{w}[0] $h{k}[1]
      $n->[1]{k}->$*
    EOT
print <<'RAW';
$r->[0] @{$r}
RAW
