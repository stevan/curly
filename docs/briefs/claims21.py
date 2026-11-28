# Step 21's statements about perl, as claims.py's rows: stdin, @ARGV, %ENV,
# exit, a file handle after say, print and printf. claims.py reads it. A row
# may say `stdin` (bytes), `args` (a list) and `env` (a dict), which perl is
# given as a golden test's headers give them.
#
#     python3 docs/briefs/claims.py T501 T502
def c(id, where, code, **said):
    return (id, where, code, said)

OPEN = "use open ':std', ':encoding(UTF-8)'; "

STEP21 = [
    # ---- found proposing step 21 (PLAN 21; TRAPS T500 to T515)
    # T500: printf to STDERR formats, as printf to stdout does. The language
    # printed the format as it stands and the values after it, a WRONG of
    # the merge of steps 15 and 16 (15b's handle, 16b's printf).
    c('T500', 'TRAPS; PLAN 21', 'printf STDERR "%d-%s\\n", 5, "a"; printf STDOUT "%03d\\n", 7; printf(STDOUT "%s\\n", "b");', out='007\nb\n', err=r'^5-a\n$'),
    c('T500-say', 'TRAPS; PLAN 21', 'say STDOUT "a", 1; print STDOUT "b\\n";', out='a1\nb\n'),
    c('T500-bare', 'PLAN 21', 'for ("x") { print STDOUT; }', out='x'),
    # T501: a readline, or an assignment of one, as the whole test of a
    # loop is tested with `defined`: a last line `0` is read. Brackets and
    # a unary plus between change nothing; the target of the assignment may
    # be an element. Not under `until`, nor in an `if`, nor beside `&&`.
    c('T501', 'TRAPS; PLAN 21', 'while (my $l = <STDIN>) { print "[$l]" } say "end";', stdin=b'a\n0', out='[a\n][0]end\n'),
    c('T501-assign', 'TRAPS; PLAN 21', 'my $l; while ($l = <STDIN>) { print "[$l]" } say "end";', stdin=b'a\n0', out='[a\n][0]end\n'),
    c('T501-brackets', 'TRAPS; PLAN 21', 'while ((my $l = +<STDIN>)) { print "[$l]" } say "end";', stdin=b'a\n0', out='[a\n][0]end\n'),
    c('T501-element', 'TRAPS; PLAN 21', 'my %h; while ($h{x} = <STDIN>) { print "[$h{x}]" } say "end";', stdin=b'a\n0', out='[a\n][0]end\n'),
    c('T501-for', 'TRAPS; PLAN 21', 'for (;my $l = <STDIN>;) { print "[$l]" } say "end";', stdin=b'a\n0', out='[a\n][0]end\n'),
    c('T501-modifier', 'TRAPS; PLAN 21', 'my $l; print "[$l]" while $l = <STDIN>; say "end";', stdin=b'a\n0', out='[a\n][0]end\n'),
    c('T501-until', 'TRAPS; PLAN 21', 'my $l; until (!($l = <STDIN>)) { print "[$l]" } say "end";', stdin=b'a\n0', out='[a\n]end\n'),
    c('T501-until-plain', 'TRAPS; PLAN 21', 'my $l; until ($l = <STDIN>) { say "x"; last } say "end";', stdin=b'0', out='x\nend\n'),
    c('T501-if', 'TRAPS; PLAN 21', 'if (my $l = <STDIN>) { print "[$l]" } else { say "false" }', stdin=b'0', out='false\n'),
    c('T501-and', 'TRAPS; PLAN 21', 'my $l; my $go = 1; while ($go && ($l = <STDIN>)) { print "[$l]" } say "end";', stdin=b'a\n0', out='[a\n]end\n'),
    c('T501-concat', 'TRAPS; PLAN 21', 'my $l = ""; while ($l .= <STDIN>) { last if length($l) > 3 } say "[$l]";', stdin=b'ab\n0', out='[ab\n0]\n'),
    c('T501-defined', 'PLAN 21', 'while (defined(my $l = <STDIN>)) { print "[$l]" } say "end";', stdin=b'a\n0', out='[a\n][0]end\n'),
    # T502: a line is bytes, one character each, without `use open`; with
    # it, UTF-8, and perl warns of every malformed sequence, surrogate,
    # character past U+10FFFF and noncharacter, and gives a line that ends
    # in a character cut short at the end of the input as undef, in silence.
    c('T502-bytes', 'TRAPS; PLAN 21', 'my $x = <STDIN>; say length $x; say ord $x;', stdin=b'\xc3\xa9', out='2\n195\n'),
    c('T502-latin1', 'TRAPS; PLAN 21', 'my $x = <STDIN>; say length $x; say ord $x;', stdin=b'\xe9', out='1\n233\n'),
    c('T502-utf8', 'TRAPS; PLAN 21', OPEN + 'my $x = <STDIN>; say length $x; say ord $x; print $x;', stdin=b'\xc3\xa9\n', out='2\n233\n\u00e9\n'),
    c('T502-malformed', 'TRAPS; PLAN 21', OPEN + 'my $x = <STDIN>; say length $x;', stdin=b'\xe9\n', err=r'does not map to Unicode', out='5\n'),
    c('T502-surrogate', 'TRAPS; PLAN 21', OPEN + 'my $x = <STDIN>;', stdin=b'\xed\xa0\x80', err=r'does not map to Unicode'),
    c('T502-past', 'TRAPS; PLAN 21', OPEN + 'my $x = <STDIN>;', stdin=b'\xf4\x90\x80\x80', err=r'does not map to Unicode'),
    c('T502-overlong', 'TRAPS; PLAN 21', OPEN + 'my $x = <STDIN>;', stdin=b'\xc0\x81', err=r'does not map to Unicode'),
    c('T502-nonchar', 'TRAPS; PLAN 21', OPEN + 'my $x = <STDIN>;', stdin=b'\xef\xbf\xbf', err=r'does not map to Unicode'),
    c('T502-nonchar-fdd0', 'TRAPS; PLAN 21', OPEN + 'my $x = <STDIN>;', stdin=b'\xef\xb7\x90', err=r'does not map to Unicode'),
    c('T502-cut', 'TRAPS; PLAN 21', OPEN + 'my $x = <STDIN>; say defined $x ? "line" : "undef";', stdin=b'\xc3', out='undef\n'),
    c('T502-cut-after', 'TRAPS; PLAN 21', OPEN + 'my $x = <STDIN>; say length $x; my $y = <STDIN>; say defined $y ? 1 : 0;', stdin=b'a\xc3', out='1\n0\n'),
    c('T502-bom', 'PLAN 21', OPEN + 'my $x = <STDIN>; say ord $x;', stdin=b'\xef\xbb\xbf', out='65279\n'),
    c('T502-nul', 'PLAN 21', 'my $x = <STDIN>; say length $x; say ord $x;', stdin=b'\x00\n', out='2\n0\n'),
    c('T502-cr', 'PLAN 21', 'my $x = <STDIN>; say length $x;', stdin=b'a\r\n', out='3\n'),
    # T503: @ARGV and %ENV hold bytes, one character each, `use open` or not.
    c('T503-argv', 'TRAPS; PLAN 21', 'say scalar(@ARGV); say "@ARGV"; say length $ARGV[1];', args=['a', 'é'], out='2\na é\n2\n'),
    c('T503-argv-open', 'TRAPS; PLAN 21', OPEN + 'say length $ARGV[0];', args=['é'], out='2\n'),
    c('T503-env', 'TRAPS; PLAN 21', OPEN + 'say $ENV{X}; say length $ENV{Y};', env={'X': '1', 'Y': 'é'}, out='1\n2\n'),
    c('T503-env-empty', 'PLAN 21', 'say exists $ENV{X} ? 1 : 0; say defined $ENV{X} ? 1 : 0; say length $ENV{X}; say exists $ENV{NOPE} ? 1 : 0;', env={'X': ''}, out='1\n1\n0\n0\n'),
    c('T503-shift', 'PLAN 21', 'my $first = shift @ARGV; say $first; say scalar(@ARGV); push @ARGV, "z"; say "@ARGV";', args=['a', 'b'], out='a\n1\nb z\n'),
    # T504: a store to %ENV makes a string of the value.
    c('T504', 'TRAPS; PLAN 21', '$ENV{Z} = [1]; say ref $ENV{Z} ? "ref" : "string"; $ENV{N} = 1.50; say $ENV{N};', out='string\n1.5\n'),
    # T505: `my @ARGV` and `my %ENV` are a program's own, in silence.
    c('T505', 'TRAPS; PLAN 21', 'my @ARGV = (5); say "@ARGV"; my %ENV; say scalar(keys %ENV);', args=['a'], out='5\n0\n'),
    c('T505-scalars', 'PLAN 21', 'my $ARGV = 1; my $ENV = 2; say $ARGV + $ENV;', out='3\n'),
    # T506: exit's status is the number's low eight bits; a Num is cut to
    # its whole part; a string not a number, and undef, are warned of.
    c('T506-3', 'TRAPS; PLAN 21', 'say "a"; exit 3; say "b";', out='a\n', exit=3),
    c('T506-256', 'TRAPS; PLAN 21', 'exit 256;', exit=0),
    c('T506-minus', 'TRAPS; PLAN 21', 'exit -1;', exit=255),
    c('T506-big', 'TRAPS; PLAN 21', 'exit 2**40 + 5;', exit=5),
    c('T506-num', 'TRAPS; PLAN 21', 'exit 1.9;', exit=1),
    c('T506-string', 'TRAPS; PLAN 21', 'exit "2";', exit=2),
    c('T506-not-number', 'TRAPS; PLAN 21', 'exit "abc";', exit=0, err="isn't numeric in exit"),
    c('T506-undef', 'TRAPS; PLAN 21', 'my $u; exit $u;', exit=0, err='uninitialized value \\$u in exit'),
    c('T506-bare', 'PLAN 21', 'print "partial"; exit;', out='partial', exit=0),
    c('T506-brackets', 'PLAN 21', 'exit(7);', exit=7),
    c('T506-modifier', 'PLAN 21', 'exit 3 if 1; say "no";', exit=3),
    c('T506-unary', 'TRAPS; PLAN 21', 'exit 1 + 1;', exit=2),
    c('T506-tighter', 'TRAPS; PLAN 21', 'exit 2 < 3;', exit=2, err='Possible precedence issue with control flow operator'),
    c('T506-or', 'TRAPS; PLAN 21', 'exit 0 || 3;', exit=0, err='Possible precedence issue with control flow operator'),
    c('T506-array', 'PLAN 21', 'my @a = (1, 2, 3); exit @a;', exit=3),
    # T507: exit is no die: a try does not catch it, and it leaves from a
    # sub, a map's block or a sort's.
    c('T507', 'TRAPS; PLAN 21', 'try { say "in"; exit 4 } catch ($e) { say "caught" } say "after";', out='in\n', exit=4),
    c('T507-map', 'TRAPS; PLAN 21', 'sub f() { exit 5 } my @a = map { f() } 1 .. 3; say "no";', exit=5),
    # T508: a readline where a list is wanted reads every line that is
    # left: among a call's arguments, on the right of a list assignment of
    # one target, in brackets before x. Where one value is wanted, a line.
    c('T508-call', 'TRAPS; PLAN 21', 'sub f(@l) { scalar(@l) } say f(<STDIN>);', stdin=b'a\nb\n', out='2\n'),
    c('T508-list', 'TRAPS; PLAN 21', 'my ($p, $q) = <STDIN>; my $r = <STDIN>; print $p, $q; say defined $r ? 1 : 0; my @s = <STDIN>; say scalar(@s);', stdin=b'a\nb\nc\n', out='a\nb\n0\n0\n'),
    c('T508-repeat', 'TRAPS; PLAN 21', 'my $x = <STDIN> x 2; print $x; my @l = (<STDIN>) x 2; print @l;', stdin=b'a\nb\nc\n', out='a\na\nb\nc\nb\nc\n'),
    c('T508-say', 'TRAPS; PLAN 21', 'say "n" if <STDIN> eq "a\\n"; print <STDIN>;', stdin=b'a\nb\nc', out='n\nb\nc'),
    c('T508-eof', 'PLAN 21', 'my $x = <STDIN>; my $y = <STDIN>; say defined $y ? 1 : 0; $y = <STDIN>; say defined $y ? 1 : 0; my @l = <STDIN>; say scalar(@l);', stdin=b'a', out='0\n0\n0\n'),
    c('T508-lines', 'PLAN 21', 'my @l = <STDIN>; say scalar(@l); print $l[-1];', stdin=b'a\n\n0', out='3\n0'),
    c('T508-for', 'PLAN 21', 'for my $l (<STDIN>) { print "<$l>" }', stdin=b'a\nb', out='<a\n><b>'),
    c('T508-number', 'PLAN 21', 'my $n = <STDIN>; say $n + 1; say $n * 2;', stdin=b'5\n', out='6\n10\n'),
    # T508-order: an assignment of a readline to an element works the
    # element out first and reads after, where with a sub on the right the
    # value comes first (D80): perl reads the line into the element.
    c('T508-order', 'TRAPS; PLAN 21', 'my %h; $h{<STDIN>} = <STDIN>; for my $k (keys %h) { print "$k=$h{$k}" }', stdin=b'a\nb\n', out='a\n=b\n'),
    c('T508-order-array', 'TRAPS; PLAN 21', 'my @a = ("x", "y"); $a[<STDIN>] = <STDIN>; print @a;', stdin=b'1\nb\n', out='xb\n'),
    c('T508-order-subs', 'TRAPS; PLAN 21; D80', 'sub k() { say "key"; "k" } sub v() { say "val"; 1 } my %h; $h{k()} = v();', out='val\nkey\n'),
    # T509: eof with brackets and nothing in them is the files of @ARGV, or
    # stdin; eof alone, the handle last read.
    c('T509', 'TRAPS; PLAN 21', 'say eof(STDIN) ? 1 : 0; my $x = <STDIN>; say eof(STDIN) ? 1 : 0;', stdin=b'a\n', out='0\n1\n'),
    c('T509-empty', 'PLAN 21', 'say eof(STDIN) ? 1 : 0;', stdin=b'', out='1\n'),
    c('T509-argv', 'TRAPS; PLAN 21', 'say eof() ? 1 : 0;', stdin=b'x', out='0\n'),
    c('T509-bare', 'TRAPS; PLAN 21', 'my $l = <STDIN>; say eof ? 1 : 0;', stdin=b'x', out='1\n'),
    c('T509-no-brackets', 'PLAN 21', 'say eof STDIN ? 1 : 0;', stdin=b'', out='1\n'),
    # T510: $0 is the path perl was given, which is not the compiled
    # program's.
    c('T510', 'TRAPS; PLAN 21', 'say $0;', out='claim.pl\n'),
    # T511: `while (<STDIN>)` stores to perl's global $_.
    c('T511', 'TRAPS; PLAN 21', 'while (<STDIN>) { print "[$_]" }', stdin=b'a\n0', out='[a\n][0]'),
    # T512: chomp of an assignment chomps the variable.
    c('T512', 'PLAN 21', 'chomp(my $l = <STDIN>); say "[$l]"; my $m; chomp($m = <STDIN>); say "[$m]";', stdin=b'a\nb\n', out='[a]\n[b]\n'),
    c('T512-count', 'PLAN 21', 'my $n = chomp(my $l = <STDIN>); say $n;', stdin=b'a\n', out='1\n'),
    c('T512-undef', 'PLAN 21', 'chomp(my $l = <STDIN>); say defined $l ? 1 : 0;', stdin=b'', out='0\n', err='uninitialized value \\$l in chomp'),
    # T513: readline and its other spellings.
    c('T513', 'PLAN 21', 'my $l = readline(STDIN); print $l; $l = readline STDIN; print $l; my $m = readline(*STDIN); print $m;', stdin=b'a\nb\nc\n', out='a\nb\nc\n'),
    c('T513-glob', 'TRAPS; PLAN 21', 'my @f = <*.nothing-matches>; say scalar(@f);', out='0\n'),
    c('T513-diamond', 'TRAPS; PLAN 21', 'my $l = <>; print $l;', stdin=b'from stdin\n', out='from stdin\n'),
    c('T513-bareword', 'PLAN 21', 'my $l = <FH>;', compiles=False, err='Bareword filehandle "FH" not allowed'),
    # T514: the oracle's perl sees PERL_HASH_SEED in %ENV, which the
    # compiled program does not.
    c('T514', 'TRAPS; PLAN 21', 'say exists $ENV{PERL_HASH_SEED} ? 1 : 0;', out='1\n'),
    # T515: STDIN in a loop's test with a readline under `use open`, and
    # several lines in one read, a character past ASCII in each.
    c('T515', 'PLAN 21', OPEN + 'while (my $l = <STDIN>) { print length($l), $l }', stdin='é\n☺'.encode(), out='2é\n1☺'),
    # T516, found by the review (the builder's own pass): once a line has
    # been read, a die's or a warn's message names the handle and how many
    # lines it has given; not after eof alone, nor after a read that found
    # nothing.
    c('T516', 'TRAPS; PLAN 21, the review', 'my $l = <STDIN>; warn "w"; my $m = <STDIN>; my $n = <STDIN>; warn "w2"; die "d";', stdin=b'a\nb\n', exit=255, err=r'^w at claim\.pl line 2, <STDIN> line 1\.\nw2 at claim\.pl line 2, <STDIN> line 2\.\nd at claim\.pl line 2, <STDIN> line 2\.\n$'),
    c('T516-none', 'TRAPS; PLAN 21, the review', 'say eof(STDIN) ? 1 : 0; my $l = <STDIN>; die "d";', stdin=b'', out='1\n', exit=255, err=r'^d at claim\.pl line 2\.\n$'),
    c('T516-list', 'TRAPS; PLAN 21, the review', 'my @l = <STDIN>; my $e; try { die "t" } catch ($x) { $e = $x } print $e;', stdin=b'a\nb\nc', out='t at claim.pl line 2, <STDIN> line 3.\n'),
    c('T516-newline', 'TRAPS; PLAN 21, the review', 'my $l = <STDIN>; die "x\\n";', stdin=b'a\n', exit=255, err=r'^x\n$'),
    # ---- found by the adversarial review of 21a (TRAPS T517 to T522; D222)
    # T517: exit's argument is a named unary operator's, and perl warns of
    # a sign after it as it does after `length` (T94).
    c('T517', 'TRAPS; D222', 'exit - 1;', exit=255, err=r'^Warning: Use of "exit" without parentheses is ambiguous at claim\.pl line 2\.\n$'),
    c('T517-hard', 'TRAPS', 'exit-1;', exit=255, err=r'^Warning: Use of "exit-1" without parentheses is ambiguous at claim\.pl line 2\.\n$'),
    c('T517-plus', 'TRAPS', 'exit + 1;', exit=1, err=r'^Warning: Use of "exit" without parentheses is ambiguous at claim\.pl line 2\.\n$'),
    c('T517-silent', 'TRAPS', 'exit -1;', exit=255),
    c('T517-silent-plus', 'TRAPS', 'exit +1;', exit=1),
    # T518: a line assigned as the left operand of && or ||, which an if
    # with nothing after its block is: perl warns. Not with an else, nor
    # in an elsif's test, nor as the test of ? :, nor under !, nor on the
    # right of &&, nor before //.
    c('T518', 'TRAPS; D222', 'if (my $l = <STDIN>) { print $l }', stdin=b'a\n', out='a\n', err=r'^Value of <HANDLE> construct can be "0"; test with defined\(\) at claim\.pl line 2\.\n$'),
    c('T518-unless', 'TRAPS; D222', 'my $l; unless ($l = <STDIN>) { say "end" }', stdin=b'', out='end\n', err=r'^Value of <HANDLE> construct can be "0"; test with defined\(\) at claim\.pl line 2\.\n$'),
    c('T518-modifier', 'TRAPS; D222', 'my $l; print "t" if $l = <STDIN>;', stdin=b'a\n', out='t', err=r'^Value of <HANDLE> construct can be "0"; test with defined\(\) at claim\.pl line 2\.\n$'),
    c('T518-and', 'TRAPS; D222', 'my $l; my $x = ($l = <STDIN>) && 1; say $x;', stdin=b'a\n', out='1\n', err=r'^Value of <HANDLE> construct can be "0"; test with defined\(\) at claim\.pl line 2\.\n$'),
    c('T518-or', 'TRAPS; D222', 'my $l; my $x = ($l = <STDIN>) || "f"; print $x;', stdin=b'a\n', out='a\n', err=r'^Value of <HANDLE> construct can be "0"; test with defined\(\) at claim\.pl line 2\.\n$'),
    c('T518-element', 'TRAPS', 'my @a; if ($a[0] = <STDIN>) { print $a[0] }', stdin=b'a\n', out='a\n', err=r'^Value of <HANDLE> construct can be "0"; test with defined\(\) at claim\.pl line 2\.\n$'),
    c('T518-while', 'TRAPS', 'my $l; while (($l = <STDIN>) && 1) { print "[$l]" }', stdin=b'a\n0', out='[a\n]', err=r'^Value of <HANDLE> construct can be "0"; test with defined\(\) at claim\.pl line 2\.\n$'),
    c('T518-else', 'TRAPS; D222', 'if (my $l = <STDIN>) { print $l } else { say "f" }', stdin=b'0', out='f\n'),
    c('T518-elsif-after', 'TRAPS; D222', 'my $l; if ($l = <STDIN>) { print $l } elsif (@ARGV) { say "e" }', stdin=b'a\n', out='a\n'),
    c('T518-elsif', 'TRAPS; D222', 'my $l; if (@ARGV) { say "a" } elsif ($l = <STDIN>) { print $l }', stdin=b'a\n', out='a\n'),
    c('T518-ternary', 'TRAPS; D222', 'my $l; print(($l = <STDIN>) ? "t" : "f");', stdin=b'0', out='f'),
    c('T518-not', 'TRAPS; D222', 'my $l; say "end" if !($l = <STDIN>);', stdin=b'0', out='end\n'),
    c('T518-right', 'TRAPS; D222', 'my $l; my $x = !@ARGV && ($l = <STDIN>); print $x;', stdin=b'a\n', out='a\n'),
    c('T518-dor', 'TRAPS; D222', 'my $l; my $x = ($l = <STDIN>) // "f"; print $x;', stdin=b'', out='f'),
    # T519: perl folds a constant test away, and what is left is the
    # assignment of a line to an element, which works the element out first.
    c('T519', 'TRAPS; D222', 'my %h; $h{<STDIN>} = 1 ? <STDIN> : 2; print %h;', stdin=b'a\nb\n', out='a\nb\n'),
    c('T519-and', 'TRAPS; D222', 'my %h; $h{<STDIN>} = 1 && <STDIN>; print %h;', stdin=b'a\nb\n', out='a\nb\n'),
    c('T519-or', 'TRAPS', 'my %h; $h{<STDIN>} = "" || <STDIN>; print %h;', stdin=b'a\nb\n', out='a\nb\n'),
    c('T519-compared', 'TRAPS', 'my %h; $h{<STDIN>} = 2 > 1 ? <STDIN> : 2; print %h;', stdin=b'a\nb\n', out='a\nb\n'),
    c('T519-builtin', 'TRAPS', 'my %h; $h{<STDIN>} = length("a") ? <STDIN> : 2; print %h;', stdin=b'a\nb\n', out='a\nb\n'),
    c('T519-not-folded', 'TRAPS', 'my %h; $h{<STDIN>} = @ARGV ? 2 : <STDIN>; print %h;', stdin=b'a\nb\n', out='b\na\n'),
    # T520: and a loop's test that folds to T501's is tested with defined.
    c('T520', 'TRAPS; D222', 'my $l; while (1 && ($l = <STDIN>)) { print "[$l]" }', stdin=b'a\n0', out='[a\n][0]'),
    c('T520-ternary', 'TRAPS; D222', 'my $l; while (1 ? ($l = <STDIN>) : 0) { print "[$l]" }', stdin=b'a\n0', out='[a\n][0]'),
    c('T520-bare', 'TRAPS', 'while (1 && <STDIN>) { print "[$_]" }', stdin=b'a\n0', out='[a\n][0]'),
    c('T520-for', 'TRAPS', 'my $l; for (; 1 && ($l = <STDIN>);) { print "[$l]" }', stdin=b'a\n0', out='[a\n][0]'),
    c('T520-modifier', 'TRAPS', 'my $l; print "[$l]" while !0 && ($l = <STDIN>);', stdin=b'a\n0', out='[a\n][0]'),
    c('T520-not-folded', 'TRAPS', 'my $l; my $go = 1; while ($go && ($l = <STDIN>)) { print "[$l]" }', stdin=b'a\n0', out='[a\n]'),
    # T521: a sub called for nothing hands that on to what it gives back,
    # and a readline there reads one line.
    c('T521', 'TRAPS; PLAN 21, the review', 'sub f() { return <STDIN> } f(); print <STDIN>;', stdin=b'a\nb\nc\n', out='b\nc\n'),
    c('T521-last', 'TRAPS', 'sub f() { <STDIN> } f(); print <STDIN>;', stdin=b'a\nb\nc\n', out='b\nc\n'),
    c('T521-list', 'TRAPS', 'sub f() { return (<STDIN>, 1) } f(); print <STDIN>;', stdin=b'a\nb\nc\n', out='b\nc\n'),
    c('T521-two', 'TRAPS', 'sub f() { return (<STDIN>, <STDIN>) } f(); print <STDIN>;', stdin=b'a\nb\nc\n', out='c\n'),
    c('T521-repeat', 'TRAPS', 'sub f() { return (<STDIN>) x 2 } f(); print <STDIN>;', stdin=b'a\nb\nc\n', out='b\nc\n'),
    c('T521-handed', 'TRAPS', 'sub g() { <STDIN> } sub f() { return (g(), 1) } f(); print <STDIN>;', stdin=b'a\nb\nc\n', out='b\nc\n'),
    c('T521-slice', 'TRAPS', 'sub f() { return (<STDIN>)[0] } f(); print <STDIN>;', stdin=b'a\nb\nc\n', out=''),
    c('T521-sort', 'TRAPS', 'sub f() { return sort <STDIN> } f(); print <STDIN>;', stdin=b'a\nb\nc\n', out=''),
    c('T521-wanted', 'TRAPS', 'sub f() { return <STDIN> } my @l = f(); print <STDIN>; say scalar(@l);', stdin=b'a\nb\nc\n', out='3\n'),
    # T522: chomp of an assignment is worth what chomp took.
    c('T522', 'TRAPS; PLAN 21, the review', 'sub f() { chomp(my $x = <STDIN>) } say f();', stdin=b'a\n', out='1\n'),
    c('T522-map', 'TRAPS', 'my @l = map { chomp(my $x = $_) } "a\\n", "b"; say "@l";', out='1 0\n'),
]

# ---- step 21b, files and handles (PLAN 21, "21b, the proposal"; TRAPS T680
# to T699). A row may say `files`, a dict of name to bytes, which stand in
# the directory perl runs in.
ABC = {'in.txt': b'a\nb\nc\n'}
STEP21B = [
    # T680: perl's errno after an open that worked is ENOTTY, 25 (perl asks
    # whether the file is a terminal), and an uncaught die exits with errno.
    c('T680', 'TRAPS; PLAN 21b', 'open(my $fh, "<", "in.txt"); say 0+$!; die "x\\n";', files=ABC, out='25\n', err=r'^x\n$', exit=25),
    c('T680-write', 'TRAPS; PLAN 21b', 'open(my $o, ">", "o.txt"); my $a = 0+$!; open(my $p, ">>", "o.txt"); say $a, " ", 0+$!; die "x\\n";', out='25 25\n', err=r'^x\n$', exit=25),
    c('T680-fail', 'TRAPS; PLAN 21b', 'open(my $fh, "<", "nope.txt") or die "cannot: $!";', out='', err=r'^cannot: No such file or directory at claim.pl line 2\.\n$', exit=2),
    c('T680-value', 'PLAN 21b', 'my $r = open(my $fh, "<", "in.txt"); my $s = open(my $g, "<", "nope"); say "[$r]", defined $s ? "def" : "undef";', files=ABC, out='[1]undef\n'),
    # T681: a readline that meets the end of its input sets errno to 0,
    # where one value is wanted and where a list is; eof() does not, and
    # after it the end is known and no read looks again. stdin the same.
    c('T681', 'TRAPS; PLAN 21b', 'open(my $fh, "<", "in.txt"); my @e; my $l = <$fh>; push @e, 0+$!; $l = <$fh>; $l = <$fh>; push @e, 0+$!; $l = <$fh>; push @e, 0+$!; say "@e"; die "x\\n";', files=ABC, out='25 25 0\n', err=r'^x\n$', exit=255),
    c('T681-again', 'TRAPS; PLAN 21b', 'open(my $fh, "<", "in.txt"); my @a = <$fh>; my @e = (0+$!); open(my $g, "<", "in.txt"); my $l = <$fh>; push @e, 0+$!; @a = <$fh>; push @e, 0+$!; say "@e";', files=ABC, out='0 25 25\n'),
    c('T681-eof', 'TRAPS; PLAN 21b', 'open(my $fh, "<", "e.txt"); my $x = eof($fh); my @e = (0+$!); my $l = <$fh>; push @e, 0+$!; say "@e";', files={'e.txt': b''}, out='25 25\n'),
    c('T681-partial', 'TRAPS; PLAN 21b', 'open(my $fh, "<", "n.txt"); my $l = <$fh>; my @e = (0+$!); $l = <$fh>; push @e, 0+$!, "[$l]"; say "@e";', files={'n.txt': b'x\ny'}, out='25 0 [y]\n'),
    c('T681-while', 'TRAPS; PLAN 21b', 'open(my $fh, "<", "in.txt"); while (my $l = <$fh>) { } die "x\\n";', files=ABC, out='', err=r'^x\n$', exit=255),
    c('T681-stdin', 'TRAPS; PLAN 21b', 'open(my $fh, "<", "in.txt"); my $l = <STDIN>; my @e = (0+$!); $l = <STDIN>; push @e, 0+$!; open($fh, "<", "in.txt"); $l = <STDIN>; push @e, 0+$!; say "@e";', files=ABC, stdin=b'q\n', out='25 0 25\n'),
    c('T681-stdin-eof', 'TRAPS; PLAN 21b', 'open(my $fh, "<", "in.txt"); my $x = eof(STDIN); my $l = <STDIN>; say 0+$!;', files=ABC, out='25\n'),
    c('T681-others', 'PLAN 21b', 'open(my $o, ">", "o.txt"); my @e; $! = 7; print $o "x" x 20000; say $o "y"; printf $o "%d", 5; push @e, 0+$!; close($o); push @e, 0+$!; open(my $fh, "<", "in.txt"); $! = 7; my $l = <$fh>; my $x = eof($fh); close($fh); push @e, 0+$!; try { die "d" } catch ($e) { } warn "w\\n"; push @e, 0+$!; say "@e";', files=ABC, out='7 7 7 7\n', err=r'^w\n$'),
    c('T681-use-open', 'PLAN 21b', OPEN + 'my @e; open(my $fh, "<", "in.txt"); push @e, 0+$!; my $l = <$fh>; $l = <$fh>; $l = <$fh>; push @e, 0+$!; $l = <$fh>; push @e, 0+$!; open(my $u, "<", "e.txt"); my $x = eof($u); $l = <$u>; push @e, 0+$!; open(my $o, ">", "o.txt"); print $o chr(233), chr(9786); close($o); push @e, 0+$!; say "@e"; die "x\\n";', files={**ABC, 'e.txt': b''}, out='25 25 0 25 25\n', err=r'^x\n$', exit=25),
    # And a number that underflowed, whose errno an uncaught die exits with
    # (T319, D151): an open, and a read that meets the end, set it after.
    c('T680-underflow', 'TRAPS; PLAN 21b', 'my $s = "1e-400"; my $t = $s + 0; say 0+$!; open(my $fh, "<", "in.txt"); die "x\\n";', files=ABC, out='34\n', err=r'^x\n$', exit=25),
    # (Written as a constant, perl works the sum out as it compiles, and
    # errno is 0 again when the program starts.)
    c('T680-folded', 'PLAN 21b', 'my $t = "1e-400" + 0; say 0+$!; die "x\\n";', out='0\n', err=r'^x\n$', exit=255),
    c('T681-underflow', 'TRAPS; PLAN 21b', 'my $s = "1e-400"; my $t = $s + 0; print 0+$!; my $l = <STDIN>; die "x\\n";', out='34', err=r'^x\n$', exit=255),
    # T682: once a line has been read from a handle, a message of die or
    # warn that does not end in a newline names it and its line, while the
    # handle lives and is not closed; eof($fh) makes it the handle last
    # read; a handle that is freed, or closed, is named no more.
    c('T682', 'TRAPS; PLAN 21b', 'open(my $fh, "<", "in.txt"); warn "w0"; my $e = eof($fh); warn "w1"; my $l = <$fh>; warn "w2"; $l = <STDIN>; warn "w3"; $e = eof($fh); warn "w4"; close($fh); warn "w5";', files=ABC, err=r'^w0 at claim.pl line 2\.\nw1 at claim.pl line 2\.\nw2 at claim.pl line 2, <\$fh> line 1\.\nw3 at claim.pl line 2\.\nw4 at claim.pl line 2, <\$fh> line 1\.\nw5 at claim.pl line 2\.\n$'),
    c('T682-freed', 'TRAPS; PLAN 21b', '{ open(my $in, "<", "in.txt"); my $l = <$in>; warn "w1"; } warn "w2"; sub rd($h) { my $l = <$h>; return $l } open(my $fh, "<", "in.txt"); rd($fh); warn "w3"; my $g = $fh; undef $fh; warn "w4"; undef $g; warn "w5";', files=ABC, err=r'^w1 at claim.pl line 2, <\$in> line 1\.\nw2 at claim.pl line 2\.\nw3 at claim.pl line 2, <\$fh> line 1\.\nw4 at claim.pl line 2, <\$fh> line 1\.\nw5 at claim.pl line 2\.\n$'),
    c('T682-all', 'PLAN 21b', 'open(my $fh, "<", "in.txt"); my @a = <$fh>; warn "w1"; open(my $o, ">", "o.txt"); print $o "x"; close($o); warn "w2"; open(my $e, "<", "e.txt"); my $l = <$e>; warn "w3";', files={**ABC, 'e.txt': b''}, err=r'^w1 at claim.pl line 2, <\$fh> line 3\.\nw2 at claim.pl line 2, <\$fh> line 3\.\nw3 at claim.pl line 2\.\n$'),
    # T683: the handle is worked out before the list, a block too.
    c('T683', 'TRAPS; PLAN 21b', 'open(my $a, ">", "a.txt"); open(my $b, ">", "b.txt"); my $fh = $a; sub f() { $fh = $b; return "x" } print $fh f(); print { print "block "; $a } f(), g(); sub g() { print "list\\n"; return "y" } close($a); close($b); open(my $in, "<", "a.txt"); print <$in>; say eof($in) ? " end" : " more";', out='block list\nxxy end\n'),
    # T684: after a handle the brackets are no argument list, and perl's
    # guess takes a variable, a blank and what begins a value for a handle.
    c('T684', 'TRAPS; PLAN 21b', 'open(my $o, ">", "o.txt"); print $o (1+2)*3; print $o ("a") x 2; print $o -1; print $o !1; print $o "s", 5; say $o " ", 3; close($o); open(my $in, "<", "o.txt"); print <$in>;', out='9aa-1s5 3\n'),
    c('T684-not', 'TRAPS; PLAN 21b', 'my $x = 7; my $y = 2; print $x - 1; print $x if $y; print $x x 2; print $x, "\\n";', out='67777\n'),
    c('T684-comma', 'TRAPS; PLAN 21b', 'open(my $o, ">", "o.txt"); print $o, "a"; say $o;', outre=r'GLOB\(0x[0-9a-f]+\)aGLOB\(0x[0-9a-f]+\)\n'),
    c('T684-no-blank', 'TRAPS; PLAN 21b', 'open(my $o, ">", "o.txt"); print $o"a";', err='String found where operator expected', out=''),
    c('T684-backslash', 'TRAPS; PLAN 21b', 'my @a; open(my $o, ">", "o.txt"); print $o \\@a;', err='Backslash found where operator expected', out=''),
    c('T684-brackets', 'PLAN 21b', 'open(my $o, ">", "o.txt"); print($o "a"); print {$o} "b"; print {$o}"c"; printf {$o} "%s", "d"; printf $o ("%s\\n", "e"); close($o); open(my $in, "<", "o.txt"); print <$in>;', out='abcde\n'),
    c('T684-empty-block', 'PLAN 21b', 'open(my $o, ">", "o.txt"); print {$o};', compiles=False, err='syntax error'),
    c('T684-not-a-handle', 'PLAN 21b', 'my $x = 5; print $x "a";', out='', exit=255, err=r'Can\'t use string \("5"\) as a symbol ref'),
    c('T684-heredoc', 'PLAN 21b', 'open(my $o, ">", "o.txt"); print $o <<"E";\nh1\nE\nclose($o); open(my $in, "<", "o.txt"); print <$in>;', out='h1\n'),
    # T685: open of a variable that holds a handle opens that handle again:
    # a copy sees the new file, and the count of lines goes on.
    c('T685', 'TRAPS; PLAN 21b', 'open(my $fh, "<", "in.txt"); my $g = $fh; my $l = <$fh>; open($fh, "<", "n.txt"); print "g:", scalar(<$g>); say $g == $fh ? "same" : "differ"; warn "w";', files={**ABC, 'n.txt': b'x\ny'}, out='g:x\nsame\n', err=r'^w at claim.pl line 2, <\$fh> line 2\.\n$'),
    c('T685-fails', 'TRAPS; PLAN 21b', 'open(my $fh, "<", "in.txt"); my $g = $fh; open($fh, "<", "nope"); my $l = <$g>;', files=ABC, err=r'readline\(\) on closed filehandle \$fh'),
    c('T685-not', 'TRAPS; PLAN 21b', 'my $fh = 5; open($fh, "<", "in.txt"); say "after";', files=ABC, out='', exit=255, err=r"Can't use string \(\"5\"\) as a symbol ref"),
    c('T685-ref', 'PLAN 21b', 'my $fh = [1]; open($fh, "<", "in.txt"); say "after";', files=ABC, out='', exit=255, err='Not a GLOB reference'),
    # T686: an open that fails leaves a handle in the variable all the same.
    c('T686', 'TRAPS; PLAN 21b', 'my $r = open(my $fh, "<", "nope"); say defined $fh ? "def" : "undef", " ", ref($fh), " ", $fh ? "true" : "false";', out='def GLOB true\n'),
    c('T686-kind', 'PLAN 21b', 'open(my $fh, "<", "in.txt"); open(my $h, "<", "in.txt"); my $g = $fh; say ref($fh), " ", ref(\\$fh), " ", $g == $fh ? 1 : 0, $h == $fh ? 1 : 0, $h != $fh ? 1 : 0; say "$fh" =~ /^GLOB\\(0x[0-9a-f]+\\)$/ ? "address" : "other";', files=ABC, out='GLOB REF 101\naddress\n'),
    # T687: what perl says of a handle that is closed, or open the other way.
    c('T687-close', 'TRAPS; PLAN 21b', 'open(my $fh, "<", "in.txt"); my $c = close($fh); my $d = close($fh); say "[$c][$d]", 0+$!; say eof($fh) ? "eof" : "not";', files=ABC, out='[1][]9\neof\n'),
    c('T687-read', 'TRAPS; PLAN 21b', 'open(my $fh, "<", "in.txt"); close($fh); my $l = <$fh>;', files=ABC, err=r'readline\(\) on closed filehandle \$fh'),
    c('T687-print', 'TRAPS; PLAN 21b', 'open(my $fh, ">", "o.txt"); close($fh); print $fh "x";', err=r'print\(\) on closed filehandle \$fh'),
    c('T687-input', 'TRAPS; PLAN 21b', 'open(my $fh, "<", "in.txt"); print $fh "x"; say $fh "x"; printf $fh "x";', files=ABC, err=r'(Filehandle \$fh opened only for input at claim.pl line 2\.\n){3}'),
    c('T687-output', 'TRAPS; PLAN 21b', 'open(my $o, ">", "o.txt"); my $l = <$o>; my @l = <$o>; my $e = eof($o);', err=r'(Filehandle \$o opened only for output at claim.pl line 2\.\n){3}'),
    # T688: what perl opens that is no file with a name.
    c('T688-undef', 'TRAPS; PLAN 21b', 'my $r = open(my $fh, "<", undef); say $r;', out='1\n'),
    c('T688-nul', 'TRAPS; PLAN 21b', 'open(my $f, "<", "in.txt\\0x") or print "no: $!\\n";', files=ABC, out='no: No such file or directory\n', err=r'Invalid \\0 character in pathname for open'),
    c('T688-dir', 'TRAPS; PLAN 21b', 'my $r = open(my $d, "<", "."); my $l = <$d>; say $r, defined $l ? "line" : "undef", " $!";', out='1undef Is a directory\n'),
    c('T688-dir-write', 'PLAN 21b', 'open(my $d, ">", ".") or print "no: $!\\n";', out='no: Is a directory\n'),
    c('T688-empty', 'PLAN 21b', 'open(my $f, "<", "") or print "no: $!\\n";', out='no: No such file or directory\n'),
    # T689: $! in a string, and what perl reads on into.
    c('T689', 'TRAPS; PLAN 21b', 'open(my $q, "<", "nope") or print "e1: $!\\n"; print "e2: $!.\\n"; print "e3: $!::x\\n"; print "e4: ${!}\\n"; print "e5: $!->\\n"; say "e6: " . $!; say $! + 0; say $! ? "t" : "f";', out='e1: No such file or directory\ne2: No such file or directory.\ne3: No such file or directory::x\ne4: No such file or directory\ne5: No such file or directory->\ne6: No such file or directory\n2\nt\n'),
    c('T689-element', 'TRAPS; PLAN 21b', 'open(my $q, "<", "nope"); print "$!{ENOENT}|"; print "$![0]\\n";', outre=r'\d+\|\n', err=r'Use of uninitialized value \$!\[0\]'),
    c('T689-arrow', 'PLAN 21b', 'open(my $q, "<", "nope"); print "$!->[0]\\n";', out='', exit=2, err='as an ARRAY ref'),
    c('T689-past', 'TRAPS; PLAN 21b', 'say "[$!]"; open(my $f, "<", "in.txt"); say "[$!]";', files=ABC, out='[]\n[Inappropriate ioctl for device]\n'),
    # T690: the forms of open perl takes in silence.
    c('T690', 'TRAPS; PLAN 21b', 'open(my $a, "in.txt"); open(my $b, "<in.txt"); open(my $c, "<:raw", "in.txt"); open(my $d, "+<", "in.txt"); open(my $e, "< ", "in.txt"); my $m = "<"; open(my $f, $m, "in.txt"); open my $g, "<", "in.txt" or die; print scalar(<$a>), scalar(<$b>), scalar(<$c>), scalar(<$d>), scalar(<$e>), scalar(<$f>), scalar(<$g>);', files=ABC, out='a\n' * 7),
    c('T690-bareword', 'TRAPS; PLAN 21b', 'open(FH, "<", "in.txt");', compiles=False, err='Bareword filehandle "FH" not allowed'),
    c('T690-mode', 'PLAN 21b', 'open(my $f, "r", "in.txt");', out='', exit=255, err="Unknown open\\(\\) mode 'r'"),
    # T691: bytes and characters, as stdin and stdout have them (T502).
    c('T691', 'TRAPS; PLAN 21b', 'open(my $fh, "<", "u.txt"); my $l = <$fh>; say length($l); open(my $o, ">", "o.txt"); print $o chr(233); close($o); open($fh, "<", "o.txt"); $l = <$fh>; say length($l), " ", ord($l);', files={'u.txt': b'caf\xc3\xa9\n'}, out='6\n1 233\n'),
    c('T691-wide', 'TRAPS; PLAN 21b', 'open(my $o, ">", "o.txt"); print $o chr(9786);', err='Wide character in print'),
    c('T691-open', 'TRAPS; PLAN 21b', OPEN + 'open(my $fh, "<", "u.txt"); my $l = <$fh>; say length($l); open(my $o, ">", "o.txt"); print $o chr(233), chr(9786); close($o); say -s "o.txt"; open($fh, "<", "o.txt"); $l = <$fh>; say length($l), " ", ord($l);', files={'u.txt': b'caf\xc3\xa9\n'}, out='5\n5\n2 233\n'),
    c('T691-malformed', 'TRAPS; PLAN 21b', OPEN + 'open(my $fh, "<", "b.txt"); my $l = <$fh>; say length($l);', files={'b.txt': b'x\xe9y\n'}, out='7\n', err='does not map to Unicode'),
    c('T691-cut', 'TRAPS; PLAN 21b', OPEN + 'open(my $fh, "<", "c.txt"); my $l = <$fh>; say length($l);', files={'c.txt': b'a\xc3'}, out='1\n'),
    c('T691-nonchar', 'PLAN 21b', OPEN + 'open(my $o, ">", "o.txt"); print $o chr(0xFFFF);', err='non-character U\\+FFFF'),
    c('T691-crlf', 'PLAN 21b', 'open(my $fh, "<", "r.txt"); my $l = <$fh>; say length($l); $l = <$fh>; say length($l);', files={'r.txt': b'a\r\nb\r'}, out='3\n2\n'),
    # T692: what is printed to a file is held back, so a second handle on
    # the file sees it late: after 8192 bytes, or when the first is closed.
    c('T692', 'TRAPS; PLAN 21b', 'open(my $o, ">", "o.txt"); print $o "abc\\n"; open(my $in, "<", "o.txt"); my $l = <$in>; say defined $l ? "seen" : "not yet"; close($o); $l = <$in>; say defined $l ? "seen" : "not yet"; open(my $p, ">", "p.txt"); print $p "x" x 8191; say -s "p.txt"; print $p "y"; say -s "p.txt";', out='not yet\nnot yet\n0\n8192\n'),
    c('T692-dropped', 'TRAPS; PLAN 21b', 'sub save($t) { open(my $o, ">", "o.txt"); print $o $t; } save("kept\\n"); open(my $in, "<", "o.txt"); print <$in>;', out='kept\n'),
    # T693: while (my $l = <$fh>) is tested with defined, as stdin's is, and
    # the other shapes warn or are $_'s as stdin's do (T501, T511, T518).
    c('T693', 'TRAPS; PLAN 21b', 'open(my $fh, "<", "z.txt"); while (my $l = <$fh>) { print "[$l]" } say "end";', files={'z.txt': b'a\n0'}, out='[a\n][0]end\n'),
    c('T693-if', 'TRAPS; PLAN 21b', 'open(my $fh, "<", "in.txt"); if (my $l = <$fh>) { print $l }', files=ABC, out='a\n', err=r'Value of <HANDLE> construct can be "0"'),
    c('T693-list', 'PLAN 21b', 'open(my $fh, "<", "in.txt"); my ($p, @rest) = <$fh>; print $p, scalar(@rest), "\\n"; my @none = <$fh>; say scalar(@none);', files=ABC, out='a\n2\n0\n'),
    # (An element in the angle brackets is a glob, of the handle's address.)
    c('T693-element', 'TRAPS; PLAN 21b', 'open(my $fh, "<", "in.txt"); my %h = (fh => $fh); my $l = <$h{fh}>; say $l =~ /^GLOB\\(0x[0-9a-f]+\\)$/ ? "a glob" : "a line";', files=ABC, out='a glob\n'),
    # A handle is thrown as itself, and is in a closure, a hash, an argument.
    c('21b-values', 'PLAN 21b', 'open(my $fh, "<", "in.txt"); try { die $fh } catch ($e) { print scalar(<$e>) } my %h = (in => $fh); my $rd = sub { my $h = $h{in}; return scalar(<$h>) }; print $rd->(); sub third($h) { return scalar(<$h>) } print third($fh);', files=ABC, out='a\nb\nc\n'),
    c('21b-append', 'PLAN 21b', 'open(my $o, ">", "o.txt"); print $o "a\\n"; close($o); open($o, ">>", "o.txt"); print $o "b\\n"; close($o); open($o, ">>", "new.txt"); print $o "n\\n"; close($o); open($o, ">", "o2.txt"); close($o); open(my $in, "<", "o.txt"); print <$in>; open($in, "<", "new.txt"); print <$in>; open($in, "<", "o2.txt"); my @l = <$in>; say scalar(@l);', out='a\nb\nn\n0\n'),
    c('21b-or-die', 'PLAN 21b', 'open(my $fh, "<", "in.txt") or die "no: $!"; open(my $g, "<", "in.txt") || die "no: $!"; close($fh) or die "no close: $!"; close $g; print "ok\\n"; open(my $h, "<", "nope") || die "no: $!\\n";', files=ABC, out='ok\n', err=r'^no: No such file or directory\n$', exit=2),
    c('21b-unflushed', 'PLAN 21b', 'open(my $o, ">", "o.txt"); print $o "kept\\n"; open(my $q, ">", "q.txt"); print $q "too\\n"; exit 3;', out='', exit=3),
    # ---- found by the review of 21b (TRAPS T694, T695)
    # T694: what follows open's mode is a list, to perl: an array there is
    # its elements, and a line read reads every line.
    c('T694', 'TRAPS; PLAN 21b', 'my @n = ("in.txt"); open(my $fh, "<", @n) or die "no\\n"; print scalar(<$fh>); open(my $g, "<", map { $_ } "in.txt") or die "no\\n"; print scalar(<$g>);', files=ABC, out='a\na\n'),
    c('T694-two', 'TRAPS; PLAN 21b', 'my @n = ("in.txt", "b"); open(my $fh, "<", @n); say "after";', files=ABC, out='', exit=255, err=r"More than one argument to open"),
    c('T694-one-value', 'PLAN 21b', 'my @r = (open(my $f, "<", "nope")); print scalar(@r), defined $r[0] ? "d" : "u", "\\n"; open($f, "<", "in.txt"); my @e = (eof($f)); my @c = (close($f)); print scalar(@e), "[$e[0]]", scalar(@c), "[$c[0]]\\n";', files=ABC, out='1u\n1[]1[1]\n'),
    # T695: $! is a variable of perl's own, read when the operator it is
    # an operand of runs: after a call that comes later in the list, the
    # row of dots, or the key. In a string it is made where it stands, and
    # an assignment to a variable reads it there.
    c('T695', 'TRAPS; PLAN 21b', 'sub g() { open(my $d, ">", "."); return "|" } sub n() { open(my $d, "<", "nope"); return "" } n(); say $!, g(); n(); say $! . g(); n(); my @l = ($!, g()); say "@l"; n(); my %h; $h{g()} = $!; say %h; n(); say join(",", $!, g());', out='Is a directory|\nIs a directory|\nIs a directory |\n|Is a directory\nIs a directory,|\n'),
    c('T695-string', 'TRAPS; PLAN 21b', 'sub g() { open(my $d, ">", "."); return "|" } sub n() { open(my $d, "<", "nope"); return "" } n(); say "$!" . g(); n(); say "e: $!", g(); n(); my $e = $!; g(); say $e;', out='No such file or directory|\ne: No such file or directory|\nNo such file or directory\n'),
    c('T695-underflow', 'PLAN 21b', 'open(my $d, "<", "nope"); my $s = "1e-400"; say $!, $s + 0; open($d, "<", "nope"); say "[$!]", $s + 0;', out='Numerical result out of range0\n[No such file or directory]0\n'),
    # (`isa` after a variable after print is the operator: what is printed
    # is whether $x is one.)
    c('21b-isa', 'PLAN 21b', 'my $x = 5; print $x isa Foo; say "after";', out='after\n'),
    # T696: perl's guess of a file handle is made after every list
    # operator, and what it then finds is no program.
    c('T696', 'TRAPS; PLAN 21b', 'my $x = 5; warn $x -1; say "after";', compiles=False, err='Missing comma after first argument to warn function'),
    c('T696-die', 'TRAPS; PLAN 21b', 'my $x = 5; die $x -1;', compiles=False, err='Missing comma after first argument to die function'),
    c('T696-join', 'TRAPS; PLAN 21b', 'my $x = 5; my $s = join $x -1, "a", "b"; say $s;', compiles=False, err='Missing comma after first argument to join or string function'),
    c('T696-reverse', 'TRAPS; PLAN 21b', 'my $x = 5; my @r = reverse($x -1, 2); say "@r";', compiles=False, err='Missing comma after first argument to reverse function'),
    c('T696-not', 'PLAN 21b', 'my $x = 5; my $s = join $x - 1, "a", "b"; say $s; my @a = (1); push @a, $x -1; say "@a"; sub f { return $x -1 } say f();', out='a4b\n1 4\n4\n'),
]
STEP21 += STEP21B

