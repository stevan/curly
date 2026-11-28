# What the independent review found (T697 to T699), as it was run: each was WRONG before the mending, and is
# refused, a fault, or the same as perl after it.
O = "open(my $o, '<', 'in.txt') or die \"n\\n\";\n"
W = "open(my $w, '>', 'o.txt') or die \"no\\n\";\n"
CASES = [
 # T697: a print's list drops the handle perl has in its hand
 W + "open(my $v, '>', 'p.txt') or die \"n\\n\"; sub sw() { $w = $v; return 's' } print $w sw(), 't'; close($v); say 'e';",
 W + "open(my $v, '>', 'p.txt') or die \"n\\n\"; my $c = $w; sub sw() { $w = $v; return 's' } print $w sw(), 't'; close($v); close($c); say 'e';",
 W + "open(my $v, '>', 'p.txt') or die \"n\\n\"; print $w 's', ($w = $v), 't'; close($v); say 'e';",
 W + "open(my $v, '>', 'p.txt') or die \"n\\n\"; sub sw() { $w = $v; return 's' } print {$w} sw(), 't'; close($v); say 'e';",
 W + "sub sw() { $w = undef; return 's' } say $w sw(), 't'; say 'e';",
 W + "sub sw() { $w = undef; return 's' } printf $w '%s%s', sw(), 't'; say 'e';",
 W + "my %h = (fh => $w); $w = undef; sub del() { delete $h{fh}; return 's' } print { $h{fh} } del(), 't'; say 'e';",
 W + "my @h = ($w); $w = undef; print { $h[0] } 'a', pop(@h), 't'; say 'e';",
 W + "my $r = [$w]; $w = undef; sub cl() { $r = undef; return 's' } print { $r->[0] } 'a', cl(), 't'; say 'e';",
 W + "my $f = sub { $w = undef; return 's' }; print $w 'a', $f->(), 't'; say 'e';",
 W + "my $v; print { $v // $w } 'a', ($v = 1), 't'; say 'e';",
 W + "my $x = 1; sub ok() { $x++; return 's' } print $w 'a', ok(), $x, \"\\n\"; print { $w } ok(); close($w); open(my $fh, '<', 'o.txt') or die \"n\\n\"; print <$fh>;",
 W + "sub ro() { open($w, '>', 'p.txt') or die \"n\\n\"; return 's' } print $w ro(), 't'; close($w); say 'e';",
 W + "sub cl() { close($w); return 's' } print $w cl(), 't'; say 'e';",
 # T698: an open's name changes the variable perl has taken the handle from
 O + "my $fh;\nsub f() { $fh = $o; return 'nonl.txt' }\nopen($fh, '<', f()) or die \"n\\n\";\nmy $l = <$fh>; print $l; $l = <$o>; print $l;",
 O + "open(my $fh, '<', g()) or die \"n\\n\";\nsub g() { $fh = $o; return 'nonl.txt' }\nmy $l = <$fh>; print $l; $l = <$o>; print $l;",
 "my $fh;\nsub f() { $fh = 5; return 'nonl.txt' }\nopen($fh, '<', f()) or die \"n\\n\";\nsay $fh;",
 O + "my $fh = $o; $o = undef;\nsub f() { $fh = undef; return 'nonl.txt' }\nopen($fh, '<', f()) or die \"n\\n\";\nmy $l = <$fh>; print $l;",
 O + "my $fh = $o;\nsub f() { $fh = undef; return 'nonl.txt' }\nopen($fh, '<', f()) or die \"n\\n\";\nmy $l = <$fh>; print $l; $l = <$o>; print $l;",
 "my $fh;\nopen($fh, '<', ($fh = 'nonl.txt')) or die \"n\\n\";\nmy $l = <$fh>; print $l;",
 O + "my $fh;\nopen($fh, '<', ($fh = $o) ? 'nonl.txt' : 'x') or die \"n\\n\";\nmy $l = <$fh>; print $l; $l = <$o>; print $l;",
 "my $fh; my $r = \\$fh; sub f() { $r->$* = undef; return 'nonl.txt' }\nopen($fh, '<', f()) or die \"n\\n\";",
 "my $fh; sub f() { open($fh, '<', 'in.txt') or die \"n\\n\"; return 'nonl.txt' }\nopen($fh, '<', f()) or die \"n\\n\"; my $l = <$fh>; print $l;",
 # T699: the name reads the variable, which holds its handle by then
 "my $fh; sub f() { return defined($fh) ? 'in.txt' : 'nonl.txt' }\nopen($fh, '<', f()) or die \"n\\n\"; my $l = <$fh>; print $l;",
 "open(my $fh, '<', g()) or die \"n\\n\"; my $l = <$fh>; print $l;\nsub g() { return defined($fh) ? 'in.txt' : 'nonl.txt' }",
 "my $fh; sub f() { return ref($fh) eq 'GLOB' ? 'in.txt' : 'nonl.txt' }\nopen($fh, '<', f()) or die \"n\\n\"; my $l = <$fh>; print $l;",
 "my $fh;\nopen($fh, '<', defined($fh) ? 'in.txt' : 'nonl.txt') or die \"n\\n\"; my $l = <$fh>; print $l;",
 "my $fh;\nopen($fh, '<', $fh ? 'in.txt' : 'nonl.txt') or die \"n\\n\"; my $l = <$fh>; print $l;",
 "my $fh; my $f = sub { return $fh ? 'in.txt' : 'nonl.txt' };\nopen($fh, '<', $f->()) or die \"n\\n\"; my $l = <$fh>; print $l;",
 "my $fh = 5; sub f() { say 'in f'; return 'in.txt' }\nopen($fh, '<', f()) or die \"n\\n\"; say 'e';",
 "my $fh; sub f() { say defined($fh) ? 'd' : 'u'; return 'nope' }\nif (!open($fh, '<', f())) { say \"no: $!\"; }",
 "open(my $fh, '<', 'in.txt') or die \"n\\n\"; sub f() { my $l = <$fh>; chomp($l); return $l . '.txt' }\nopen($fh, '>', f()) or die \"n\\n\"; print $fh 'x'; close($fh); say 'e';",
 "open(my $fh, '<', 'in.txt') or die \"n\\n\"; sub f() { close($fh); return 'nonl.txt' }\nopen($fh, '<', f()) or die \"n\\n\"; my $l = <$fh>; print $l;",
 "my $fh = 'in.txt';\n{ open(my $fh, '<', $fh) or die \"no\\n\"; print <$fh>; }",
 "my $fh = 'in.txt';\nif (open(my $fh, '<', $fh)) { print <$fh>; }",
]
