# Step 19's statements about perl, as claims.py's rows: a file of its own so
# that step 19, built in a worktree beside step 17a, merges without touching
# the rows other steps add. claims.py reads it.
#
#     python3 docs/briefs/claims.py T540 19-scalar
def c(id, where, code, **said):
    return (id, where, code, said)

STEP19 = [
    # ---- found proposing step 19 (TRAPS; PLAN 19)
    c('T540', 'TRAPS; PLAN 19', r"""my @l = ("ab" =~ /(?:(a)|b)*/); say scalar(@l), defined $l[0] ? "d" : "u"; @l = ("aba" =~ /^(?:(a)|(b))+$/); say "@l"; @l = ("ab" =~ /(?:(a)|(b))*/); say defined $l[0] ? "d" : "u", $l[1];""", out='1u\na b\nub\n'),
    c('T541', 'TRAPS; PLAN 19', r"""say "ab" =~ m|a\|b| ? 1 : 0; say "a|b" =~ m|a\|b| ? 1 : 0; say "a{2}" =~ m{a\{2\}} ? 1 : 0;""", out='1\n1\n1\n'),
    c('T542', 'TRAPS; PLAN 19', r"""say "aa" =~ /a{ 2 }/ ? 1 : 0; say "aaa" =~ /^a{,3}$/ ? 1 : 0;""", out='1\n1\n'),
    c('T542-brace', 'TRAPS; PLAN 19', r"""say "a{" =~ /a{/ ? 1 : 0;""", out='1\n', err='Unescaped left brace in regex is passed through'),
    c('T543', 'TRAPS; PLAN 19', r"""my $s = "aXbX"; my $t = $s =~ /X/g; $t = $s =~ /X/g; my @l = ($s =~ /X/g); say scalar(@l);""", out='0\n'),
    c('T544', 'TRAPS; PLAN 19', r"""my @m = ("aab" =~ /a*/g); say join "|", @m; @m = ("ab" =~ /x*|a/g); say join "|", @m; @m = ("abc" =~ /x*/g); say scalar(@m);""", out='aa||\n|a||\n4\n'),
    c('T545', 'TRAPS; PLAN 19', r"""say "\xe9" =~ /\w/ ? 1 : 0, "\xa0" =~ /\s/ ? 1 : 0, "\x0b" =~ /\s/ ? 1 : 0, "\x85" =~ /\s/ ? 1 : 0, "\x{200b}" =~ /\s/ ? 1 : 0, "\x{2028}" =~ /\s/ ? 1 : 0;""", out='111101\n'),
    c('T546', 'TRAPS; PLAN 19', r"""say "\x{212A}" =~ /k/i ? 1 : 0, "\x{17F}" =~ /s/i ? 1 : 0, "\xdf" =~ /ss/i ? 1 : 0, "\x{FB01}" =~ /fi/i ? 1 : 0;""", out='1111\n'),
    c('T547', 'TRAPS; PLAN 19', r"""my $x = "a"; say !$x =~ /a/ ? 1 : 0;""", out='0\n', err='Possible precedence problem between ! and pattern match'),
    c('T547-array', 'TRAPS; PLAN 19', r"""my @a = (1); say @a =~ /1/ ? 1 : 0;""", out='1\n', err=r'Applying pattern match \(m//\) to @a will act on scalar\(@a\)'),
    c('T548', 'TRAPS; PLAN 19', r"""my @l = ("a" =~ /b/); say scalar(@l); @l = ("a" =~ /a/); say "@l"; @l = ("a" !~ /b/); say scalar(@l), "[@l]"; @l = ("a" !~ /a/); say scalar(@l), "[@l]"; @l = ("ab" =~ /(a)(x)?/); say scalar(@l), defined $l[1] ? "d" : "u";""", out='0\n1\n1[1]\n1[]\n2u\n'),
    c('T548-bool', 'TRAPS; PLAN 19', r"""use builtin 'is_bool'; no warnings 'experimental::builtin'; say is_bool("a" =~ /a/) ? 1 : 0, is_bool("a" =~ /b/) ? 1 : 0, is_bool("a" !~ /b/) ? 1 : 0;""", out='111\n'),
    c('T549', 'TRAPS; PLAN 19', r"""say "a\n" =~ /\n^/m ? 1 : 0, "a\nb" =~ /\n^/m ? 1 : 0, "a\n" =~ /a$/ ? 1 : 0, "a\n\n" =~ /a$/ ? 1 : 0, "a\n" =~ /a\Z/ ? 1 : 0, "a\n" =~ /a\z/ ? 1 : 0; my @l = ("a\n" =~ /$/g); say scalar(@l); @l = ("a\n\nb" =~ /^/mg); say scalar(@l);""", out='011010\n2\n3\n'),
    c('T550', 'TRAPS; PLAN 19', r"""say "a" =~ /a$|b/ ? 1 : 0, "a" =~ /(a$)/ ? 1 : 0, "a|" =~ /a$|b/ ? 1 : 0; my $n = 5; say "5" =~ /^$n$/ ? 1 : 0;""", out='110\n1\n'),
    c('T551', 'TRAPS; PLAN 19', r"""say "a" =~ /(a)\2/ ? 1 : 0;""", exit=255, err='Reference to nonexistent group'),
    c('T551-unset', 'TRAPS; PLAN 19', r"""say "b" =~ /(a)?\1b/ ? 1 : 0;""", out='0\n'),
    c('T552', 'TRAPS; PLAN 19', r"""say "" =~ /(?:\b)*/ ? 1 : 0;""", out='1\n', err='matches null string many times'),
    c('T553', 'TRAPS; PLAN 19', r"""my @l = ("b" =~ /(a*)?b/); say defined $l[0] ? "d[$l[0]]" : "u";""", out='d[]\n'),
    c('T554', 'TRAPS; PLAN 19', r"""if ("a" =~ /(a)/) { } "b" =~ /(x)/; say $1;""", out='a\n'),
    c('T555', 'TRAPS; PLAN 19', r"""my $s = ("a" x 60) . "b"; say $s =~ /^(?:a|aa)*$/ ? 1 : 0;""", out='0\n'),
    c('T66', 'TRAPS; PLAN 19', r""""abc" =~ /b/; say "xbx" =~ // ? "y" : "n";""", out='y\n'),
    c('T67', 'TRAPS; PLAN 19', "use utf8;\nuse open ':std', ':encoding(UTF-8)';\nsay \"\u0663\" =~ /^\\d$/ ? 'digit' : 'no'; say \"a\\n\" =~ /a$/ ? 'match' : 'no'; say \"\u2163\" =~ /\\w/ ? 1 : 0, \"\u2163\" =~ /\\d/ ? 1 : 0;", out='digit\nmatch\n10\n'),
    # ---- the rest the proposal stands on
    c('19-nested', 'PLAN 19', r"""say "a" =~ /a**/ ? 1 : 0;""", exit=255, err='Nested quantifiers'),
    c('19-backwards', 'PLAN 19', r"""say "a" =~ /a{2,1}/ ? 1 : 0;""", out='0\n', err=r"Quantifier \{n,m\} with n > m can't match"),
    c('19-range', 'PLAN 19', r"""say "a" =~ /[z-a]/ ? 1 : 0;""", exit=255, err=r'Invalid \[\] range'),
    c('19-false-range', 'PLAN 19', r"""say "a" =~ /[a-\d]/ ? 1 : 0;""", out='1\n', err=r'False \[\] range'),
    c('19-unknown-escape', 'PLAN 19', r"""say "ab" =~ /a\yb/ ? 1 : 0;""", out='0\n', err=r'Unrecognized escape \\y passed through'),
    c('19-possessive', 'PLAN 19', r"""say "aa" =~ /a{2}+/ ? 1 : 0, "aa" =~ /a++/ ? 1 : 0;""", out='11\n'),
    c('19-x', 'PLAN 19', "my @l = (\"ab cd\" =~ /(\\w+) # word\n  \\s (\\w+)/x); say \"@l\"; say \"a b\" =~ /a\\ b/x ? 1 : 0, \"aa\" =~ /a +/x ? 1 : 0, \"a#b\" =~ /a\\#b/x ? 1 : 0;", out='ab cd\n111\n'),
    c('19-close-bracket-first', 'PLAN 19', r"""say "]" =~ /[]a]/ ? 1 : 0, "-" =~ /[a-]/ ? 1 : 0;""", out='11\n'),
    c('19-not-g', 'PLAN 19', r"""say "a" !~ /a/g ? 1 : 0;""", out='0\n'),
    c('19-copies', 'PLAN 19', r"""my $x = "a"; my @l = ($x =~ /(a)/, $x = "b"); say "@l";""", out='a b\n'),
    c('19-list-g-groups', 'PLAN 19', r"""my @l = ("ab" =~ /(a)|(b)/g); say join ",", map { $_ // "u" } @l;""", out='a,u,u,b\n'),
    c('19-quantified-group', 'PLAN 19', r"""my @l = ("aab" =~ /(a|b)*/); say "@l"; @l = ("aab" =~ /(a)*b/); say "@l"; @l = ("ac" =~ /(a|b)*c/); say "@l";""", out='b\na\na\n'),
    c('19-m-brackets', 'PLAN 19', r"""say "x" =~ m{x}, "x" =~ m(x), "x" =~ m[x], "x" =~ m<x>, "x" =~ m!x!, "aa" =~ m{a{2}};""", out='111111\n'),
    c('19-dot', 'PLAN 19', "use utf8;\nsay \"a\\x{301}\" =~ /^.$/ ? 1 : 0, \"\\n\" =~ /./ ? 1 : 0, \"\\n\" =~ /./s ? 1 : 0;", out='001\n'),
]
