# Step 16d's statements about perl, and those of what the census's reading
# asked for (PLAN.md, step 16: "What the census's reading asked for" and
# "16d"), as claims.py's rows: a file of its own, so that the branch merges
# beside the steps built at the same time. claims.py reads it.
#
#     python3 docs/briefs/claims.py T660 16d-scalar-bare
def c(id, where, code, **said):
    return (id, where, code, said)

STEP16D = [
    # ---- scalar without brackets (D250)
    c('16d-scalar-bare', 'PLAN 16 census', r"""my @a = (1, 2, 3); my %h = (a => 1, b => 2); my $r = [4, 5]; say scalar @a; say scalar %h; say scalar keys %h; say scalar $r->@*; say scalar @{$r}; say scalar @a == 3 ? "y" : "n"; say join ",", (scalar @a, 9);""", out='3\n2\n2\n2\n2\ny\n3,9\n'),
    c('16d-scalar-reads-on', 'PLAN 16 census', r"""my @a = (1, 2, 3); say scalar @a + 1; say scalar @a . "x"; say scalar @a x 2; say scalar @a ** 2;""", out='4\n3x\n33\n9\n'),
    c('16d-scalar-slice', 'PLAN 16 census', r"""my @a = (1, 2, 3); say scalar @a[1];""", out='2\n', err='Scalar value @a\\[1\\] better written as \\$a\\[1\\]'),
    c('16d-scalar-any', 'PLAN 16 census', r"""my $x = 1; say scalar $x;""", out='1\n'),
    # ---- $#a = N (D251)
    c('16d-lastindex', 'PLAN 16 census', r"""my @a = (1, 2, 3); $#a = 1; say "@a"; $#a = 3; say scalar(@a); say exists $a[3] ? "e" : "n"; say defined $a[3] ? "d" : "u";""", out='1 2\n4\nn\nu\n'),
    c('16d-lastindex-cut', 'PLAN 16 census', r"""my @a = (1, 2, 3); $#a = 1.7; say scalar @a; $#a = "2"; say scalar @a; $#a = -1; say scalar @a; @a = (1, 2, 3); $#a = -0.5; say scalar @a; $#a = -1.5; say scalar @a;""", out='2\n3\n0\n1\n0\n'),
    c('T660', 'TRAPS; PLAN 16 census', r"""my @a = (1, 2, 3); $#a = -2; say scalar @a; @a = (1, 2, 3); $#a = -5; say scalar @a;""", out='0\n0\n'),
    c('16d-lastindex-undef', 'PLAN 16 census', r"""my @a = (1, 2, 3); $#a = undef; say scalar @a;""", out='1\n', err='uninitialized value in scalar assignment'),
    c('16d-lastindex-string', 'PLAN 16 census', r"""my @a = (1, 2, 3); $#a = "abc"; say scalar @a;""", out='1\n', err='isn.t numeric'),
    c('16d-lastindex-value', 'PLAN 16 census', r"""my @a = (1, 2, 3); my $x = ($#a = 0); say $x; say scalar @a; $#a += 2; say scalar @a; $#a++; say scalar @a;""", out='0\n1\n3\n4\n'),
    c('16d-lastindex-foreach', 'PLAN 16 census', r"""my @a = (1, 2, 3); for my $x (@a) { $#a = 0; say $x }""", out='1\n'),
    c('16d-lastindex-ref', 'PLAN 16 census', r"""my @a = (1, 2, 3); my $r = \@a; $#{$r} = 0; say scalar @a; $r->$#* = 4; say scalar @a; my $u; $#{$u} = 2; say scalar $u->@*; say ref $u;""", out='1\n5\n3\nARRAY\n'),
    c('16d-lastindex-huge', 'PLAN 16 census', r"""my @a = (1, 2, 3); $#a = 2**40; say "x";""", exit='nonzero', err='Out of memory'),
    # ---- undef X; (D252)
    c('16d-undef', 'PLAN 16 census', r"""my @a = (1); undef $a[3]; say scalar @a; my %h; undef $h{k}; say exists $h{k} ? "e" : "n"; say scalar keys %h; my $x = 3; my $y = undef $x; say defined $y ? "d" : "u"; say defined $x ? "d" : "u";""", out='4\ne\n1\nu\nu\n'),
    c('16d-undef-whole', 'PLAN 16 census', r"""my @a = (1, 2); undef @a; say scalar @a; my %h = (a => 1); undef %h; say scalar %h; my $x = 1; undef($x); say defined $x ? "d" : "u"; $x = 1; undef $x if 1; say defined $x ? "d" : "u";""", out='0\n0\nu\nu\n'),
    c('16d-undef-ref', 'PLAN 16 census', r"""my $r = [1, 2]; undef $r->@*; say scalar $r->@*; undef $r->[5]; say scalar $r->@*; my $u; undef $u->[1]; say ref $u; my $v; undef @{$v}; say ref $v; my $w; undef %{$w}; say ref $w; my $x = 1; my $s = \$x; undef $s->$*; say defined $x ? "d" : "u";""", out='0\n6\nARRAY\nARRAY\nHASH\nu\n'),
    c('T661', 'TRAPS; PLAN 16 census', r"""my @a = (1, 2, 3); undef @a[0, 1]; say "@a";""", out='1  3\n', err='uninitialized value \\$a\\[1\\]'),
    c('16d-undef-foreach', 'PLAN 16 census', r"""my @a = (1, 2, 3); for my $x (@a) { undef $x } say defined $a[0] ? "d" : "u";""", out='u\n'),
    c('16d-undef-comma', 'PLAN 16 census', r"""my $x = 1; undef $x, print "a\n";""", out='a\n'),
    # ---- do { } while (D253)
    c('16d-do-while', 'PLAN 16 census', r"""my $i = 5; do { print $i; $i++ } while ($i < 3); print "\n"; $i = 0; do { $i++ } until $i >= 3; say $i; my @s; $i = 0; do { my $k = $i; push @s, sub { $k }; $i++ } while ($i < 3); say join ",", map { $_->() } @s;""", out='5\n3\n0,1,2\n'),
    c('T64-last', 'TRAPS; PLAN 16 census', r"""my $i = 0; for my $k (1 .. 3) { do { $i++; last if $i == 2 } while ($i < 5); print "k$k\n" } say "end $i";""", out='end 2\n'),
    c('16d-do-while-label', 'PLAN 16 census', r"""my $i = 0; OUT: for my $k (1 .. 3) { do { $i++; next OUT if $i == 2 } while ($i < 5); print "k$k\n" } say "end $i";""", out='k2\nk3\nend 6\n'),
    c('16d-do-while-last-alone', 'PLAN 16 census', r"""my $i = 0; do { $i++; last if $i == 2 } while ($i < 5); say "end $i";""", exit=255, err='Can.t "last" outside a loop block'),
    c('T662', 'TRAPS; PLAN 16 census', r"""my $i = 0; L: do { $i++; last L if $i == 2 } while ($i < 5); say "end $i";""", exit=255, err='Label not found for "last L"'),
    c('16d-do-while-my', 'PLAN 16 census', r"""my $i = 0; do { my $j = $i; $i++ } while ($j < 3);""", compiles=False, err='Global symbol "\\$j"'),
    c('16d-do-while-return', 'PLAN 16 census', r"""sub f { do { return 5 } while (1); } say f();""", out='5\n'),
    c('16d-do-other-modifiers', 'PLAN 16 census', r"""my $i = 0; do { $i++ } for 1 .. 3; do { $i++ } unless 0; do { $i++ }; say $i;""", out='5\n'),
    c('16d-do-while-two-modifiers', 'PLAN 16 census', r"""my $i = 0; do { $i++ } while $i < 3 if 1;""", compiles=False, err='syntax error'),
    c('T663-until', 'TRAPS; PLAN 16 census', 'my $i = 0;\ndo { $i++; print "b$i\\n"; } until (die "x\\n");', out='b1\n', err='x', exit=255),
    c('T663-line', 'TRAPS; PLAN 16 census', 'my $i = 0;\ndo {\n  $i++;\n} while ($i < 2 || die "x");', exit=255, err='x at - line 3\\.|x at .* line 3\\.'),
    # ---- 16d: substr of four (D254)
    c('16d-substr4', 'PLAN 16d', r"""my $s = "abcdef"; my $r = substr($s, 1, 2, "XYZ"); say "$r $s"; $r = substr($s, -2, 1, ""); say "$r $s"; substr($s, 0, 0, "<"); say $s; my $t = "abc"; $r = substr($t, 3, 1, "x"); say "[$r] $t"; $r = substr($t, 1, -1, "Q"); say "[$r] $t"; my $n = 12345; substr($n, 1, 1, 9); say $n + 1;""", out='bc aXYZdef\ne aXYZdf\n<aXYZdf\n[] abcx\n[bc] aQx\n19346\n'),
    c('16d-substr4-outside', 'PLAN 16d', r"""my $s = "abc"; my $r = substr($s, 5, 1, "x"); say "[$r] $s";""", exit=255, err='substr outside of string'),
    c('16d-substr4-before', 'PLAN 16d', r"""my $s = "abc"; my $r = substr($s, -5, 1, "x"); say "[$r] $s";""", exit=255, err='substr outside of string'),
    c('16d-substr4-undef', 'PLAN 16d', r"""my $s; my $r = substr($s, 0, 0, "x"); say "[$r] $s";""", out='[] x\n', err='uninitialized value \\$s in substr'),
    c('16d-substr-lvalue', 'PLAN 16d', r"""my $s = "abc"; substr($s, 1, 1) = "ZZ"; say $s; my $r = \substr($s, 0, 1); $$r = "Q"; say $s;""", out='aZZc\nQZZc\n'),
    c('16d-substr4-loop', 'PLAN 16d', r"""my @a = ("abc", "def"); for my $x (@a) { substr($x, 0, 1, "Z") } say "@a";""", out='Zbc Zef\n'),
    # ---- 16d: scalar reverse (D258)
    c('16d-scalar-reverse', 'PLAN 16d', r"""my $s = "abc"; say scalar reverse $s; say scalar reverse("ab", "cd"); say scalar reverse "dlrow ,", "olleH"; my @a = ("x", "yz"); say scalar reverse @a; say scalar reverse 12, 3.5;""", out='cba\ndcba\nHello, world\nzyx\n5.321\n'),
    c('T23', 'TRAPS; PLAN 16d', r"""my $x = reverse "hello"; say $x; say reverse "abc"; say "" . reverse "ab"; say lc reverse "AB"; sub f { reverse "abc" } my $s = f(); my @l = f(); say "$s @l";""", out='olleh\nabc\nba\nba\ncba abc\n'),
    c('16d-reverse-nothing', 'PLAN 16d', r"""my $x = reverse(); say "[$x]";""", out='[]\n', err='uninitialized value in reverse'),
    # ---- 16d: the case escapes (D256)
    c('16d-case-escapes', 'PLAN 16d', r"""my $x = "fOO"; say "\U$x\E-\L$x\E-\u$x-\l$x-\u\L$x\E-\L\u$x\E-\Qa.b\E"; my $y = "fOO bar"; say "a\Uxy$y z\Ew"; my $e = ""; say "\u${e}d"; say "\Ua${e}b\E"; say "\uab\Ucd"; say "\u\lABC"; say "\l\uabc"; say "\U\uabc\E"; say "x\L\uABC\E-\uyz"; say "\Ua\Qb.c\Ed.e";""", out='FOO-foo-FOO-fOO-Foo-Foo-a\\.b\naXYFOO BAR Zw\nD\nAB\nAbCD\nABC\nabc\nABC\nxAbc-Yz\nAB\\.CD.E\n'),
    c('16d-case-replaced', 'PLAN 16d', r"""say "\Uab\Lcd\Eef";""", out='ABcdef\n'),
    c('16d-case-useless-E', 'PLAN 16d', r"""say "x\E";""", out='x\n', err='Useless use of \\\\E'),
    c('16d-case-undef', 'PLAN 16d', r"""my $x; say "\U$x";""", out='\n', err='uninitialized value \\$x in uc'),
    c('16d-case-fold', 'PLAN 16d', r"""say "\F" . "SS", "\FAB";""", out='SSab\n'),
    c('16d-quotemeta', 'PLAN 16d', r"""say quotemeta(" -_a1."); say quotemeta(chr(0xE9)) eq chr(0xE9) ? "same" : "quoted"; say quotemeta(chr(0xAD)) eq "\\" . chr(0xAD) ? "quoted" : "same";""", out='\\ \\-_a1\\.\nsame\nquoted\n'),
    # ---- 16d: __FILE__ and __LINE__ (D255)
    c('T665', 'TRAPS; PLAN 16d', 'say __LINE__;\nsay "a",\n  __LINE__,\n  "b";\nsay __LINE__\n  + 1;\nsay __LINE__ . __LINE__;\nmy %h = (__LINE__ => 1); say keys %h;', out='2\na4b\n7\n88\n__LINE__\n'),
    c('16d-file', 'PLAN 16d', 'say __FILE__; my $s = "__FILE__"; say $s;', out='claim.pl\n__FILE__\n'),
    c('16d-line-call', 'PLAN 16d', 'say __LINE__();', out='2\n'),
    # ---- 16d: POD, __END__ and __DATA__ (D255)
    c('16d-pod', 'PLAN 16d', 'say 1;\n=head1 X\n\n=cut\nsay 2;\n=pod\n=cutting\nsay 3;\n=cut back\nsay 4;', out='1\n2\n4\n'),
    c('T666', 'TRAPS; PLAN 16d', 'say 1;\n=cut\nsay 2;\n=cut\nsay 3;', out='1\n3\n'),
    c('16d-pod-to-end', 'PLAN 16d', 'say 1;\n=pod\nsay 2;', out='1\n'),
    c('16d-pod-mid-statement', 'PLAN 16d', 'say(1,\n=pod\nx\n=cut\n2);', compiles=False, err='syntax error'),
    c('16d-pod-in-block', 'PLAN 16d', 'if (1) {\n=pod\nx\n=cut\nsay 2;\n}', out='2\n'),
    c('16d-pod-indented', 'PLAN 16d', 'say 1;\n =pod\nsay 2;', compiles=False, err='syntax error'),
    c('T667', 'TRAPS; PLAN 16d', '=pod\n\n# line 200 "x"\n\n=cut\ndie "here";', exit=255, err='here at x line 202\\.'),
    c('16d-end', 'PLAN 16d', 'say 1;\n__END__\nsay 2;', out='1\n'),
    c('16d-end-same-line', 'PLAN 16d', 'say 1; __DATA__ say 2;', out='1\n'),
    c('16d-end-value', 'PLAN 16d', 'say 1 . __END__;', compiles=False, err='syntax error'),
    # ---- 16d: uc, lc, ucfirst, lcfirst past ASCII (D257)
    c('16d-case-tables', 'PLAN 16d', 'use open ":std", ":encoding(UTF-8)"; say uc(chr(0xE9)), lc(chr(0xC9)), uc(chr(0xDF)), ucfirst(chr(0xDF)), lc(chr(0x130)), length lc(chr(0x130)), ucfirst(chr(0x1C6)), uc(chr(0x1C6)), uc(chr(0x149)), uc(chr(0xFB03));', out='ÉéSSSsi̇' + '2ǅǄʼNFFI\n'),
    c('16d-no-final-sigma', 'PLAN 16d', 'use open ":std", ":encoding(UTF-8)"; say lc(chr(0x391) . chr(0x3A3));', out='ασ\n'),
    c('T664', 'TRAPS; PLAN 16d', 'say join ",", map { sprintf "%X", ord } split //, uc "\\x{345}\\x{345}"; say join ",", map { sprintf "%X", ord } split //, uc "\\x{345}x\\x{345}";', out='399\n399,58,399\n'),
    # ---- the freeze's exception (D259)
    c('T668', 'TRAPS; PLAN 16 census', r"""my @a = (1, 2, 3); for my $i (0 .. $#a) { $a[$i] *= 2; push @a, 9 if $i == 0; } say "@a"; @a = (1, 2, 3); my $n = 0; for my $i (0 .. $#a) { shift @a; $n++ } say "$n @a"; @a = (1, 2, 3); $n = 0; for my $i (0 .. $#a) { @a = (); $n++ } say $n; @a = (1, 2, 3); $n = 0; for my $i (1 .. @a) { push @a, 1; $n++ } say $n; my %h = (a => 1, b => 2); $n = 0; for my $i (1 .. keys %h) { $h{$i} = 1; $n++ } say $n;""", out='2 4 6 9\n3 \n3\n3\n2\n'),
    c('T668-ref', 'TRAPS; PLAN 16 census', r"""my $r = [1, 2, 3]; my $n = 0; for my $i (0 .. $#{$r}) { push $r->@*, 1; $n++ } say $n; my @a = (5, 6); $n = 0; for my $i ($a[0] .. $a[1]) { $a[1] = 100; $n++ } say $n; @a = (1, 2, 3); for my $i (0 .. $#a) { $#a = 0 if $i == 0; say $a[$i] // "u" }""", out='3\n2\n1\nu\nu\n'),
    c('T669', 'TRAPS; PLAN 16 census', r"""my $n = 3; my @s; for my $i (1 .. $n) { push @s, sub { $i } } $n = 9; say join ",", map { $_->() } @s;""", out='1,2,3\n'),
    c('16d-range-variable', 'PLAN 16 census', r"""my $n = 2; for my $i (1 .. $n) { $i++; say $i }""", out='2\n3\n'),
    c('16d-range-sub', 'PLAN 16 census', r"""my $c = 0; sub f() { $c++; return 3 } my $n = 0; for my $i (0 .. f()) { $n++ } say "$n $c";""", out='4 1\n'),
    c('16d-each-array-alias', 'PLAN 16 census', r"""my @a = (1, 2, 3); my $n = 0; for my $x (@a) { push @a, 9 if $n++ < 2; } say $n;""", out='5\n'),
    # ---- items 5 to 7 of the census's part (D260 to D262)
    c('16d-or-die', 'PLAN 16 census', 'my %ops = (a => 1); my $f = $ops{a} or die "no\\n"; say $f; my $g = $ops{b} or die "unknown b\\n";', out='1\n', exit=255, err='^unknown b\\n$'),
    c('16d-or-return', 'PLAN 16 census', 'sub h ($x) { my $n = $x or return "none"; return "got $n" } say h(0), " ", h(5);', out='none got 5\n'),
    c('16d-or-next', 'PLAN 16 census', 'for my $i (1 .. 3) { my $v = $i - 2 or next; say $i } for my $i (1 .. 3) { $i == 2 and last; say $i }', out='1\n3\n1\n'),
    c('16d-or-die-constant', 'PLAN 16 census', 'my $x = 0 or die "no\\n";', exit=255, err='Found = in conditional'),
    c('16d-and-say', 'PLAN 16 census', 'my %h; $h{a} = 3 and say "yes";', out='yes\n', err='Found = in conditional'),
    c('T670', 'TRAPS; PLAN 16 census', 'my ($p) = (0) or die "e\\n"; say "here";', out='here\n'),
    c('16d-or-die-modifier', 'PLAN 16 census', 'my %h = (a => 1); my $f = $h{a} or die "no\\n" if 1; say "ok";', out='ok\n'),
    c('16d-or-die-own-variable', 'PLAN 16 census', 'my $y = 2; my $f = $y or die "f is $f\\n";', compiles=False, err='Global symbol "\\$f"'),
    c('16d-sort-brackets', 'PLAN 16 census', 'my @x = (3, 1, 2); say join "", sort(@x); say join "", sort((@x)); say join "", sort({ $b <=> $a } @x); my %h = (b => 1, a => 2); say join ",", sort(keys %h); say join ",", sort(reverse @x); my @s = (sort(@x), 9); say "@s";', out='123\n123\n321\na,b\n1,2,3\n1 2 3 9\n'),
    c('E24-sort-blank', 'PLAN 16 census; T190', 'my @a = (2, 1); my @s = (sort (@a), 9); say "@s";', out='1 2 9\n', err='sort \\(\\.\\.\\.\\) interpreted as function'),
    c('T671', 'TRAPS; PLAN 16 census', 'sub l($w) { return split //, $w } say join "", sort(l("cab")); say join "", sort(l ("cab"));', out='abc\ncab\n', err='Unquoted string "l" may clash'),
    c('16d-sort-brackets-scalar', 'PLAN 16 census', 'my @x = (3, 1, 2); my $by = sub { $a <=> $b }; say join ",", sort($by @x);', out='1,2,3\n'),
    c('16d-sort-brackets-subscript', 'PLAN 16 census', 'my @x = (3, 1, 2); my @s = (sort(@x)[0]);', compiles=False, err='syntax error'),
    c('16d-die-sprintf', 'PLAN 16 census', 'my $n = 1;\ndie sprintf("has %d\\n", $n)\n    if $n;', exit=255, err='^has 1\\n$'),
    c('16d-die-concat', 'PLAN 16 census', 'my @l = (1, 2);\ndie "cycle among: " . join(" ", @l) . "\\n"\n    if @l;', exit=255, err='^cycle among: 1 2\\n$'),
    c('16d-die-join-last', 'PLAN 16 census', 'my @l = ("a", "b\\n");\ndie join(" ", @l)\n    if @l;', exit=255, err='^a b\\n$'),
    c('16d-die-sprintf-inner-newline', 'PLAN 16 census', 'my $n = 1;\ndie sprintf("has\\n%d", $n)\n    if $n;', exit=255, err='^has\\n1 at .* line 3\\.\\n$'),
    # ---- what the independent review found (T673 to T699)
    c('T673', 'TRAPS; PLAN 16 review', 'say 1;\n=_x\nsay 2;\n=cut\nsay 3;', compiles=False, err='syntax error at .* line 3, near "="'),
    c('T674-do', 'TRAPS; PLAN 16 review', 'my $i = 0;\ndo { $i++ }\n=pod\n=cut\nuntil ($i);\nsay $i;', compiles=False, err="Can't modify constant item in scalar assignment"),
    c('T674-map', 'TRAPS; PLAN 16 review', 'my @l = map {\n$_ * 2\n}\n=pod\n=cut\n1, 2;\nsay "@l";', compiles=False, err='syntax error at .* line 5, near "="'),
    c('T674-sort', 'TRAPS; PLAN 16 review', 'my @l = sort {\n$a <=> $b\n}\n=pod\n=cut\n2, 1;\nsay "@l";', compiles=False, err='syntax error at .* line 5, near "="'),
    c('T674-for', 'TRAPS; PLAN 16 review', 'my $i = 0;\nfor ($i = 0; $i < 2;\n=pod\n=cut\n$i++) { }\nsay $i;', compiles=False, err='syntax error at .* line 4, near "="'),
    c('T674-in', 'PLAN 16 review', 'my @l = map {\n=pod\n=cut\n$_ * 2 } 1, 2;\nsay "@l";\nmy $i = 0;\nif ($i) { say 1; }\n=pod\n=cut\nelse { say "e"; }\nfor ($i = 0; $i < 1; $i++) {\n=pod\n=cut\n}\nsay $i;', out='2 4\ne\n1\n'),
    c('T675', 'TRAPS; PLAN 16 review', r"""sub codes($s) { return join " ", map { sprintf "%X", ord } split //, $s } say codes(uc "\x{345}\x{301}"); say codes(uc "\x{345}\x{301}\x{345}"); say codes(uc "a\x{345}\x{300}"); say codes(uc "\x{345}a\x{301}"); say codes(ucfirst "\x{345}\x{301}"); say codes(lc "\x{345}\x{301}");""", out='301 399\n301 399\n41 300 399\n399 41 301\n399 301\n345 301\n'),
    c('T675-marks', 'TRAPS; PLAN 16 review', r"""my ($moved, $marks, $differ) = (0, 0, 0); for my $c (0 .. 0x10FFFF) { next if $c >= 0xD800 && $c <= 0xDFFF; my $s = chr $c; my $m = uc("\x{345}" . $s) ne "\x{399}" . uc($s); my $k = $s =~ /\p{M}/; $moved++ if $m; $marks++ if $k; $differ++ if $m != $k; } say "$moved $marks $differ";""", out='2501 2501 0\n'),
    c('T676', 'TRAPS; PLAN 16 review', 'my @a = (1, 2); $#a = 0 or die "e\\n";', exit=255, err='Found = in conditional, should be == at .*\\ne\\n'),
    c('T676-true', 'TRAPS; PLAN 16 review', 'no warnings; my @a = (1, 2); $#a = -1 and die "e\\n"; say "past";', exit=255, err='^e\\n$'),
    c('T677', 'TRAPS; PLAN 16 review', r"""my $e = ""; say "\U\u$e\Eabc"; say "\L\l$e\EABC"; say "\Q\u$e\Ea.c"; say "\L\u$e\Eabc"; say "\U\l$e\EABC"; say "\L\u$e\Eabc \uxyz"; say "\u\U$e\Eabc";""", out='abc\nABC\na.c\nAbc\naBC\nAbc Xyz\nAbc\n'),
    c('T677-own', 'TRAPS; PLAN 16 review', r"""say "\U\u\Eabc"; say "\L\l\EABC"; say "\Q\u\Ea.c"; say "\Q\l\EA.C";""", out='ABC\nabc\na\\.c\nA\\.C\n'),
]
