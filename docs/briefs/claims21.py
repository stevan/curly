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
