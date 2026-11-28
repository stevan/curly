"""D261: a die or warn over several lines, by its last argument: every
shape that might be judged to end in a newline, run where it does and does
not."""

LASTS = [
    '"a\\n"', '"a\\n" . ""', '"" . "a\\n"', '"a" . "\\n"', '"a\\n" . "b"', '"a" . "b"', '"a" . "\\n" . ""', '("a" . "\\n")', '("a\\n")', '+"a\\n"', '"a\\n" x 1', '"a\\n" x $n', '"a" . "\\n" x $n', '("a" . "\\n") x $n',
    '"a" . $e', '"a" . $nl', '"a\\n" . $e', '"a$nl"', '"a$e\\n"', '"a\\n$e"', '"a\\n${e}"', '"a\\n@em"', '"a@em\\n"', '"a\\n$em[0]"', '"a\\n$hh{k}"', '"a$hh{k}\\n"', '"a\\n" . "$e"', '"a" . "$e\\n"', '"$e" . "\\n"',
    'sprintf("%s\\n", "a")', 'sprintf("%s\\n", $e)', 'sprintf("\\n%s", $e)', 'sprintf("a\\n")', 'sprintf("%s", "a\\n")', 'sprintf("%s\\n%s", "a", $e)', 'sprintf("%s\\n%%", "a")', 'sprintf("%%\\n")', 'sprintf("%s%c", "a", 10)',
    'sprintf("a\\n") . ""', '"" . sprintf("a\\n")', 'sprintf("a\\n") . $e', '"a" . sprintf("%s\\n", $e)', 'sprintf("%s" . "\\n", "a")', 'sprintf("%5s\\n", "a")', 'sprintf("%-5s\\n", "a")', 'sprintf("%s\\n", "")', 'sprintf("%.0s\\n", "a")', 'sprintf("%*s\\n", 0, "")',
    'join("", "a", "\\n")', 'join("\\n", "a", "")', 'join("\\n", "a")', 'uc("a\\n")', 'lc "a\\n"', 'ucfirst("\\n")', 'quotemeta("a\\n")', 'substr("a\\nb", 0, 2)', 'scalar reverse("\\na")', 'chr(10)',
    '$c ? "a\\n" : "b\\n"', '$c ? "a\\n" : "b"', '($c ? "a" : "b") . "\\n"', '$e || "a\\n"', '$e // "a\\n"', '$nl && "a\\n"', '"a\\n" || $e', '"a\\n" // $e',
    "'a\\n'", "'a\n'", '"a\n"', 'q(a\\n)', 'qq(a\\n)', 'qq{a\\n}', 'qq(a\\n) . q()', "q(a\n)", '"a\\x0a"', '"a\\x{a}"', '"a\\012"', '"a\\o{12}"', '"a\\N{U+A}"', '"a\\cJ"', '"a\\x0A" . ""', '"a\\r"', '"a\\n\\r"', '"a\\n "', '"a\\n\\n"', '"\\n"', '""',
    '"\\Ua\\n"', '"\\Ua\\E\\n"', '"\\Ua\\n\\E"', '"\\Qa\\n"', '"\\Q\\n\\E"', '"a\\n\\E"', '"\\La\\n"', '"\\u\\n"', '"\\l\\n"', '"a\\n\\U"', '"a\\n\\Q\\E"', '"\\Qa\\E" . "\\n"', '"\\Q$e\\E\\n"', '"\\Q$e\\n"', '"\\U$e\\n"', '"\\n\\U$e"', '"\\n\\Q$e"', '"a\\n\\Q$e\\E"',
    '"a" . "\\Q\\n"', '"a" . "\\Q\\n\\E"', '"a" . "\\U\\n"',
    '$nl', '$e', '@em', '@nls', '$hh{nl}', '$nls[0]', 'f()', 'fn()', '"a" . fn()', 'fn() . ""', '__LINE__', '__LINE__ . "\\n"', '__FILE__ . "\\n"', '"a\\n" . __LINE__', 'true', '5', '5 . "\\n"', '"\\n" . 5', '$obj',
]

PRE = 'my $e = ""; my $nl = "\\n"; my $n = 1; my $c = 1; my @em = (); my @nls = ("x\\n"); my %hh = (k => "", nl => "\\n"); my $obj = "o";\nsub f() { return "f"; } sub fn() { return "f\\n"; }\n'

FORMS = [
    ('d1', 'die "x",\n  %s;\n'),
    ('d2', 'die\n  %s;\n'),
    ('d3', 'die(%s\n);\n'),
    ('d4', 'die %s\n  if $c;\n'),
    ('d5', '$e or\n  die %s;\n'),
    ('w1', 'warn "x",\n  %s;\nsay "after";\n'),
    ('d6', 'my $k = 0;\nwhile ($k++ < 1) {\n  die %s }\n'),
    ('d7', 'my $k = 0;\nuntil (0) { last if $k++; say "in"; }\ndo { $k++; } until (\n  $k > 2 and warn %s);\nsay $k;\n'),
    ('d8', 'my $k = 0;\nwhile ($k++ < 1 or warn %s) { say "body"; last if $k > 2; }\n'),
    ('d9', 'my $k = 0;\nif ($k) { say "no"; }\nelsif (not $k and warn %s) { say "elsif"; }\n'),
    ('da', 'my $k = 0;\nfor ($k = 0; $k < 1 or warn %s; $k++) { say "body"; last if $k > 1; }\n'),
    ('db', 'my $k = 0;\nfor ($k = 0; $k < 2; $k++, warn %s) { say "body"; }\n'),
    ('dc', 'for my $q (1 .. 2) { say "b" }\ncontinue_not_in();\nsub continue_not_in() { warn "x", %s\n  ; return; }\n'),
    ('dd', 'my @l = map { warn "m",\n %s; $_ } 1;\n'),
    ('de', 'my $h = { a =>\n  1 };\ndie "x", %s if $h->{a} ==\n  1;\n'),
    ('df', 'sub g($p = die("x", %s)) {\n  return 1; }\ng(\n);\n'),
    ('dg', 'try { die "x",\n %s; } catch ($err) { print "c:", $err; }\n'),
    ('dh', 'my $k = 0;\n$k++ while ($k < 2 or\n  warn "x", %s);\n'),
]


def cases():
    for n, last in enumerate(LASTS):
        for tag, form in FORMS:
            # every last under the plain forms; the loops and tests by turns
            if tag not in ('d1', 'd2', 'w1', 'd5') and (n + len(tag) + ord(tag[1])) % 4:
                continue
            yield ('%03d%s' % (n, tag), PRE + form % last)
