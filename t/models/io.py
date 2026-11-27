#!/usr/bin/env python3
"""t/4700 to t/4733 and the faults t/4740 to t/4762: stdin, @ARGV, %ENV,
exit, STDOUT and printf to a handle (step 21a; D211 to D219).

The definition, which is all this file knows of them:

  <STDIN>, one value wanted   the next line of the input, its newline
                              kept (the last may have none), or undef
                              when none is left, every time after
  <STDIN>, a list wanted      every line that is left: among a call's
                              arguments, on the right of a list
                              assignment, a loop's list, a map's block,
                              (<STDIN>) x N, say and print
  a line                      without `use open` each byte a character;
                              with it, UTF-8, and a byte that is not is
                              the fault `malformed UTF-8 read`, as are a
                              surrogate, past U+10FFFF, an overlong form,
                              a noncharacter, and a character cut short
  while (my $l = <STDIN>)     tested with defined: a last line 0 is read
  eof(STDIN)                  no line is left
  @ARGV                       the arguments, an array the program changes
  %ENV                        the environment; a change is the fault
                              `%ENV is read-only`
  exit N                      the status N's whole part, its low eight
                              bits; a try does not catch it
  say/print/printf STDOUT     to stdout; printf STDERR to stderr, formatted
  chomp(my $x = E)            $x is E less one newline at its end

perl is the second derivation (t/checks.py oracle). A test's stdin,
arguments and environment are its headers, which t/run.sh and the oracle
give perl and the program alike (D220).

Every command that writes a file, one a line (t/checks.py runs them all):

    python3 t/models/io.py --program 4700 > t/4700-io-lines.pl
    python3 t/models/io.py 4700 > t/4700-io-lines.expected
    python3 t/models/io.py --program 4701 > t/4701-io-rest-into-an-array.pl
    python3 t/models/io.py 4701 > t/4701-io-rest-into-an-array.expected
    python3 t/models/io.py --program 4702 > t/4702-io-call-arguments.pl
    python3 t/models/io.py 4702 > t/4702-io-call-arguments.expected
    python3 t/models/io.py --program 4703 > t/4703-io-list-assignment.pl
    python3 t/models/io.py 4703 > t/4703-io-list-assignment.expected
    python3 t/models/io.py --program 4704 > t/4704-io-loop-list.pl
    python3 t/models/io.py 4704 > t/4704-io-loop-list.expected
    python3 t/models/io.py --program 4705 > t/4705-io-map-block.pl
    python3 t/models/io.py 4705 > t/4705-io-map-block.expected
    python3 t/models/io.py --program 4706 > t/4706-io-repeat.pl
    python3 t/models/io.py 4706 > t/4706-io-repeat.expected
    python3 t/models/io.py --program 4707 > t/4707-io-bytes.pl
    python3 t/models/io.py 4707 > t/4707-io-bytes.expected
    python3 t/models/io.py --program 4708 > t/4708-io-utf8.pl
    python3 t/models/io.py 4708 > t/4708-io-utf8.expected
    python3 t/models/io.py --program 4709 > t/4709-io-eof.pl
    python3 t/models/io.py 4709 > t/4709-io-eof.expected
    python3 t/models/io.py --program 4710 > t/4710-io-argv.pl
    python3 t/models/io.py 4710 > t/4710-io-argv.expected
    python3 t/models/io.py --program 4711 > t/4711-io-env.pl
    python3 t/models/io.py 4711 > t/4711-io-env.expected
    python3 t/models/io.py --program 4712 > t/4712-io-stdout.pl
    python3 t/models/io.py 4712 > t/4712-io-stdout.expected
    python3 t/models/io.py --program 4713 > t/4713-io-printf-stderr.pl
    python3 t/models/io.py 4713 > t/4713-io-printf-stderr.expected
    python3 t/models/io.py --program 4714 > t/4714-io-chomp-assigned.pl
    python3 t/models/io.py 4714 > t/4714-io-chomp-assigned.expected
    python3 t/models/io.py --program 4715 > t/4715-io-numbers.pl
    python3 t/models/io.py 4715 > t/4715-io-numbers.expected
    python3 t/models/io.py --program 4716 > t/4716-io-tested.pl
    python3 t/models/io.py 4716 > t/4716-io-tested.expected
    python3 t/models/io.py --program 4720 > t/4720-exit-3.pl
    python3 t/models/io.py 4720 > t/4720-exit-3.expected
    python3 t/models/io.py --program 4721 > t/4721-exit-256.pl
    python3 t/models/io.py 4721 > t/4721-exit-256.expected
    python3 t/models/io.py --program 4722 > t/4722-exit-minus-one.pl
    python3 t/models/io.py 4722 > t/4722-exit-minus-one.expected
    python3 t/models/io.py --program 4723 > t/4723-exit-big.pl
    python3 t/models/io.py 4723 > t/4723-exit-big.expected
    python3 t/models/io.py --program 4724 > t/4724-exit-num.pl
    python3 t/models/io.py 4724 > t/4724-exit-num.expected
    python3 t/models/io.py --program 4725 > t/4725-exit-string.pl
    python3 t/models/io.py 4725 > t/4725-exit-string.expected
    python3 t/models/io.py --program 4726 > t/4726-exit-bare.pl
    python3 t/models/io.py 4726 > t/4726-exit-bare.expected
    python3 t/models/io.py --program 4727 > t/4727-exit-in-try.pl
    python3 t/models/io.py 4727 > t/4727-exit-in-try.expected
    python3 t/models/io.py --program 4728 > t/4728-exit-in-map.pl
    python3 t/models/io.py 4728 > t/4728-exit-in-map.expected
    python3 t/models/io.py --program 4729 > t/4729-exit-modifier.pl
    python3 t/models/io.py 4729 > t/4729-exit-modifier.expected
    python3 t/models/io.py --program 4730 > t/4730-exit-brackets.pl
    python3 t/models/io.py 4730 > t/4730-exit-brackets.expected
    python3 t/models/io.py --program 4731 > t/4731-exit-count.pl
    python3 t/models/io.py 4731 > t/4731-exit-count.expected
    python3 t/models/io.py --program 4732 > t/4732-exit-zero.pl
    python3 t/models/io.py 4732 > t/4732-exit-zero.expected
    python3 t/models/io.py --program 4733 > t/4733-exit-in-sort.pl
    python3 t/models/io.py 4733 > t/4733-exit-in-sort.expected
    python3 t/models/io.py --program 4740 > t/4740-fault-utf8-latin1-byte.pl
    python3 t/models/io.py 4740 > t/4740-fault-utf8-latin1-byte.expected
    python3 t/models/io.py --program 4741 > t/4741-fault-utf8-surrogate.pl
    python3 t/models/io.py 4741 > t/4741-fault-utf8-surrogate.expected
    python3 t/models/io.py --program 4742 > t/4742-fault-utf8-past-the-last.pl
    python3 t/models/io.py 4742 > t/4742-fault-utf8-past-the-last.expected
    python3 t/models/io.py --program 4743 > t/4743-fault-utf8-overlong.pl
    python3 t/models/io.py 4743 > t/4743-fault-utf8-overlong.expected
    python3 t/models/io.py --program 4744 > t/4744-fault-utf8-noncharacter.pl
    python3 t/models/io.py 4744 > t/4744-fault-utf8-noncharacter.expected
    python3 t/models/io.py --program 4745 > t/4745-fault-utf8-noncharacter-fdd0.pl
    python3 t/models/io.py 4745 > t/4745-fault-utf8-noncharacter-fdd0.expected
    python3 t/models/io.py --program 4746 > t/4746-fault-utf8-cut-alone.pl
    python3 t/models/io.py 4746 > t/4746-fault-utf8-cut-alone.expected
    python3 t/models/io.py --program 4747 > t/4747-fault-utf8-cut-after.pl
    python3 t/models/io.py 4747 > t/4747-fault-utf8-cut-after.expected
    python3 t/models/io.py --program 4748 > t/4748-fault-utf8-mid-line.pl
    python3 t/models/io.py 4748 > t/4748-fault-utf8-mid-line.expected
    python3 t/models/io.py --program 4749 > t/4749-fault-utf8-in-a-list.pl
    python3 t/models/io.py 4749 > t/4749-fault-utf8-in-a-list.expected
    python3 t/models/io.py --program 4750 > t/4750-fault-env-store.pl
    python3 t/models/io.py 4750 > t/4750-fault-env-store.expected
    python3 t/models/io.py --program 4751 > t/4751-fault-env-delete.pl
    python3 t/models/io.py 4751 > t/4751-fault-env-delete.expected
    python3 t/models/io.py --program 4752 > t/4752-fault-env-assigned.pl
    python3 t/models/io.py 4752 > t/4752-fault-env-assigned.expected
    python3 t/models/io.py --program 4753 > t/4753-fault-env-through-a-reference.pl
    python3 t/models/io.py 4753 > t/4753-fault-env-through-a-reference.expected
    python3 t/models/io.py --program 4754 > t/4754-fault-env-step.pl
    python3 t/models/io.py 4754 > t/4754-fault-env-step.expected
    python3 t/models/io.py --program 4755 > t/4755-fault-env-new-key.pl
    python3 t/models/io.py 4755 > t/4755-fault-env-new-key.expected
    python3 t/models/io.py --program 4756 > t/4756-fault-exit-not-a-number.pl
    python3 t/models/io.py 4756 > t/4756-fault-exit-not-a-number.expected
    python3 t/models/io.py --program 4757 > t/4757-fault-exit-undef.pl
    python3 t/models/io.py 4757 > t/4757-fault-exit-undef.expected
    python3 t/models/io.py --program 4758 > t/4758-fault-exit-reference.pl
    python3 t/models/io.py 4758 > t/4758-fault-exit-reference.expected
    python3 t/models/io.py --program 4759 > t/4759-fault-line-past-the-end.pl
    python3 t/models/io.py 4759 > t/4759-fault-line-past-the-end.expected
    python3 t/models/io.py --program 4760 > t/4760-fault-chomp-past-the-end.pl
    python3 t/models/io.py 4760 > t/4760-fault-chomp-past-the-end.expected
    python3 t/models/io.py --program 4761 > t/4761-fault-wide-line-without-open.pl
    python3 t/models/io.py 4761 > t/4761-fault-wide-line-without-open.expected
    python3 t/models/io.py --program 4762 > t/4762-fault-env-slice-store.pl
    python3 t/models/io.py 4762 > t/4762-fault-env-slice-store.expected
"""

import random
import sys

OPEN = "use open ':std', ':encoding(UTF-8)';"
FILE = 't/{name}.pl'


def stdin_header(data):
    """A `# stdin:` header for these bytes, in printf %b's escapes."""
    out = ''
    for b in data:
        c = chr(b)
        if c == '\\':
            out += '\\\\'
        elif c == '\n':
            out += '\\n'
        elif 0x20 <= b < 0x7f:
            out += c
        else:
            out += '\\0%03o' % b
    return out


def lines_of(data):
    """The lines perl reads, as bytes."""
    found, start = [], 0
    for k, b in enumerate(data):
        if b == 0x0A:
            found.append(data[start:k + 1])
            start = k + 1
    if start < len(data):
        found.append(data[start:])
    return found


def show(line):
    """A line as a program prints it between brackets, ASCII only."""
    return line.decode('latin-1')


def random_lines(rnd, n, last_newline=True, zero=False):
    words = ['a', 'bc', '0', 'x y', '', '42', ' ', 'q\tz', '-1', '0.5']
    text = '\n'.join(rnd.choice(words) for _ in range(n))
    if zero:
        text += '\n0'
    elif last_newline:
        text += '\n'
    return text.encode()


def program(stdin=None, args=None, env=None, kind=None, prelude=(), body=()):
    head = []
    if kind:
        head.append(f'# kind: {kind}')
    if stdin is not None:
        head.append(f'# stdin: {stdin_header(stdin)}')
    if args is not None:
        head.append(f'# args: {args}')
    if env is not None:
        head.append(f'# env: {env}')
    return head, list(prelude), list(body)


# ---- the same tests

def case_lines(rnd):
    data = random_lines(rnd, 6, zero=True)
    lines = lines_of(data)
    body = [
        'my $first = <STDIN>;',
        'print "first [$first]";',
        'my $n = 0;',
        'while (my $line = <STDIN>) { $n++; print "$n [$line]"; }',
        'say "";',
        'my $after = <STDIN>;',
        'say defined $after ? "a line" : "undef";',
        '$after = <STDIN>;',
        'say defined $after ? "a line" : "undef";',
        'my @none = <STDIN>;',
        'say scalar(@none);',
    ]
    out = f'first [{show(lines[0])}]'
    for k, line in enumerate(lines[1:], 1):
        out += f'{k} [{show(line)}]'
    out += '\nundef\nundef\n0\n'
    return program(stdin=data, body=body), out


def case_rest(rnd):
    data = random_lines(rnd, 5, last_newline=False)
    lines = lines_of(data)
    body = [
        'my $one = <STDIN>;',
        'my @rest = <STDIN>;',
        'say scalar(@rest);',
        'print "[$one]";',
        'print "<$_>" for @rest;',
        'say "";',
        'say $#rest;',
    ]
    out = f'{len(lines) - 1}\n[{show(lines[0])}]' + ''.join(f'<{show(x)}>' for x in lines[1:]) + f'\n{len(lines) - 2}\n'
    return program(stdin=data, body=body), out


def case_call(rnd):
    data = random_lines(rnd, 4)
    lines = lines_of(data)
    body = [
        'sub count(@lines) { return scalar(@lines) }',
        'sub last_of(@lines) { return $lines[-1] }',
        'my $first = <STDIN>;',
        'say count(<STDIN>);',
        'say count(<STDIN>);',
        'print "[$first]";',
        'say join("|", "x", <STDIN>, "y");',
    ]
    out = f'{len(lines) - 1}\n0\n[{show(lines[0])}]x|y\n'
    return program(stdin=data, body=body), out


def case_list_assign(rnd):
    data = random_lines(rnd, 4)
    lines = lines_of(data)
    body = [
        'my ($p, $q) = <STDIN>;',
        'my $r = <STDIN>;',
        'print "[$p][$q]";',
        'say defined $r ? "more" : "none";',
        'my %h = (a => 1);',
        'my @got = (<STDIN>);',
        'say scalar(@got);',
    ]
    out = f'[{show(lines[0])}][{show(lines[1])}]none\n0\n'
    return program(stdin=data, body=body), out


def case_loop_list(rnd):
    data = random_lines(rnd, 5, last_newline=False)
    lines = lines_of(data)
    body = [
        'my $n = 0;',
        'for my $line (<STDIN>) { $n++; print "$n<$line>"; }',
        'say "";',
        'say "done $n";',
    ]
    out = ''.join(f'{k}<{show(x)}>' for k, x in enumerate(lines, 1)) + f'\ndone {len(lines)}\n'
    return program(stdin=data, body=body), out


def case_map(rnd):
    data = random_lines(rnd, 3)
    lines = lines_of(data)
    body = [
        'my @all = map { <STDIN> } 1 .. 3;',
        'say scalar(@all);',
        'my @tested = grep { defined(<STDIN>) } 1 .. 2;',
        'say scalar(@tested);',
        'print @all;',
    ]
    out = f'{len(lines)}\n0\n' + ''.join(show(x) for x in lines)
    return program(stdin=data, body=body), out


def case_repeat(rnd):
    data = b'a\nb\nc\n'
    body = [
        'my $twice = <STDIN> x 2;',
        'print $twice;',
        'my @twice = (<STDIN>) x 2;',
        'print @twice;',
        'say scalar(@twice);',
    ]
    out = 'a\na\nb\nc\nb\nc\n4\n'
    return program(stdin=data, body=body), out


def case_bytes(rnd):
    data = bytes([0xC3, 0xA9, 0x0A, 0xE9, 0x0A, 0x00, 0x41, 0x0A, 0x41, 0x0D, 0x0A, 0xFF])
    lines = lines_of(data)
    body = [
        'while (my $line = <STDIN>) {',
        '    my @ords;',
        '    for my $i (0 .. length($line) - 1) { push @ords, ord(substr($line, $i, 1)); }',
        '    say length($line), ": @ords";',
        '}',
    ]
    out = ''.join(f'{len(x)}: {" ".join(str(b) for b in x)}\n' for x in lines)
    return program(stdin=data, body=body), out


def case_utf8(rnd):
    text = 'é\n☺ and ☺\n\U0001F600x\n﻿\nplain'
    data = text.encode()
    lines = text.splitlines(keepends=True)
    body = [
        'while (my $line = <STDIN>) {',
        '    print length($line), " ", ord($line), " ", $line;',
        '}',
        'say "";',
    ]
    out = ''.join(f'{len(x)} {ord(x[0])} {x}' for x in lines) + '\n'
    return program(stdin=data, prelude=['use utf8;', OPEN], body=body), out


def case_eof(rnd):
    data = b'one\ntwo'
    body = [
        'say eof(STDIN) ? "end" : "more";',
        'my $a1 = <STDIN>;',
        'say eof(STDIN) ? "end" : "more";',
        'my $a2 = <STDIN>;',
        'say eof(STDIN) ? "end" : "more";',
        'print $a1, $a2, "\\n";',
        'say "still" unless eof(STDIN);',
        'say "at the end" if eof(STDIN);',
        'my $more = 0;',
        'until (eof(STDIN)) { my $l = <STDIN>; $more++; }',
        'say $more;',
    ]
    out = 'more\nmore\nend\none\ntwo\nat the end\n0\n'
    return program(stdin=data, body=body), out


def case_argv(rnd):
    args = ['one', '2', 'three-3', '0', '-x', '1.5']
    body = [
        'say scalar(@ARGV);',
        'say "@ARGV";',
        'say $#ARGV;',
        'say $ARGV[0], "|", $ARGV[-1];',
        'say $ARGV[1] + $ARGV[5];',
        'my $first = shift @ARGV;',
        'say $first, " ", scalar(@ARGV);',
        'push @ARGV, "last";',
        'say join(",", @ARGV);',
        'for my $a1 (@ARGV) { print length($a1); }',
        'say "";',
        'sub show(@all) { return join("+", @all) }',
        'say show(@ARGV);',
        'my @sorted = sort @ARGV;',
        'say "@sorted";',
        'say defined $ARGV[20] ? "defined" : "undef";',
        '@ARGV = ();',
        'say scalar(@ARGV);',
    ]
    rest = args[1:] + ['last']
    out = (f'{len(args)}\n{" ".join(args)}\n{len(args) - 1}\none|1.5\n3.5\none {len(args) - 1}\n'
           f'{",".join(rest)}\n{"".join(str(len(a)) for a in rest)}\n{"+".join(rest)}\n{" ".join(sorted(rest))}\nundef\n0\n')
    return program(args=' '.join(args), body=body), out


def case_env(rnd):
    env = {'CURLY_IO_A': 'one', 'CURLY_IO_EMPTY': '', 'CURLY_IO_N': '41', 'CURLY_IO_EQ': 'a=b'}
    body = [
        'say $ENV{CURLY_IO_A};',
        'say "[$ENV{CURLY_IO_EMPTY}]";',
        'say $ENV{CURLY_IO_N} + 1;',
        'say $ENV{CURLY_IO_EQ};',
        'say exists $ENV{CURLY_IO_EMPTY} ? "there" : "not";',
        'say exists $ENV{CURLY_IO_NONE} ? "there" : "not";',
        'say defined $ENV{CURLY_IO_NONE} ? "defined" : "undef";',
        'say $ENV{CURLY_IO_NONE} // "default";',
        'my @mine = sort grep { substr($_, 0, 8) eq "CURLY_IO" } keys %ENV;',
        'say "@mine";',
        'my $name = "CURLY_IO_A";',
        'say "the value: $ENV{$name}";',
        'my %copy = %ENV;',
        '$copy{CURLY_IO_A} = "changed";',
        'say $copy{CURLY_IO_A}, " ", $ENV{CURLY_IO_A};',
        'my $r = \\%ENV;',
        'say $r->{CURLY_IO_N};',
        'say defined $ENV{PATH} ? "path" : "none";',
    ]
    mine = sorted(env)
    out = f'one\n[]\n42\na=b\nthere\nnot\nundef\ndefault\n{" ".join(mine)}\nthe value: one\nchanged one\n41\npath\n'
    return program(env=' '.join(f'{k}={v}' for k, v in env.items()), body=body), out


def case_stdout(rnd):
    body = [
        'say STDOUT "a", 1;',
        'print STDOUT "b", "\\n";',
        'printf STDOUT "%03d|%s|%.2f\\n", 7, "x", 1.5;',
        'printf STDOUT "%s\\n", "no brackets";',
        'my @l = ("p", "q");',
        'say STDOUT @l;',
        'printf "%d\\n", 9;',
        'say STDOUT "on" if 1;',
    ]
    out = 'a1\nb\n007|x|1.50\nno brackets\npq\n9\non\n'
    return program(body=body), out


def case_printf_err(rnd):
    body = [
        'say "before";',
        'printf STDERR "%d-%s\\n", 5, "a";',
        'printf STDERR "%5.1f|%-3s|\\n", 2.25, "b";',
        'printf STDERR "%x\\n", 255;',
        'say "after";',
    ]
    out = 'before\nafter\n5-a\n  2.2|b  |\nff\n'
    return program(kind='warns', body=body), out


def case_chomp(rnd):
    data = b'first\nsecond\n\nlast'
    body = [
        'chomp(my $a1 = <STDIN>);',
        'say "[$a1]";',
        'my $a2;',
        'chomp($a2 = <STDIN>);',
        'say "[$a2]";',
        'chomp(my $a3 = <STDIN>);',
        'say "[$a3]";',
        'chomp(my $a4 = <STDIN>);',
        'say "[$a4]";',
        'chomp(my $s = "x\\n\\n");',
        'say length $s;',
        'chomp(my $n = 41);',
        'say $n + 1;',
    ]
    out = '[first]\n[second]\n[]\n[last]\n2\n42\n'
    return program(stdin=data, body=body), out


def case_numbers(rnd):
    nums = [rnd.randint(-50, 50) for _ in range(6)]
    data = ''.join(f'{n}\n' for n in nums).encode()
    body = [
        'my $total = 0;',
        'my $count = 0;',
        'while (my $line = <STDIN>) { $total += $line; $count++; }',
        'say "$count numbers, total $total";',
    ]
    out = f'{len(nums)} numbers, total {sum(nums)}\n'
    return program(stdin=data, body=body), out


def case_tested(rnd):
    data = b'0\n0'
    body = [
        'my $l = <STDIN>;',
        'say $l ? "true" : "false";',
        'if (my $m = <STDIN>) { say "true" } else { say "false: [$m]" }',
        'my $n = <STDIN> // "end";',
        'say $n;',
        'my $o = <STDIN> || "nothing";',
        'say $o;',
    ]
    out = 'true\nfalse: [0]\nend\nnothing\n'
    return program(stdin=data, body=body), out


EXITS = {
    4720: (['say "a";', 'exit 3;', 'say "b";'], 'a\nexit: 3\n'),
    4721: (['exit 256;'], ''),
    4722: (['exit -1;'], 'exit: 255\n'),
    4723: (['exit 2 ** 40 + 5;'], 'exit: 5\n'),
    4724: (['exit 1.9;'], 'exit: 1\n'),
    4725: (['my $s = "2";', 'exit $s;'], 'exit: 2\n'),
    4726: (['print "partial";', 'exit;', 'say "no";'], 'partial'),
    4727: (['try { say "in"; exit 4; } catch ($e) { say "caught"; }', 'say "after";'], 'in\nexit: 4\n'),
    4728: (['sub f($n) { exit 5 if $n == 2; return $n }', 'my @a = map { f($_) } 1 .. 3;', 'say "no";'], 'exit: 5\n'),
    4729: (['my $x = 1;', 'exit 3 if $x;', 'say "no";'], 'exit: 3\n'),
    4730: (['exit(7);'], 'exit: 7\n'),
    4731: (['my @a = (1, 2, 3);', 'say "out";', 'exit @a;'], 'out\nexit: 3\n'),
    4732: (['say "zero";', 'exit 0 unless 0;', 'say "no";'], 'zero\n'),
    4733: (['my @s = sort { exit 6 if $a eq "c"; $a cmp $b } ("b", "a", "c");', 'say "no";'], 'exit: 6\n'),
}


def case_exit(n):
    body, out = EXITS[n]
    return program(body=body), out


# ---- the faults: what the program printed, and its fault's line

def fault(head, prelude, body, printed, message, line):
    """A fault test: `line` counts the program's own lines from 1."""
    return (head, prelude, body), (printed, message, line)


MALFORMED = {
    4740: b'ok\n\xe9\n',
    4741: b'ok\n\xed\xa0\x80\n',
    4742: b'ok\n\xf4\x90\x80\x80\n',
    4743: b'ok\n\xc0\x81\n',
    4744: b'ok\n\xef\xbf\xbf\n',
    4745: b'ok\n\xef\xb7\x90\n',
    4746: b'ok\n\xc3',
    4747: b'ok\na\xc3',
    4748: b'ok\nab\xe9cd\n',
}


def case_fault(n):
    if n in MALFORMED:
        head, _, _ = program(stdin=MALFORMED[n])
        body = ['my $first = <STDIN>;', 'print $first;', 'my $second = <STDIN>;', 'say "not reached";']
        return fault(head, [OPEN], body, 'ok\n', 'malformed UTF-8 read', 3)
    if n == 4749:
        head, _, _ = program(stdin=b'one\ntwo\n\xff\n')
        body = ['say "start";', 'my @all = <STDIN>;', 'say "not reached";']
        return fault(head, [OPEN], body, 'start\n', 'malformed UTF-8 read', 2)
    env_changes = {
        4750: '$ENV{CURLY_IO_A} = "b";',
        4751: 'delete $ENV{CURLY_IO_A};',
        4752: '%ENV = (CURLY_IO_A => "b");',
        4753: 'my $r = \\%ENV; $r->{CURLY_IO_A} = "b";',
        4754: '$ENV{CURLY_IO_A}++;',
        4755: '$ENV{CURLY_IO_NEW} .= "x";',
        4762: '@ENV{"CURLY_IO_A", "CURLY_IO_B"} = (1, 2);',
    }
    if n in env_changes:
        head, _, _ = program(env='CURLY_IO_A=a')
        body = ['say $ENV{CURLY_IO_A};', env_changes[n], 'say "not reached";']
        return fault(head, [], body, 'a\n', '%ENV is read-only', 2)
    if n == 4756:
        return fault([], [], ['say "before";', 'exit "three";'], 'before\n', 'not a numeric string', 2)
    if n == 4757:
        return fault([], [], ['my $u;', 'say "before";', 'exit $u;'], 'before\n', 'undef where a number is wanted', 3)
    if n == 4758:
        return fault([], [], ['my $r = [3];', 'exit $r;'], '', 'a reference where a number is wanted', 2)
    if n == 4759:
        head, _, _ = program(stdin=b'only\n')
        return fault(head, [], ['my $a1 = <STDIN>;', 'print $a1;', 'my $a2 = <STDIN>;', 'print $a2;'], 'only\n', 'undef where a string is wanted', 4)
    if n == 4760:
        head, _, _ = program(stdin=b'')
        return fault(head, [], ['say "before";', 'chomp(my $l = <STDIN>);', 'say "not reached";'], 'before\n', 'undef where a string is wanted', 2)
    if n == 4761:
        head, _, _ = program(stdin=b'plain\n\xc3\xa9\n')
        return fault(head, [], ['my $a1 = <STDIN>;', 'print $a1;', 'my $a2 = <STDIN>;', 'print $a2;'], 'plain\n', "a character past ASCII printed without 'use open'", 4)
    raise SystemExit(f'no case {n}')


SAME = {4700: case_lines, 4701: case_rest, 4702: case_call, 4703: case_list_assign, 4704: case_loop_list,
        4705: case_map, 4706: case_repeat, 4707: case_bytes, 4708: case_utf8, 4709: case_eof, 4710: case_argv,
        4711: case_env, 4712: case_stdout, 4713: case_printf_err, 4714: case_chomp, 4715: case_numbers,
        4716: case_tested}

NAMES = {
    4740: 'fault-utf8-latin1-byte', 4741: 'fault-utf8-surrogate', 4742: 'fault-utf8-past-the-last',
    4743: 'fault-utf8-overlong', 4744: 'fault-utf8-noncharacter', 4745: 'fault-utf8-noncharacter-fdd0',
    4746: 'fault-utf8-cut-alone', 4747: 'fault-utf8-cut-after', 4748: 'fault-utf8-mid-line',
    4749: 'fault-utf8-in-a-list', 4750: 'fault-env-store', 4751: 'fault-env-delete', 4752: 'fault-env-assigned',
    4753: 'fault-env-through-a-reference', 4754: 'fault-env-step', 4755: 'fault-env-new-key',
    4756: 'fault-exit-not-a-number', 4757: 'fault-exit-undef', 4758: 'fault-exit-reference',
    4759: 'fault-line-past-the-end', 4760: 'fault-chomp-past-the-end', 4761: 'fault-wide-line-without-open',
    4762: 'fault-env-slice-store',
}


def render(n, head, prelude, body, kind=None):
    hdr = list(head)
    if kind and not any(h.startswith('# kind:') for h in hdr):
        hdr.insert(0, f'# kind: {kind}')
    return '\n'.join([f'# t/models/io.py {n}', *hdr, 'use v5.42;', *prelude, *body]) + '\n'


def main(argv):
    want_program = argv[0] == '--program'
    n = int(argv[-1])
    rnd = random.Random(n)
    if n in SAME or n in EXITS:
        (head, prelude, body), out = SAME[n](rnd) if n in SAME else case_exit(n)
        sys.stdout.write(render(n, head, prelude, body) if want_program else out)
        return
    (head, prelude, body), (printed, message, line) = case_fault(n)
    # The program's first line is the comment naming this model, then the
    # headers, then `use v5.42;` and the prelude: the fault's line counts
    # from the first line of the file.
    first = 4 + len(head) + len(prelude)
    if want_program:
        sys.stdout.write(render(n, head, prelude, body, kind='fault'))
    else:
        sys.stdout.write(f'{printed}fault: {message} at {FILE.format(name=f"{n}-{NAMES[n]}")} line {first + line - 1}.\nexit: 1\n')


if __name__ == '__main__':
    main(sys.argv[1:])
