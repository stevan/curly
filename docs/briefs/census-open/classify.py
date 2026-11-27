#!/usr/bin/env python3
"""The census's open refusals and its LOUD probes, read (2026-11-27).

    python3 docs/briefs/census-open/classify.py [census.json]      # the causes, counted, three examples each
    git show 41a9025:t/census/census.json > /tmp/before.json
    python3 docs/briefs/census-open/classify.py /tmp/before.json   # the 822 as they were read
    python3 docs/briefs/census-open/classify.py --list CAUSE       # every probe of one cause

Each open REFUSED probe of t/census/census.json is given a cause by the
compiler's message and the text at the place it names (`before`, the line
up to the place; `after`, from it on). The first cause that matches. A
cause's verdict: `a` decided (a decision refuses it: the census's reason
table now says so), `b` waits for a step, `c` stricter than it has to be,
`d` undecided. README.md beside this file is written from its output.
Run from the repository's root. A probe no cause takes is printed as
UNREAD, and there are none: the reading is total.
"""

import collections
import json
import os
import re
import sys

# (cause, verdict, ref, message, before, after, what)
CAUSES = [
    # ---- (a) decided
    ('bare-shift', 'a', 'D17', r"^(shift|pop) names an array, found '(;|\}|\)|//|,)'", None, None,
     "`shift` or `pop` with no array: perl's `@_` in a sub (`my $self = shift;`), `@ARGV` outside one"),
    ('at-underscore', 'a', 'D17', r"^@_ is not declared", None, None, "`$#_`: perl's `@_`"),
    ('eval-error', 'a', 'D20', r"^after '\$' comes a name", None, r"^\$@", "`$@`, the error of a block `eval`"),
    ('package-var', 'a', 'D19', r"^after '[$@%]' comes a name|^expected '[;)]', found ':'$", None, r"^[$@%]::|^::|^:", "`$::x`, `$main::x`, `%::h`: package variables"),
    ('punct-global', 'a', 'D22', r"^after '\$' comes a name", None, r'^\$[,"/\\]', "`$,`, `$\"`, `$/`, `$\\`: the punctuation variables that set global behaviour"),
    ('last-index-store', 'c', 'D80', r"^the left side of '=' is a variable, an element", r"\$#\w+\s*$", None, "`$#a = N`: D80 left it 'until its step', and no step has it"),
    ('lvalue-expr', 'a', 'D56', r"^the left side of '[^']+' is a variable, an element", None, None, "an assignment to what is not a variable: `($x = 5) += 2`, `($c ? $p : $q) = 7`, `substr(...) = `"),
    ('step-expr', 'a', 'D56', r"^expected ';', found '(\+\+|--)'$|^'\+\+' is for a variable", None, None, "`++` or `--` on what is not a variable: `($x = 5)++`, `++($c ? $p : $q)`"),
    ('list-assign-value', 'a', 'D78', r"^scalar names an array, found '(\(|my)'|^expected '\)', found '='$", None, None, "`scalar(($x, $y) = ...)`, `scalar(@a = sort ...)`: a list assignment as a value"),
    ('array-target', 'a', 'D80', r"^an array among the targets takes every value that is left|^a comma after an assignment's right side", None, None, "an array that is not the last target, `(@a, @b) = ...`; a comma after an assignment's right side"),
    ('slice-target', 'a', 'D100', r"^a target of a list assignment is a variable", None, None, "a slice among other targets, `($a[0], @a[1,2]) = ...`"),
    ('kv-slice', 'a', 'D104', r"is a slice of (keys|indexes) and values", None, None, "`%h{...}`, `%a[...]`, slices of keys and values"),
    ('one-key-slice', 'a', 'D104', r"with one key: perl warns", None, None, "`@h{\"c\"}`, a slice by one key"),
    ('map-brackets', 'a', 'D87', r"^(map|grep) takes no brackets of its own", None, None, "`map(...)`, `grep(...)`"),
    ('sort-word', 'a', 'D87', r"first after sort: perl takes a (word|scalar) there", None, None, "`sort by_num LIST`, `sort $by LIST`"),
    ('no-warnings', 'a', 'D16', r"^'no warnings' is written", None, None, "`no warnings;`"),
    ('phase-block', 'a', 'D20', r"^'(INIT|CHECK|UNITCHECK)' is not in the language$", None, None, "`INIT { }`, `CHECK { }`"),
    ('pod-data', 'a', 'D20', r"^expected a value, found '<'$", None, r"^<DATA>", "`<DATA>`: `__DATA__` is refused"),
    ('implicit-it', 'a', 'D85', r"^(length|lc|uc|ucfirst|lcfirst|ord|chr|defined) needs an argument$", None, None, "a builtin with no argument, meaning `$_`"),
    ('implicit-it', 'a', 'D85', r"^expected a value, found '(;|\}|for|\])'$", r"(\bprint|\buc|\blength)\s*$", None, "a builtin with no argument, meaning `$_`"),
    ('minus-letter', 'a', 'D21', r"a minus hard against one letter is a file test", None, None, "`-e`, `-s`, `n()-n()`, `a-c`: a minus hard against one letter (T135)"),
    ('word-op-statement', 'a', 'D56', r"^'(or|and)' after a statement joins it", None, None, "two statements joined by a word operator"),
    ('reversed-op', 'a', 'D56', r"^'=-' with a blank after it", None, None, "`$x=- -$i`, `=-` and a blank (T127)"),
    ('my-modifier', 'a', 'D56', r"^my under a modifier", None, None, "`my` under a statement modifier"),
    ('print-brackets', 'a', 'D21', r"after print \(\.\.\.\): perl takes the brackets", None, None, "`print (1+2)*3` (T25)"),
    ('printf-value', 'a', 'D21', r"^printf is a statement, and has no value", None, None, "`printf` as a value"),
    ('sub-in-block', 'a', 'D72', r"^a sub stands at the top level", None, None, "a named sub in a block"),
    ('sub-attribute', 'a', 'D165', r"^after sub \S+ comes its signature", None, None, "`sub slot :lvalue`, `sub T::DESTROY`: an attribute, a package's sub"),
    ('return-list', 'a', 'D18', r"^a list after return is in brackets", None, None, "`return $a, $b;`"),
    ('label', 'a', 'D61', r"^a label is on a loop", None, None, "a label on what is not a loop (with `goto`)"),
    ('map-block', 'a', 'D85', r"^map's block ends in an expression|^last out of the block of a map|^'\{' first in map's block", None, None, "a `map` block that ends in a loop, holds `last`, or begins with `{`"),
    ('splice-brackets', 'a', 'D80', r"^splice needs brackets", None, None, "`splice @a, ...` without brackets"),
    ('typeglob', 'a', 'D4', r"^expected a value, found '\*'$", None, None, "`*f = sub { }`: typeglobs (D4, the subset without them)"),
    ('prototype', 'a', 'D21', r"^expected a value, found 'prototype'$|^after '\$' comes a name", None, r"^prototype|^\$\)", "`prototype \\&f`, `:prototype($)`"),
    ('vstring', 'a', 'D38', r"^expected a value, found v\d", None, None, "a v-string, `v65.66.67` (T62)"),
    ('lock-select', 'a', 'D22', r"^'(lock|select)' is not in the language$", None, None, "`lock`, `select`"),
    ('format', 'a', 'D22', r"^after '@' comes a name", None, r"^@[<>|]", "a format picture line"),
    ('undef-range', 'a', 'D15', r"^undef before '\.\.'", None, None, "`undef..2` under `no warnings`"),
    # ---- (b) later, by the step
    ('env-argv', 'b', '21', r"^(%ENV|@ARGV) is not declared", None, None, "`$ENV{X}`, `@ARGV`: the environment and the command line"),
    ('open', 'b', '21', r"^'open' is not in the language$", None, None, "`open(my $fh, '<', \\$s)`: in-memory files"),
    ('glob', 'b', '21', r"^expected a value, found '(glob|<)'$", None, None, "`glob`, `<*.x>`"),
    ('process-var', 'b', '21', r"^after '\$' comes a name", None, r"^\$[|0$]|^\$\^[OX]", "`$|`, `$0`, `$$`, `$^O`, `$^X`"),
    ('match-var', 'b', '19', r"^after '\$' comes a name", None, r"^\$\d", "`$1`: a capture"),
    ('regex', 'b', '19', r"^'(\^|\^\.|\||!~)' is not in the language yet|^expected a value, found '(/|qr)'$", r"(s/|qr/|split\s*/|/\s*$|split\(/|=~|!~|\bqr$)|^\s*my \$\w+ = \$s\s*$|qr\([^)]*$|split /[^/]*$", None, "a regex: `s/^\\s+//`, `qr/^a/`, `split /,|;/`, `!~`"),
    ('regex', 'b', '19', r"^'!~' is not in the language yet|^expected a value, found '(/|qr)'$", None, None, "a regex: `s/^\\s+//`, `qr/^a/`, `split /,|;/`, `!~`"),
    ('bitwise', 'b', '22', r"^'(\^|\||&|~|<<|>>)=?' is not in the language yet|^'<<=' is not|^'>>=' is not", None, None, "the bitwise operators and their assignments"),
    ('numeric-fn', 'b', '22', r"^expected a value, found '(hex|log|oct|exp)'$|^after '%' comes a name", None, None, "`hex`, `log`; `time % 1`"),
    ('substr4', 'b', '16d', r"^substr takes 2 to 3 arguments, and here are 4", None, None, "`substr` of four arguments (D120)"),
    ('scalar-reverse', 'b', '16d', r"^scalar names an array, found 'reverse'", None, None, "`scalar(reverse(...))`, a string reversed (D120)"),
    ('scalar-reverse', 'b', '16d', r"^scalar needs brackets", None, r"^scalar\s+reverse", "`scalar reverse ...`, a string reversed (D120)"),
    ('pod', 'b', '16d', r"^expected a value, found '='$|^q\{\.\.\.\} that never ends", None, None, "POD (D120)"),
    ('bytes', 'b', 'bytes', r"^expected a value, found '(pack|unpack)'$", None, None, "`pack`, `unpack`: with bytes (SURFACE)"),
    ('processes', 'b', 'library', r"^'`' is not in the language yet|^expected a value, found 'qx'$", None, None, "backticks, `qx`: processes, a library (SURFACE)"),
    ('state', 'b', 'D160', r"^'state' is not in the language$", None, None, "`state` (D160: proposed when something wants it)"),
    # ---- (c) and (d): what nobody has decided
    ('scalar-bare', 'c', '', r"^scalar needs brackets", None, None, "`scalar @a`, `scalar @{ $r }` without brackets"),
    ('do-block', 'c', '', r"^expected a value, found 'do'$", None, None, "`do { ... }` as a value"),
    ('do-while', 'c', '', r"^'do' is not in the language$", None, None, "`do { ... } while COND;`, `until`, a `do` as a statement"),
    ('undef-var', 'c', '', r"^undef before '[$%@]|^expected ';', found '@\w+'$", None, None, "`undef $x;`, `undef @a;`, `undef %h;`"),
    ('array-exists', 'd', 'D80', r"^(exists|delete) takes an element of a hash, found '\$a'", None, None, "`exists $a[i]`, `delete $a[i]`: D80 left them 'until their step', and no step has them"),
]
CAUSES = [(c, v, r, re.compile(m), re.compile(b) if b else None, re.compile(a) if a else None, w) for c, v, r, m, b, a, w in CAUSES]

def cause(name, p):
    line, col = map(int, p['at'].split(':'))
    # A probe the reading moved to by-design/ is read there.
    where = f't/census/run/{name}' if os.path.exists(f't/census/run/{name}') else f't/census/by-design/{name}'
    text = open(where, encoding='utf-8', errors='replace').read().split('\n')[line - 1]
    before, after = text[:col - 1], text[col - 1:]
    for c, v, r, m, b, a, w in CAUSES:
        if m.search(p['why']) and (b is None or b.search(before)) and (a is None or a.search(after)):
            return c, text, col
    return 'UNREAD', text, col

def main(argv):
    path = next((a for a in argv if not a.startswith('--') and a.endswith('.json')), 't/census/census.json')
    probes = json.load(open(path, encoding='utf-8'))['probes']
    opened = {n: p for n, p in probes.items() if p['verdict'] == 'REFUSED' and p['reason'] == 'open'}
    found = collections.defaultdict(list)
    for n, p in opened.items():
        c, text, col = cause(n, p)
        found[c].append((n, p, text, col))
    if '--list' in argv:
        want = argv[argv.index('--list') + 1]
        for n, p, text, col in found[want]:
            print(f'{n} {p["at"]}: {p["why"]}\n    {text.strip()[:200]}')
        return
    meta = {c: (v, r, w) for c, v, r, m, b, a, w in CAUSES}
    print(f'{len(opened)} open refusals')
    for c, rows in sorted(found.items(), key=lambda kv: (meta.get(kv[0], ('z',))[0], -len(kv[1]))):
        v, r, w = meta.get(c, ('?', '', 'no cause takes it'))
        print(f'\n[{v}] {c} {r}: {len(rows)}: {w}')
        for n, p, text, col in rows[:3]:
            print(f'    {n} {p["at"]}: {p["why"][:100]}')
            print(f'        {text.strip()[:160]}')

if __name__ == '__main__':
    main(sys.argv[1:])
