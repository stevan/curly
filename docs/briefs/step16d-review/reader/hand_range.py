"""D259 by hand: a loop over one range, and what its ends name."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from split import split

TEXT = r'''
my @a = (1, 2, 3);
for my $i (0 .. $#a) { push @a, $i; }
say "@a";
----
my @a = (1, 2, 3);
for my $i (0 .. $#a) { shift @a; say scalar(@a); }
----
my @a = (1, 2, 3);
for my $i (0 .. $#a) { $#a = 0; say $i; }
say "@a";
----
my @a = (1, 2, 3);
for my $i (0 .. $#a) { undef @a; say $i; }
----
my @a = (1, 2, 3);
for my $i (0 .. scalar(@a)) { @a = (); say $i; }
----
my @a = (1, 2, 3);
for my $i (0 .. @a) { splice(@a, 0, 1); say $i; }
----
my @a = (1, 2, 3);
for my $i (0 .. scalar @a) { pop @a; say $i; }
----
my $r = [1, 2, 3];
for my $i (0 .. $#{$r}) { push $r->@*, 9; say $i; }
say "$r->@*";
----
my $r = [1, 2, 3];
for my $i (0 .. $r->$#*) { $r = [1]; say $i; }
----
my $r = [1, 2, 3];
for my $i (0 .. $#{$r}) { $r = undef; say $i; }
----
my %h = (a => 1, b => 2);
for my $i (1 .. keys %h) { $h{"k$i"} = 1; say $i; }
say scalar(%h);
----
my %h = (a => 1, b => 2);
for my $i (1 .. %h) { delete $h{a}; say $i; }
----
my %h = (a => 1, b => 2);
for my $i (1 .. scalar(%h)) { %h = (); say $i; }
----
for my $c ('a' .. 'e') { say $c; }
----
my $s = 'a'; my $e = 'e';
for my $c ($s .. $e) { $e = 'c'; say $c; }
----
my $s = 'aa'; my $e = 'ad';
for my $c ($s .. $e) { $s = 'zz'; say $c; }
----
my @a = ('x', 'z');
for my $c ($a[0] .. $a[1]) { $a[1] = 'y'; say $c; }
----
for my $c ('08' .. '11') { say $c; }
----
for my $c ('a' .. 9) { say $c; }
----
for my $c ('' .. 'c') { say "[$c]"; }
----
for my $c ('ab' .. 'c') { say "[$c]"; }
----
for my $c ('x' .. 'ab') { say "[$c]"; }
----
for my $c ('1e2' .. '102') { say "[$c]"; }
----
for my $c ('0x10' .. '3') { say "[$c]"; }
----
for my $c ('-2' .. '2') { say "[$c]"; }
----
for my $c ('+2' .. '4') { say "[$c]"; }
----
for my $c (' 2' .. '4') { say "[$c]"; }
----
for my $c ('2 ' .. '4') { say "[$c]"; }
----
for my $c ('2.5' .. '4.5') { say "[$c]"; }
----
for my $c (1.5 .. 4.5) { say "[$c]"; }
----
for my $c (-1.5 .. 1.5) { say "[$c]"; }
----
for my $c (1 .. '3abc') { say "[$c]"; }
----
my $u;
for my $c ($u .. 2) { say "[$c]"; }
----
my $u;
for my $c (0 .. $u) { say "[$c]"; }
----
for my $c (5 .. 1) { say "[$c]"; }
say "done";
----
for my $c ('a' .. 'a') { say "[$c]"; }
----
for my $c ('09' .. '08') { say "[$c]"; }
----
for my $c ('az' .. 'bc') { say "[$c]"; }
----
for my $c ('Zz' .. 'AAc') { say "[$c]"; }
----
for my $c ('a9' .. 'b2') { say "[$c]"; }
----
for my $c ('zz' .. 'a') { say "[$c]"; }
----
for my $c ('a-' .. 'a-') { say "[$c]"; }
----
for my $c ('é' .. 'é') { say "[$c]"; }
----
for my $c (true .. 3) { say "[$c]"; }
----
for my $c (false .. 2) { say "[$c]"; }
----
my $n = 0;
sub lo() { $n++; return 1; }
sub hi() { $n++; return 3; }
for my $i (lo() .. hi()) { say "$i $n"; }
----
my $n = 3;
sub hi() { return $n; }
for my $i (1 .. hi()) { $n = 10; say $i; }
----
my $n = 3;
for my $i (1 .. $n) { $n = 10; say $i; }
say $n;
----
my $n = 3;
for my $i (1 .. $n) { $n--; say $i; }
say $n;
----
my $n = 3;
for my $i ($n .. 5) { $n++; say "$i $n"; }
----
my $n = 3;
for my $i (1 .. $n++) { say "$i $n"; }
----
my $n = 3;
for my $i ($n++ .. $n++) { say "$i $n"; }
----
my $n = 3;
for my $i ($n .. $n++) { say "$i $n"; }
----
my $n = 3;
for my $i (++$n .. $n++) { say "$i $n"; }
----
my $n = 3;
for my $i ($n .. ++$n) { say "$i $n"; }
----
my $n = 3;
for my $i ($n .. ($n = 6)) { say "$i $n"; }
----
my $n = 3;
for my $i (($n = 1) .. $n + 2) { say "$i $n"; }
----
my @a = (1, 2, 3);
for my $i (0 .. $#a) { for my $j (0 .. $#a) { push @a, 0 if $i == 0 and $j == 0; say "$i $j"; } }
----
my @a = (1, 2, 3);
for my $i (0 .. $#a) { for my $x (@a) { say "$i $x"; } push @a, 9 if $i == 0; }
----
my @a = (1, 2, 3);
for my $x (@a) { for my $i (0 .. $#a) { say "$i $x"; } }
----
my @a = (1, 2, 3);
OUT: for my $i (0 .. $#a) { for my $j (0 .. $#a) { next OUT if $j == 1; push @a, 1; say "$i $j"; } }
say scalar(@a);
----
my @a = (1, 2, 3);
sub f() { for my $i (0 .. $#a) { push @a, 4; return $i if $i == 1; } return -1; }
say f();
say "@a";
push @a, 5;
say "@a";
----
my @a = (1, 2, 3);
try { for my $i (0 .. $#a) { push @a, 4; die "x\n" if $i == 1; } } catch ($e) { print $e; }
push @a, 5;
say "@a";
----
my @a = (1, 2, 3);
my @s;
for my $i (0 .. $#a) { push @s, sub { return $i * 10; }; }
push @a, 4;
say join(",", map { $_->() } @s);
say "@a";
----
my @a = (1, 2, 3);
my @s;
for my $i (0 .. $#a) { push @s, sub { push @a, $i; return scalar(@a); }; }
say join(",", map { $_->() } @s);
say "@a";
----
my $n = 3;
my @s;
for my $i (1 .. $n) { push @s, sub { $n++; return "$i/$n"; }; }
$n = 9;
say join(",", map { $_->() } @s);
----
my $n = 3;
my @s;
for my $i (1 .. $n) { push @s, sub { return $i + $n; }; $n = 100; }
say join(",", map { $_->() } @s);
----
my @s;
for my $i ('a' .. 'c') { push @s, sub { return $i; }; }
say join(",", map { $_->() } @s);
----
my @s;
for my $i (1 .. 3) { my $r = \$i; push @s, $r; }
say join(",", map { $_->$* } @s);
----
my @a = (1, 2, 3);
say join(",", map { push @a, 1; $_ } 0 .. $#a);
----
my @a = (1, 2, 3);
say join(",", grep { $#a = 0; true } 0 .. $#a);
----
my @a = (3, 1, 2);
say join(",", sort { push @a, 1; $a <=> $b } 0 .. $#a);
----
my @a = (1, 2, 3);
push @a, $_ for 0 .. $#a;
say "@a";
----
my @a = (1, 2, 3);
$#a = 0 for 0 .. $#a;
say "@a";
----
my @a = (1, 2, 3);
for (0 .. $#a) { shift @a; say $_; }
----
my @a = (1, 2, 3);
for my $i (reverse 0 .. $#a) { push @a, 1; say $i; }
----
my @a = (1, 2, 3);
for my $i ((0 .. $#a)) { push @a, 1; say $i; }
----
my @a = (1, 2, 3);
for my $i (0 .. $#a,) { push @a, 1; say $i; }
----
my @a = (1, 2, 3);
for my $i (+(0 .. $#a)) { push @a, 1; say $i; }
----
my @a = (1, 2, 3);
for my $i (0 .. $#a, 7) { push @a, 1; say $i; last; }
----
my @a = (1, 2, 3);
for my $i (@a[0 .. $#a]) { push @a, 1; say $i; last; }
----
my @a = (1, 2, 3);
for my $i ((0 .. $#a)[1, 2]) { push @a, 1; say $i; }
----
my @a = (1, 2, 3);
for my $i (0 .. $a[0]) { $a[0] = 5; say $i; }
----
my @a = (1, 2, 3);
for my $i ($a[0] .. $a[2]) { @a = (9); say $i; }
----
my @a = (1, 2, 3);
for my $i ($a[0] .. $a[7]) { say $i; }
say scalar(@a);
----
my @a = (1, 2, 3);
for my $i ($a[7] // 0 .. 2) { say $i; }
say scalar(@a);
----
my %h = (a => 1);
for my $i ($h{a} .. $h{b} // 2) { say $i; }
say join(",", sort keys %h);
----
my %h = (a => 1);
for my $i (0 .. $h{zz}{n} // 1) { say $i; }
say join(",", sort keys %h);
----
my $r;
for my $i (0 .. $#{$r}) { say $i; }
say defined $r ? "made" : "undef";
----
my $r;
for my $i (0 .. $r->$#*) { say $i; }
say defined $r ? "made" : "undef";
----
my $r;
for my $i (0 .. scalar($r->@*)) { say $i; }
say defined $r ? "made" : "undef";
----
my $r = [[1, 2], [3]];
for my $i (0 .. $#{$r->[0]}) { $r->[0] = [9, 9, 9, 9]; say $i; }
----
my $r = [[1, 2], [3]];
for my $i (0 .. $r->[2]->$#*) { say $i; }
say scalar($r->@*);
----
my @a = (1, 2, 3);
for my $i (0 .. $#a) { $i = 5; }
----
my @a = (1, 2, 3);
for my $i (0 .. $#a) { $i++; say $i; }
----
my @a = (1, 2, 3);
for my $i (0 .. $#a) { my $r = \@a; push $r->@*, 1; say $i; }
----
my @a = (1, 2, 3);
my $r = \@a;
for my $i (0 .. $r->$#*) { push @a, 1; say $i; }
----
my @a = (1, 2, 3);
sub g() { push @a, 1; return; }
for my $i (0 .. $#a) { g(); say $i; }
say "@a";
----
for my $i (9223372036854775805 .. 9223372036854775807) { say $i; }
----
for my $i (-9223372036854775808 .. -9223372036854775806) { say $i; }
----
for my $i (9223372036854775807 .. 9223372036854775807) { say $i; }
----
for my $i (1 .. 1e3) { say $i if $i == 1000; }
----
for my $i (1e15 .. 1e15 + 1) { say $i; }
----
for my $i (9007199254740992 .. 9007199254740993) { say $i; }
----
for my $i (9.0e15 .. 9.0e15 + 1) { say $i; }
----
for my $i ("9007199254740993" .. "9007199254740994") { say $i; }
----
for my $i (1 .. 3) { for my $i (1 .. $i) { print $i; } print "\n"; }
----
my $n = 2;
for my $i (1 .. $n) { for my $j (1 .. $n) { $n = 4 if $i == 1 and $j == 1; print "$i$j "; } }
print "\n";
----
my @a = (1, 2, 3);
for my $i (0 .. $#a) { @a = map { $_ * 2 } @a; }
say "@a";
----
my @a = (3, 1, 2);
for my $i (0 .. $#a) { @a = sort { $a <=> $b } @a; push @a, $i; }
say "@a";
----
my @a = (1, 2, 3);
for my $i (0 .. $#a) { say $i; last if $i == 1; }
$#a = 5;
say scalar(@a);
----
my @a = (1, 2, 3);
my $k = 0;
do { for my $i (0 .. $#a) { push @a, $i; } $k++; } while ($k < 2);
say scalar(@a);
----
my @a = (1, 2, 3);
for my $i (0 .. $#a) { for my $x (0 .. $#a) { } push @a, 1; }
say scalar(@a);
----
my @a = (1, 2);
for my $i (0 .. $#a) { for my $x (@a, 0 .. $#a) { } push @a, 1; }
say scalar(@a);
----
my @a = (1, 2);
for my $x (@a) { for my $i (0 .. $#a) { push @a, 1; last; } }
say scalar(@a);
----
my @a = (1, 2, 3);
my @s;
for my $x (@a) { for my $i (0 .. 1) { push @s, sub { return $i + $x; }; } }
say join(",", map { $_->() } @s);
push @a, 4;
----
my @a = (1, 2, 3);
my @s;
for my $i (0 .. 1) { for my $x (@a) { push @s, sub { return $i + $x; }; } }
say join(",", map { $_->() } @s);
push @a, 4;
----
my @a = (1, 2, 3);
my $x = 0;
for my $i (0 .. ($x = $#a)) { $x = 9; say $i; }
say $x;
----
my @a = (1, 2, 3);
for my $i (0 .. (push @a, 5)) { say $i; }
----
my @a = (1, 2, 3);
for my $i (0 .. shift @a) { say $i; }
say "@a";
----
my @a = (1, 2, 3);
for my $i (shift(@a) .. shift(@a)) { say $i; }
say "@a";
----
my @a = (1, 2, 3);
for my $i (shift(@a) .. $#a) { say $i; }
----
my @a = (1, 2, 3);
for my $i ($#a .. pop(@a)) { say $i; }
----
my @a = (4, 2, 3);
for my $i ($a[0] .. ($a[0] = 6)) { say $i; }
----
my @a = (1, 2, 3);
for my $i (0 .. $#a) { $_ = 1 for @a; }
say "@a";
----
my $i = 5;
for $i (1 .. 3) { }
say $i;
----
my @a = (1,2,3);
for my $i (0 .. $#a) { my $j = $i; for my $k ($j .. $#a) { $j++; pop @a if $k > 5; } }
say "@a";
'''


def cases():
    return split('r', TEXT)
