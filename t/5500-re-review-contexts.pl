# kind: same
# The match as an expression, from the independent review of step 19: where
# a list and where one value is wanted (arguments, a hash's and an array's
# brackets, ? :, || and &&, push, map, grep, sort, x, a slice), what binds
# tighter and looser than =~, every kind of left side. Each line was first
# run under perl by hand; none is the compiler's.
use v5.42;
{ my $s = "ab"; my @l = ($s =~ /(a)/, $s =~ /(z)/, $s =~ /b/, $s =~ /q/); say scalar(@l); say "@l"; }
{ my $s = "ab"; my %h = (k => $s =~ /a/, j => 2); say join(",", map { "$_=$h{$_}" } sort keys %h); }
{ my $s = "ab"; my $r = [ $s =~ /z/ ]; say scalar($r->@*); my $q = [ $s =~ /(a)(b)/ ]; say "@{ $q }"; }
{ my $s = "ab"; say "r=", $s =~ /z/, "|"; say "r=", $s =~ /a/, "|"; say "r=", $s !~ /a/, "|"; }
{ my $s = "ab"; say join(",", $s =~ /z/, "x"); say join(",", "q", $s =~ /(.)(.)/); }
{ my $s = "ab"; my @l = ($s =~ /z/) || ("d"); say "@l"; my @m = ($s =~ /(a)/) || ("d"); say "@m"; }
{ my $s = "ab"; my @l = $s =~ /z/ ? "y" : "n"; say "@l"; }
{ my $s = "ab"; my $c = 1; my @l = $c ? $s =~ /(a)(b)/ : $s =~ /(z)/; say "@l"; }
{ my $s = "ab"; my $c = 0; my @l = $c ? $s =~ /(a)(b)/ : $s =~ /(b)/; say "@l"; }
{ my $s = "ab"; my $x = $s =~ /(a)(b)/; say $x; }
{ my $s = "ab"; my ($x) = $s =~ /a/; say $x; my ($y) = $s =~ /z/; say defined $y ? "d" : "u"; }
{ my $s = "ab"; say (($s =~ /(a)(b)/)[1]); }
{ my $s = "a1b2"; my %h = $s =~ /(\w)(\d)/g; say join(",", map { "$_=$h{$_}" } sort keys %h); }
{ my $s = "a1b2"; my @l; push @l, $s =~ /(\d)/g; push @l, $s =~ /z/; say "@l"; }
{ my @w = ("a1", "b", "c22"); my @l = map { $_ =~ /(\d+)/ } @w; say "@l"; my @g = grep { $_ =~ /\d/ } @w; say "@g"; my @n = grep { $_ !~ /\d/ } @w; say "@n"; }
{ my @w = ("a1", "b", "c22"); my @l = map { $_ =~ /\d/ } @w; say scalar(@l); say "@l"; }
{ my @w = ("a1", "b", "c22"); my @l = map { $_ =~ /\d/ ? "y" : "n" } @w; say "@l"; }
{ my @w = ("b2", "a1", "c22"); my @l = sort { ($a =~ /(\d+)/)[0] <=> ($b =~ /(\d+)/)[0] } @w; say "@l"; }
{ my $s = "a1b2"; for my $d ($s =~ /(\d)/g) { say $d; } for ($s =~ /[a-z]/g) { say $_; } }
{ my $s = "ab"; say "x" . $s =~ /a/; say $s . "x" =~ /x$/; say $s =~ /a/ . "b"; }
{ my $s = "-5"; say -$s =~ /^5$/ ? "y" : "n"; my $n = 4; say $n ** 2 =~ /16/ ? "y" : "n"; say $n + 1 =~ /1/; }
{ my $s = "ab"; say $s =~ /a/ == 1 ? "y" : "n"; say $s =~ /a/ =~ /1/ ? "y" : "n"; say $s x 2 =~ /2/; }
{ my $s = "ab"; say defined $s =~ /z/ ? "y" : "n"; say length $s =~ /a/; say uc $s =~ /a/; say lc $s =~ /A/; }
{ my $s = "ab"; say not $s =~ /a/; say !($s =~ /a/) ? "y" : "n"; }
{ my $s = "ab"; my $x = 5; say $x =~ /5/; say 5.5 =~ /\./; say true =~ /1/; say false =~ /^$/; say 1e3 =~ /^1000$/; say 0.1 + 0.2 =~ /3/; }
{ my @a = ("x1"); my %h = (k => "v9"); my $r = { a => ["zz7"] }; say $a[0] =~ /(\d)/; say $h{k} =~ /(\d)/; say $r->{a}[0] =~ /(\d)/; say "$a[0]$h{k}" =~ /(\d)v/; }
{ my $s = "aXbXc"; my @p = $s =~ /X/g; say scalar(@p); my @q = $s =~ /X/g; say scalar(@q); my @z = $s =~ /Z/g; my @r = $s =~ /X/g; say scalar(@r); }
{ my $s = "ab"; my @l = ($s =~ /(a)|(b)/g); say scalar(@l); say join(",", map { defined $_ ? $_ : "u" } @l); }
{ my $s = "ab"; my $t = $s =~ /a/ && $s =~ /(b)/; say $t; my @l = $s =~ /a/ && $s =~ /(b)/; say "@l"; my @m = $s =~ /z/ && $s =~ /(b)/; say scalar(@m); }
{ my $s = "ab"; my @l = ($s =~ /z/ or 5); say "@l"; }
{ my $s = "ab"; my @l = (!$s) =~ /^$/; say "@l"; }
{ my $s = "ab"; my $u; my @l = $s =~ /(a)|(z)/; say defined $l[1] ? "d" : "u"; say scalar(@l); }
{ my $s = "ab"; say "yes" if $s =~ /a/ and $s !~ /z/; say "no" unless $s =~ /z/ or $s =~ /q/; }
{ my $s = "ab"; try { die "oops\n" if $s =~ /a/; } catch ($e) { say $e =~ /(oo)/; } }
{ my $s = "a b c"; my @l = ($s =~ /(\w)/g) x 2; say "@l"; }
{ my $s = "ab"; my ($x, $y) = ($s =~ /(a)/, $s =~ /(b)/); say "$x$y"; }
{ my $s = "ab"; my @l = (1, $s =~ /z/, 2); say "@l"; say sprintf("%s-%s", $s =~ /(a)(b)/); }
{ my $s = "ab"; say (($s !~ /a/) =~ /^$/); }
{ my $s = "ab"; say (($s !~ /a/) !~ /^$/); }
{ my $s = "ab"; say $s =~ /a/ !~ /1/; }
{ my $s = "ab"; say ((!$s) =~ /^$/); }
{ my $s = "ab"; say defined($s) =~ /1/; say length($s) =~ /2/; }
{ my $s = "ab"; say $s eq "ab" =~ /1/; }
{ my $s = "ab"; my $t = ($s ne "x") =~ /1/; say $t; }
{ my $s = "ab"; my $c = 1; my $t = ($c ? $s : "q") =~ /a/; say $t; say (($s || "z") =~ /a/); }
{ my $s = "ab"; say (($s =~ /a/) =~ /1/); }
{ my $s = "ab"; say $s =~ /a/ . $s !~ /a/ . "|"; }
{ my $s = "ab"; say $s x 2 =~ /2/; say (($s x 2) =~ /abab/); }
{ my $s = "ab"; say 3 - 2 =~ /2/; say 3 * 2 =~ /2/; }
{ my $s = "ab"; my $r = \$s; say $r->$* =~ /a/; say ${ $r } =~ /b/; }
{ my @a = ("ab", "cd"); say $a[-1] =~ /cd/; say $#a =~ /1/; say "@a" =~ /b c/; say scalar(@a) =~ /2/; }
{ my @a = ("ab", "cd"); say sprintf("%s", "ab") =~ /ab/; say substr("abc", 1) =~ /^bc/; say uc("ab") =~ /AB/; say uc "ab" =~ /AB/; }
{ my $s = "ab"; say $s =~ /a/ ? "y" : "n" =~ /n/; }
{ my $s = "ab"; say $s =~ /a/ <=> 0; say 1 < $s =~ /a/; say "1" eq $s =~ /a/; }
{ my $s = "ab"; say "a" . "b" =~ /b/; say "a" lt "b" =~ /b/; }
{ my $s = "ab"; my @l = (1 .. $s =~ /a/); say "@l"; }
{ my $s = "ab"; my $t; $t = $s =~ /a/; $t .= $s =~ /b/; $t += $s =~ /b/; say $t; $t ||= $s =~ /q/; say $t; }
{ my $s = "ab"; my @l; @l = $s =~ /(a)(b)/; say "@l"; my ($x, @r) = $s =~ /(.)(.)/; say "$x @r"; }
{ my $s = "ab"; my %h; $h{$s =~ /a/} = 1; say join(",", sort keys %h); my @a = (5, 6); say $a[$s =~ /a/]; }
{ my $s = "ab"; my %h; @h{"p", "q"} = $s =~ /(a)(b)/; say "$h{p}$h{q}"; }
{ my %h = (s => 1, y => 2, tr => 3, m => 4, q => 5, qq => 6, qw => 7); say join(",", map { "$_=$h{$_}" } sort keys %h); }
{ my %h = (m => { s => 1 }); say $h{m}{s}; my $r = \%h; say $r->{m}->{s}; say "$h{m}{s}"; }
{ my %h; $h{m} = 1; $h{s} = 2; $h{y} = 3; say exists $h{m} ? 1 : 0; delete $h{y}; say join(",", sort keys %h); }
{ my @l = (m => 1); say "@l"; my @k = (s  => 1, y =>2); say "@k"; }
{ my $s = "a/b/c"; my @p = $s =~ /([^\/]+)/g; say "@p"; my @q = $s =~ m{([^/]+)}g; say "@q"; }
{ my $s = "ab"; my @l = (1) x ($s =~ /a/); say "@l"; }
{ my $s = "ab"; say $s =~ /a/ ? $s =~ /b/ ? "bb" : "nb" : "na"; }
{ my $s = "ab"; say "t" if ($s =~ /a/) + ($s =~ /b/) == 2; }
{ my $s = "ab"; say 4 / ($s =~ /a/) / 2; }
{ my $x = 9; my $y = $x /3; say $y; my $z = $x/3/3; say $z; }
{ my $x = 9; my @a = (1, $x / 3, 2); say "@a"; say "@a" if $x / 3 == 3; }
{ my $x = 9; my $h = { v => $x / 3 }; say $h->{v} / 3 / 1; }
{ my $s = "x=1,y=2"; my %h = $s =~ /(\w)=(\d)/g; for my $k (sort keys %h) { say "$k$h{$k}"; } }
{ my @w = ("a1", "b2"); for my $w (@w) { my ($l, $d) = $w =~ /^(\w)(\d)$/; say "$d$l"; push @w, "x" if 0; } }
{ my $s = "aXbXc"; for my $i (1 .. 3) { my @p = $s =~ /X/g; say scalar(@p); } }
{ my $s = "aXbXc"; my @e = $s =~ /Z/g; my @p = $s =~ /X(.)/g; say "@p"; my ($f) = $s =~ /X(.)/g; say $f; my @p2 = $s =~ /X(.)/g; say "@p2"; }
{ my $s = "abc"; say "[$s]" =~ /\[(\w+)\]/; say "$s$s" =~ /cab/; say '$s' =~ /^\$s$/; }
{ my $s = "abc"; my @l = "abc" =~ /(x)?abc/; say defined $l[0] ? "d" : "u"; }
