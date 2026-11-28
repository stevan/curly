#!/usr/bin/env python3
"""The independent review of step 19 (matching): a differential generator
with a wide grammar, written by a reader who did not write the step.

Each pattern is drawn from a grammar that covers the subset and goes well
past it: classes with ranges, negation, escapes, `]`, `-` and `^` at every
position and POSIX-looking text; `\\d \\w \\s` and their opposites inside
and outside classes; every anchor, with and without /m and /s;
quantifiers greedy and lazy, on groups and backreferences, with large and
zero counts, and braces that are no quantifier; alternation with empty
branches; backreferences to groups closed, open, in another branch and
missing; /x with blanks and comments; every delimiter the language takes;
every escape perl has; `$` and `@` everywhere. Subjects are sampled from
the pattern itself and then spoiled, and drawn at random, over ASCII and
Unicode, with newlines.

Three steps:

1. Every pattern is put in a small program and read by the compiler's
   whole front end (`classify.ts`) and by perl (`classify.pl`). A pattern
   the compiler takes and perl warns of or dies at is a finding at once.
2. The patterns both take in silence are run in programs of a few hundred
   each, under perl and compiled: for every subject the match where a list
   is wanted (each capture's characters as numbers, undef told from the
   empty string), where one value is, and with `!~`; the two outputs must
   be the same. A fault of the compiled program names its pattern, which
   is counted and taken out, and the program is run again.
3. The refusals are counted by their message, with how many of them perl
   takes in silence.

    python3 docs/briefs/step19-review/differential.py [COUNT] [SEED] [MODE]

MODE is `wide` (the default), `unicode` (the `\\d \\w \\s \\b` boundaries
over Unicode subjects) `fold` (/i over ASCII subjects, patterns of letters in both cases) or
`counts` (counts inside repeated groups, after something of any length).
`outputs-differential.txt` beside this file is what the runs recorded in
README.md printed.
"""

import bisect
import json
import os
import random
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
PERL = os.environ.get('CURLY_PERL', 'perl')
PRELUDE = '''use v5.42;
use utf8;
use open ':std', ':encoding(UTF-8)';
sub enc(@l) {
    my $o = scalar(@l) . ":";
    for my $x (@l) {
        if (defined $x) {
            $o .= "<";
            for (my $i = 0; $i < length($x); $i++) { $o .= ord(substr($x, $i, 1)) . "."; }
            $o .= ">";
        } else { $o .= "u"; }
    }
    return $o;
}
'''
PRELUDE_LINES = PRELUDE.count('\n')

# Characters a subject is spoiled with, and random subjects are made of.
NOISE = list('aabcABxk019_ -.,\n\n\t') + ['é', '٣', ' ', '\U0001F600', 'K', 'ß', ' ', '\x0b', 'Ā', 'ʰ', '̀', 'Ⅰ']
ASCII_NOISE = [c for c in NOISE if ord(c) < 128]

W_CHARS = list('abcABxk019_') + ['é', '٣', 'Ā', 'K', 'ß', 'ʰ', '̀', 'Ⅰ', 'ª', 'µ', '‿']
D_CHARS = list('0123456789') + ['٣', '१', '１', '\U0001d7d8']
S_CHARS = [' ', '\t', '\n', '\r', '\f', '\x0b', '\u0085', ' ', ' ', ' ', ' ', ' ', ' ', '　']
NOT_W = [' ', '-', '.', '\n', ' ', '×', '÷', ' ', '\U0001F600', '²', '①']


class Gen:
    def __init__(self, r, mode):
        self.r = r
        self.mode = mode

    # Each piece is (source, sampler, nullable, hascap); a sampler takes
    # the captures sampled so far and gives a string the piece may match.
    def literal(self, wild):
        r = self.r
        plain = list('abcABx019_k') + [' ', '-', ':', '=', ',', '!', '~', '"', "'", '<', '>', '&', '%', ';', '`']
        wide = ['é', 'ß', '٣', '\U0001F600', 'K', 'ſ', ' ', 'Ā']
        esc = [('\\.', '.'), ('\\\\', '\\'), ('\\/', '/'), ('\\|', '|'), ('\\(', '('), ('\\)', ')'), ('\\[', '['), ('\\]', ']'),
               ('\\{', '{'), ('\\}', '}'), ('\\*', '*'), ('\\+', '+'), ('\\?', '?'), ('\\^', '^'), ('\\$', '$'), ('\\@', '@'),
               ('\\#', '#'), ('\\ ', ' '), ('\\-', '-'), ('\\n', '\n'), ('\\t', '\t'), ('\\r', '\r'), ('\\f', '\f'), ('\\e', '\x1b'),
               ('\\a', '\x07'), ('\\x41', 'A'), ('\\x{e9}', 'é'), ('\\x{1F600}', '\U0001F600'), ('\\N{U+E9}', 'é'),
               ('\\o{101}', 'A'), ('\\x0a', '\n'), ('\\x{0}', '\x00'), ('\\_', '_'), ('\\<', '<'), ('\\>', '>'), ('\\=', '='),
               ('\\:', ':'), ('\\,', ','), ('\\!', '!'), ('\\~', '~'), ('\\"', '"'), ("\\'", "'"), ('\\&', '&'), ('\\%', '%'),
               ('\\;', ';'), ('\\`', '`'), ('\\x7f', '\x7f'), ('\\x{2028}', ' '), ('\\x{a0}', ' ')]
        odd = [('\\0', '\x00'), ('\\01', '\x01'), ('\\10', '\x08'), ('\\12', '\n'), ('\\012', '\n'), ('\\cA', '\x01'), ('\\Qa.\\E', 'a.'),
               ('\\E', ''), ('\\Ua', 'A'), ('\\la', 'a'), ('\\h', ' '), ('\\v', '\n'), ('\\R', '\n'), ('\\K', ''), ('\\G', ''),
               ('\\X', 'a'), ('\\N', 'a'), ('\\pL', 'a'), ('\\p{L}', 'a'), ('\\P{L}', '1'), ('\\g1', 'a'), ('\\g{1}', 'a'),
               ('\\g{-1}', 'a'), ('\\k<a>', 'a'), ('\\y', 'y'), ('\\i', 'i'), ('\\x', '\x00'), ('\\xg', 'g'), ('\\x{}', '\x00'),
               ('\\x4 ', '\x04 '), ('\\x4g', '\x04g'), ('\\x4-', '\x04-'), ('\\o{}', ''), ('\\o{8}', '8'), ('\\N{U+}', ''),
               ('\\N{LATIN SMALL LETTER A}', 'a'), ('\\x{110000}', 'a'), ('\\x{D800}', 'a'), ('\\x{ 41 }', 'A'), ('\\o{ 101 }', 'A'),
               ('$', ''), ('@', '@'), ('{', '{'), ('}', '}'), ('#', '#'), ('/', '/'), (']', ']'), ('$a', ''), ('@a', ''),
               ('$)', ''), ('$|', ''), ('$ ', ' '), ('$1', ''), ('@-', '@-'), ('$&', ''), ('\\b{wb}', ''), ('\\N{2}', 'aa'),
               ('\\z', ''), ('(?#c)', ''), ('(?i)', ''), ('(?i:a)', 'a'), ('(?=a)', ''), ('(?!a)', ''), ('(?<=a)', ''), ('(?>a)', 'a'),
               ('(?<n>a)', 'a'), ('(?|a)', 'a'), ('(?^:a)', 'a'), ('\u0085', '\u0085'), (' ', ' '), ('\\8', '8'), ('\\9', '9'),
               ('\\1', 'a'), ('\\2', 'a'), ('\\\n', '\n'), ('\\\t', '\t'), ('\\é', 'é')]
        k = r.random()
        if wild and k < 0.15:
            s, c = r.choice(odd)
        elif k < 0.55:
            c = r.choice(plain)
            s = c
        elif k < 0.65:
            c = r.choice(wide)
            s = c
        else:
            s, c = r.choice(esc)
        return (s, lambda env, c=c: c, c == '', False)

    def klass(self, wild):
        r = self.r
        items = []       # (source, candidates)
        simple = [(c, [c]) for c in 'abcABx019_k'] + [(c, [c]) for c in '.*+?()|{}# :=,!<>&%;"\'/'] + [('é', ['é']), ('\U0001F600', ['\U0001F600']), ('٣', ['٣'])]
        escs = [('\\]', [']']), ('\\-', ['-']), ('\\^', ['^']), ('\\\\', ['\\']), ('\\[', ['[']), ('\\n', ['\n']), ('\\t', ['\t']),
                ('\\x41', ['A']), ('\\x{e9}', ['é']), ('\\.', ['.']), ('\\$', ['$']), ('\\@', ['@']), ('\\/', ['/']), ('\\ ', [' ']),
                ('\\#', ['#']), ('\\N{U+41}', ['A']), ('\\o{101}', ['A']), ('\\e', ['\x1b'])]
        classes = [('\\d', D_CHARS), ('\\w', W_CHARS), ('\\s', S_CHARS), ('\\D', NOT_W + ['a']), ('\\W', NOT_W), ('\\S', W_CHARS + ['-'])]
        ranges = [('a-c', list('abc')), ('0-9', list('0123456789')), ('A-Z', list('ABXZ')), ('a-z', list('abxkz')), ('à-ÿ', ['é', 'ß', '÷']),
                  ('\\x00-\\x7f', list('a \n~')), ('\\x{100}-\\x{17f}', ['Ā', 'ſ']), ('!-/', list('!-./')), ('+--', list('+,-')),
                  ('\\x{0}-\\x{10FFFF}', ['a', '\U0001F600']), ('a-a', ['a']), ('\\t-\\r', ['\t', '\n', '\r', '\x0b']), (' -~', list(' a~')),
                  ('\\--0', ['-', '.', '/', '0']), ('*-\\-', ['*', '+', ',', '-'])]
        odd = [('c-a', ['a']), ('a-\\d', ['a', '-', '1']), ('\\d-a', ['a', '-', '1']), ('\\w-z', ['a', '-']), ('--/', ['-', '.', '/']), ('[:alpha:]', ['a']),
               ('[:^digit:]', ['a']), (':alpha:', [':', 'a']), ('[', ['[']), ('$', ['$']), ('@', ['@']), ('\\b', ['\x08']), ('\\1', ['\x01']),
               ('\\0', ['\x00']), ('\\012', ['\n']), ('\\N', ['a']), ('\\pL', ['a']), ('\\h', [' ']), ('\\y', ['y']), ('\\cA', ['\x01']),
               ('[=a=]', ['a']), ('[.a.]', ['a']), ('a-\\x{e9}', ['a', 'é', 'z']), ('\\B', ['B']), ('\\z', ['z']), ('\\Qa', ['a']),
               ('$a', ['a']), ('\\x', ['\x00']), ('-', ['-']), ('^', ['^']), ('a--', ['a']), ('\\E', []), ('\\c]', [])]
        n = r.randint(1, 4)
        for _ in range(n):
            k = r.random()
            pool = odd if wild and k < 0.2 else simple if k < 0.5 else escs if k < 0.62 else classes if k < 0.8 else ranges
            items.append(r.choice(pool))
        neg = r.random() < 0.3
        head = []
        tail = []
        k = r.random()
        if k < 0.08:
            head.append(('-', ['-']))
        elif k < 0.11 and wild:
            head.append((']', [']']))
        elif k < 0.13 and wild:
            head.append(('^' if neg else '\\^', ['^']))
        elif k < 0.15 and wild:
            head.append(('--', ['-']))
        k = r.random()
        if k < 0.08:
            tail.append(('-', ['-']))
        elif k < 0.12:
            tail.append(('^', ['^']))
        items = head + items + tail
        src = '[' + ('^' if neg else '') + ''.join(s for s, _ in items) + ']'
        cands = [c for _, cs in items for c in cs]

        def sample(env):
            if neg or not cands:
                return r.choice(NOISE)
            return r.choice(cands)
        return (src, sample, False, False)

    def escape_class(self):
        r = self.r
        s, cs = r.choice([('\\d', D_CHARS), ('\\w', W_CHARS), ('\\s', S_CHARS), ('\\D', NOT_W + ['a']), ('\\W', NOT_W), ('\\S', W_CHARS + ['-'])])
        return (s, lambda env: r.choice(cs), False, False)

    def glue(self):
        """What may stand between two pieces under /x."""
        r = self.r
        if not self.x:
            return ''
        k = r.random()
        if k < 0.6:
            return ''
        if k < 0.8:
            return r.choice([' ', '  ', '\t', '\n', ' \n '])
        if k < 0.9:
            return ' # ' + r.choice(['c', 'a comment', 'a* b+', '', '(', 'x|y', "it's", '$', 'a $ b', '\\', '[', 'a{2}', '?']) + '\n'
        return r.choice(['#\n', ' #c\n ', '\n\n'])

    def atom(self, depth, wild):
        r = self.r
        k = r.random()
        if self.mode == 'unicode':
            if k < 0.2:
                return self.literal(False)
            if k < 0.45:
                return self.escape_class()
            if k < 0.65:
                a = r.choice(['\\b', '\\B', '^', '$', '\\z', '\\Z', '\\A'])
                return (a, lambda env: '', True, False)
            if k < 0.8:
                return self.klass(False)
            if k < 0.85:
                return ('.', lambda env: r.choice(NOISE), False, False)
        elif self.mode == 'fold':
            if k < 0.5:
                c = r.choice(list('abkKsSAZaz') + ['ss', 'st', 'ff', 'fi', 'i', 'I', 'j'])
                return (c, lambda env, c=c: c.swapcase() if r.random() < 0.5 else c, False, False)
            if k < 0.7:
                return self.klass(False)
        else:
            if k < 0.34:
                return self.literal(wild)
            if k < 0.40:
                return ('.', lambda env: r.choice(NOISE), False, False)
            if k < 0.54:
                return self.klass(wild)
            if k < 0.64:
                return self.escape_class()
            if k < 0.73:
                a = r.choice(['^', '$', '\\b', '\\B', '\\A', '\\z', '\\Z', '^', '$'])
                return (a, lambda env: '', True, False)
        if k < 0.78 and (self.groups > 0 or wild):
            n = r.randint(1, max(1, min(self.groups + (1 if wild else 0), 9)))
            if not wild and n not in self.closed:
                n = r.choice(sorted(self.closed)) if self.closed else 1
            return (f'\\{n}', lambda env, n=n: env.get(n, ''), True, False)
        if depth <= 0:
            return self.literal(wild)
        cap = r.random() < 0.55
        n = 0
        if cap:
            self.groups += 1
            n = self.groups
        src, sample, nullable, hascap = self.alt(depth - 1, wild)
        if cap:
            self.closed.add(n)

            def cap_sample(env, n=n, sample=sample):
                s = sample(env)
                env[n] = s
                return s
            return ('(' + self.glue() + src + ')', cap_sample, nullable, True)
        return ('(?:' + src + ')', sample, nullable, hascap)

    QUANTS = [('*', 0, 3), ('+', 1, 3), ('?', 0, 1), ('{2}', 2, 2), ('{1}', 1, 1), ('{2,}', 2, 4), ('{0,}', 0, 2), ('{1,3}', 1, 3), ('{0,2}', 0, 2),
              ('{2,2}', 2, 2), ('{0}', 0, 0), ('{0,0}', 0, 0), ('{3}', 3, 3), ('{1,}', 1, 3), ('{0,1}', 0, 1), ('{2,5}', 2, 5)]
    ODD_QUANTS = [('{3,1}', 1, 1), ('{,2}', 0, 2), ('{ 2 }', 2, 2), ('{2, 3}', 2, 3), ('{', 1, 1), ('{a}', 1, 1), ('{2', 1, 1), ('{,}', 1, 1), ('{}', 1, 1),
                  ('{12}', 12, 12), ('{0,40}', 0, 5), ('{100}', 100, 100), ('{32766}', 3, 3), ('{32767}', 3, 3), ('{65536}', 1, 1), ('{2}{3}', 6, 6),
                  ('**', 0, 2), ('+*', 1, 2), ('?+', 0, 1), ('*+', 0, 2), ('++', 1, 2), ('{2}+', 2, 2), ('{1,2}+', 1, 2), ('{02}', 2, 2), ('{2,02}', 2, 2),
                  ('{-1}', 1, 1), ('{1,2,3}', 1, 1), ('{2}?', 2, 2), ('{0}?', 0, 0), ('{1,1}?', 1, 1)]

    def piece(self, depth, wild):
        r = self.r
        src, sample, nullable, hascap = self.atom(depth, wild)
        k = r.random()
        want = k < (0.4 if self.mode == 'wide' else 0.3)
        if want and not wild and (nullable or (hascap and not (src.startswith('(') and not src.startswith('(?') and src.count('(') - src.count('(?') - src.count('\\(') == 1))):
            # Mostly keep to what D231 takes.
            want = r.random() < 0.08
        if not want:
            return (src, sample, nullable, hascap)
        q, lo, hi = r.choice(self.ODD_QUANTS) if wild and r.random() < 0.25 else r.choice(self.QUANTS)
        lazy = '?' if r.random() < 0.3 and (wild or '{' not in q or ',' in q) and q not in ('{2,2}', '{0,0}') else ''
        g = self.glue() if r.random() < 0.3 else ''

        def rep_sample(env, sample=sample, lo=lo, hi=hi):
            # (Counts nest, and a subject is cut to sixty characters.)
            out = ''
            for _ in range(r.randint(lo, hi)):
                out += sample(env)
                if len(out) > 200:
                    break
            return out
        return (src + g + q + lazy, rep_sample, nullable or lo == 0, hascap)

    def seq(self, depth, wild):
        r = self.r
        n = r.choice([1, 1, 2, 2, 2, 3, 3, 4, 5]) if depth > 0 else r.choice([1, 1, 2, 3])
        if r.random() < (0.06 if wild else 0.02):
            n = 0
        pieces = [self.piece(depth, wild) for _ in range(n)]
        src = self.glue()
        for p in pieces:
            src += p[0] + self.glue()

        def sample(env):
            return ''.join(p[1](env) for p in pieces)
        return (src, sample, all(p[2] for p in pieces), any(p[3] for p in pieces))

    def alt(self, depth, wild):
        r = self.r
        n = r.choice([1, 1, 1, 1, 2, 2, 3])
        alts = [self.seq(depth, wild) for _ in range(n)]

        def sample(env):
            return r.choice(alts)[1](env)
        return ('|'.join(a[0] for a in alts), sample, any(a[2] for a in alts), any(a[3] for a in alts))

    def counts(self):
        """A pattern of the `counts` mode: something of any length, a
        separator, and a repeated group with counts inside it, over three
        letters. (It is the family perl 5.42 was found to answer wrongly
        in, T570: its optimiser asks for a string the match need not
        hold.)"""
        r = self.r

        # (No repeat without end inside another: perl and every other
        # backtracking matcher take for ever over those.)
        def unit(depth, top):
            k = r.random()
            c = r.choice('abx')
            if k < 0.4 or depth == 0:
                atom, text = r.choice([(c, c), (c, c), ('[' + c + ']', c), ('.', c), ('\\w', c), ('(?:' + c + ')', c)])
            else:
                parts = [unit(depth - 1, False) for _ in range(r.randint(1, 3))]
                atom, text = '(?:' + ''.join(p[0] for p in parts) + ')', ''.join(p[1] for p in parts)
            counted = [('', 1), ('', 1), ('{1}', 1), ('{2}', 2), ('{3}', 3), ('{1,2}', 2), ('{2,3}', 3), ('?', 1), ('{2,2}', 2), ('{2}', 2), ('{3}', 3)]
            endless = [('{2,}', 2), ('+', 2), ('*', 2), ('+?', 1), ('{1,}', 1), ('{3,}', 3)]
            q, times = r.choice(counted + (endless if top and '(?:' not in atom[3:] else []))
            return atom + q, text * times
        pre, pre_text = r.choice([('b+', 'bb'), ('b*', 'b'), ('\\w+', 'ab'), ('b?', 'b'), ('', ''), ('b', 'b'), ('.+', 'xb'), ('b+?', 'b'), ('(b+)', 'bb'), ('.*', ''), ('[ab]{1,}', 'ab'), ('^', ''), ('(?:ab)*', 'ab')])
        sep, sep_text = r.choice([('', ''), ('&', '&'), ('&', '&'), ('&&', '&&'), ('.', '&'), ('[&]', '&'), ('\\W', '&'), ('9', '9'), ('&?', '&')])
        parts = [unit(2, True) for _ in range(r.randint(1, 3))]
        body, text = ''.join(p[0] for p in parts), ''.join(p[1] for p in parts)
        post, post_text = r.choice([('', ''), ('', ''), ('9', '9'), ('$', ''), ('\\1', 'bb'), ('x+', 'x'), ('&', '&')])
        if post == '\\1' and not pre.startswith('('):
            post, post_text = '', ''
        written = '/' + pre + sep + body + post + '/' + r.choice(['', '', '', 'g', 's'])
        good = pre_text + sep_text + text + post_text
        subjects = [good, 'b' + good, good + good, good[:-1], good[1:], 'bb&' + text + text, ''.join(r.choice('abx&9') for _ in range(r.randint(1, 12))), good.replace('&', '&&', 1)]
        return written, subjects

    def pattern(self):
        """A pattern as it is written, with its delimiters and flags, and
        subjects for it."""
        r = self.r
        if self.mode == 'counts':
            return self.counts()
        wild = r.random() < 0.25 and self.mode == 'wide'
        flags = ''
        for f, p in (('i', 0.2), ('m', 0.3), ('s', 0.2), ('x', 0.15), ('g', 0.3)):
            if r.random() < p:
                flags += f
        if self.mode == 'fold' and 'i' not in flags:
            flags += 'i'
        if wild and r.random() < 0.08:
            flags += r.choice(['a', 'x', 'g', 'o', 'u', 'n', 'p', 'l', 'c', 'e', 'r', 'd', 'q', 'aa', 'i'])
        flags = ''.join(r.sample(flags, len(flags)))
        self.x = 'x' in flags
        self.groups = 0
        self.closed = set()
        src, sample, _, _ = self.alt(r.choice([1, 2, 2, 3]), wild)
        k = r.random()
        if k < 0.7:
            written = '/' + src + '/' + flags
        else:
            o, c = r.choice(['{}', '()', '[]', '<>'])
            written = 'm' + o + src + c + flags
        if wild and r.random() < 0.03:
            written = r.choice(['m/', 'm#', 'm,', 'm!', 'm|', "m'", 'm ', 'm"']) + src + r.choice(['/', '#', ',', '!', '|', "'", '"']) + flags
        # (Under /i a subject past ASCII is a fault, D230: `folds.py`
        # beside this file holds that to its edge.)
        ascii_only = 'i' in flags
        noise = ASCII_NOISE if ascii_only else NOISE
        subjects = []
        for _ in range(4):
            try:
                s = sample({})
            except RecursionError:
                s = ''
            subjects.append(s)
        for s in list(subjects[:3]):
            cs = list(s)
            for _ in range(r.randint(1, 2)):
                k = r.random()
                at = r.randint(0, len(cs))
                if k < 0.35 and cs:
                    del cs[min(at, len(cs) - 1)]
                elif k < 0.7:
                    cs.insert(at, r.choice(noise))
                elif k < 0.85:
                    cs.append('\n')
                else:
                    cs = cs + [r.choice(noise)] + cs
            subjects.append(''.join(cs))
        subjects.append(''.join(r.choice(noise) for _ in range(r.randint(0, 8))))
        if ascii_only:
            subjects = [''.join(c if ord(c) < 128 else 'k' for c in s) for s in subjects]
        subjects = [s[:60] for s in subjects]
        return written, subjects


def quoted(s):
    """A double-quoted string both perl and the compiler read alike."""
    return '"' + ''.join(c if (c.isascii() and c.isalnum()) or c == ' ' else '\\x{%x}' % ord(c) for c in s) + '"'


def probe(written):
    return f'use v5.42;\nuse utf8;\nmy $s = "";\nmy @l = $s =~ {written};\n'


def block(n, written, subjects, glob):
    text = f'for my $s ({", ".join(quoted(s) for s in subjects)}) {{\nmy @l = $s =~ {written};\nsay "{n} L ", enc(@l);\n'
    if not glob:
        text += f'say "{n} B ", $s =~ {written} ? 1 : 0;\nsay "{n} N ", $s !~ {written} ? 1 : 0;\n'
    return text + '}\n'


def classify(cmd, programs):
    out = subprocess.run(cmd, input=json.dumps(programs).encode(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=ROOT)
    if out.returncode != 0:
        sys.exit(f'{cmd}: {out.stderr.decode()}')
    return json.loads(out.stdout)


def run_batch(tmp, k, tests):
    """Runs one program of tests under perl and compiled. Gives back
    (same pairs, faults, differences, perl's own complaints)."""
    faults, diffs, complaints = [], [], []
    tests = list(tests)
    env = dict(os.environ, CURLY_RT_OBJ=os.path.join(tmp, 'rt.o'))
    for attempt in range(40):
        starts, text = [], PRELUDE
        for n, written, subjects, glob in tests:
            starts.append(text.count('\n') + 1)
            text += block(n, written, subjects, glob)
        path = os.path.join(tmp, f'b{k}.pl')
        with open(path, 'w') as f:
            f.write(text)
        try:
            p = subprocess.run([PERL, path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300)
        except subprocess.TimeoutExpired:
            return 0, faults, diffs, complaints + [('perl ran past five minutes', [t[1] for t in tests])]
        if p.returncode != 0 or p.stderr:
            # perl's own complaint as it runs: name the test, take it out.
            m = re.search(rb' line (\d+)', p.stderr)
            if m is None:
                return 0, faults, diffs, complaints + [(p.stderr.decode(errors='replace')[:300], [])]
            at = bisect.bisect_right(starts, int(m.group(1))) - 1
            complaints.append((p.stderr.decode(errors='replace').splitlines()[0], tests[at][1]))
            del tests[at]
            continue
        c = subprocess.run(['node', os.path.join(ROOT, 'bin', 'curlyc.ts'), '-o', path[:-3], path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        if c.returncode != 0:
            diffs.append(('the compiler refused a program whose patterns it took one by one', c.stderr.decode(errors='replace')[:300], ''))
            return 0, faults, diffs, complaints
        try:
            b = subprocess.run([path[:-3]], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300)
        except subprocess.TimeoutExpired:
            diffs.append(('the compiled program ran past five minutes', '', ''))
            return 0, faults, diffs, complaints
        if b.returncode != 0:
            m = re.search(rb'^fault: (.*) at .* line (\d+)\.$', b.stderr, re.M)
            if m is None:
                diffs.append(('the compiled program stopped, and not with a fault', b.stderr.decode(errors='replace')[:300], ''))
                return 0, faults, diffs, complaints
            at = bisect.bisect_right(starts, int(m.group(2))) - 1
            faults.append((m.group(1).decode(), tests[at][1], tests[at][2]))
            del tests[at]
            continue
        if b.stderr:
            diffs.append(('the compiled program wrote to stderr', b.stderr.decode(errors='replace')[:300], ''))
        pl, bl = p.stdout.decode().splitlines(), b.stdout.decode().splitlines()
        by = {t[0]: t for t in tests}
        bad = set()
        for x, y in zip(pl, bl):
            if x != y:
                n = int(x.split(' ')[0])
                if n not in bad:
                    bad.add(n)
                    diffs.append((by[n][1], x, y))
        if len(pl) != len(bl) and not bad:
            diffs.append(('the outputs are of different lengths', str(len(pl)), str(len(bl))))
        pairs = sum(len(t[2]) for t in tests if t[0] not in bad)
        return pairs, faults, diffs, complaints
    return 0, faults, diffs, complaints + [('forty tries', [])]


def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    mode = sys.argv[3] if len(sys.argv) > 3 else 'wide'
    r = random.Random(seed)
    g = Gen(r, mode)
    seen, cases = set(), []
    while len(cases) < count:
        written, subjects = g.pattern()
        if written in seen:
            continue
        seen.add(written)
        cases.append((written, subjects))
    programs = [probe(w) for w, _ in cases]
    ours = classify(['node', os.path.join(HERE, 'classify.ts')], programs)
    perls = classify([PERL, os.path.join(HERE, 'classify.pl')], programs)

    taken_warned, taken_died, refused, refused_quiet, internal = {}, {}, {}, {}, []
    tests = []
    for n, ((written, subjects), o, p) in enumerate(zip(cases, ours, perls)):
        if o.startswith('internal'):
            internal.append((written, o))
        elif o == '' and p.startswith('W: '):
            taken_warned.setdefault(re.sub(r' in regex;.*| at \(eval.*', '', p[3:])[:70], []).append(written)
        elif o == '' and p.startswith('D: '):
            taken_died.setdefault(re.sub(r' in regex;.*| at \(eval.*', '', p[3:])[:70], []).append(written)
        elif o == '':
            tests.append((n, written, subjects, bool(re.search(r'g[a-z]*$', written))))
        else:
            key = re.sub(r"'[^']*'|\\\S+|\{[^}]*\}|U\+\w+", '_', o)[:60]
            refused[key] = refused.get(key, 0) + 1
            if p == '':
                refused_quiet.setdefault(key, []).append(written)

    print(f'{mode}, seed {seed}: {len(cases)} patterns; the compiler takes {len(tests) + sum(map(len, taken_warned.values())) + sum(map(len, taken_died.values()))}, refuses {sum(refused.values())}')
    for what, table in (('perl WARNS of as it compiles', taken_warned), ('perl DIES at as it compiles', taken_died)):
        print(f'taken by the compiler, and {what}: {sum(map(len, table.values()))}')
        for key, ws in sorted(table.items(), key=lambda kv: -len(kv[1])):
            print(f'  {len(ws):5}  {key}    e.g. {min(ws, key=len)!r}')
    for written, o in internal[:10]:
        print(f'INTERNAL: {written!r}: {o}')

    pairs, faults, diffs, complaints = 0, [], [], []
    with tempfile.TemporaryDirectory() as tmp:
        size = 150
        batches = [tests[k:k + size] for k in range(0, len(tests), size)]
        with ThreadPoolExecutor(max_workers=int(os.environ.get('JOBS', '3'))) as pool:
            for a, b, c, d in pool.map(lambda kb: run_batch(tmp, kb[0], kb[1]), enumerate(batches)):
                pairs += a
                faults += b
                diffs += c
                complaints += d
    print(f'run under perl and compiled: {len(tests)} patterns, {sum(len(t[2]) for t in tests)} pairs of a pattern and a subject; the same: {pairs} pairs')
    print(f'faults of the compiled program: {len(faults)}')
    kinds = {}
    for what, written, _ in faults:
        kinds.setdefault(what, []).append(written)
    for what, ws in sorted(kinds.items(), key=lambda kv: -len(kv[1])):
        print(f'  {len(ws):5}  {what}    e.g. {min(ws, key=len)!r}')
    print(f"perl's own complaints as it ran: {len(complaints)}")
    for what, written in complaints[:12]:
        print(f'  {what}    {written!r}')
    print(f'DIFFERENT: {len(diffs)}')
    for written, x, y in diffs[:40]:
        print(f'  {written!r}\n    perl:     {x}\n    compiled: {y}')
    print(f'refused: {sum(refused.values())}, of which perl compiles in silence {sum(map(len, refused_quiet.values()))}')
    for key, n in sorted(refused.items(), key=lambda kv: -kv[1])[:60]:
        quiet = refused_quiet.get(key, [])
        print(f'  {n:5} ({len(quiet):5} quiet)  {key}' + (f'    e.g. {min(quiet, key=len)!r}' if quiet else ''))
    sys.exit(1 if diffs or taken_warned or taken_died or internal else 0)


if __name__ == '__main__':
    main()
