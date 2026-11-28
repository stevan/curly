#!/usr/bin/env python3
# Writes step 21b's refusal tests from a table written by hand: the program,
# the text the message points at (its column is counted here, from the
# program's own text), and the message. Nothing here asks the compiler.
# What perl does with each is in its comment, from perl 5.42 run plain in a
# directory that holds `in.txt` (`python3 docs/briefs/step21b-refusals.py
# --perl` prints each again).
#
#     python3 docs/briefs/step21b-refusals.py 6520
import os
import subprocess
import sys
import tempfile
T = []
def r(name, why, body, at, message, nth=1):
    T.append((name, why, body, at, message, nth))

SHAPE = 'open is written open(my $fh, MODE, PATH), or with a scalar variable for my $fh: three arguments, in brackets (D270)'
MODE = "open's second argument is one of the literals '<', '>' and '>>', and here is {}: a mode with a layer, a '+', a pipe or a blank, and one worked out, are not in the language (D270)"
OR = "'{}' after {}(...): what may follow it as a statement is 'or die ...' (D274); for anything else, test it with an if or an unless"
MY = 'my ${} here: a my begins a statement or a for, or stands in the test of an if or a while, where it is always reached'
BARE = "{} after close ${}: without brackets close takes one scalar variable, and then the statement ends, or a modifier or 'or' follows (D283); write close(...)"
IN = "open(my $fh, '<', 'in.txt');\n"
OUT = "open(my $fh, '>', 'o.txt');\n"
ERRNO = "'{0}' hard after $! in a string: perl reads an element of its own @! or %! there, or goes through $! as a reference (D273, T689); write $!\\{0}"
WHILE = 'write while (my $line = <$fh>) { ... }'
GLOB = "'<' where a value begins is a readline or a glob to perl: the readlines of the language are <STDIN> and <$fh>, a scalar variable hard against both angle brackets (D211, D281)"

# ---- open's shape (D270, D271)
r('open-no-brackets', 'perl opens the file.', "open my $fh, '<', 'in.txt';", 'open', f'open without brackets: {SHAPE}')
r('open-two-arguments', 'perl opens in.txt to read: the mode is read out of the name (T690).', "open(my $fh, 'in.txt');", "'in.txt'", f'open with two arguments: perl reads the mode out of the name, by its first characters; {SHAPE}')
r('open-one-and-a-mode', "perl takes '<' for the name, which says to read a file with no name: nothing opens, in silence.", "open(my $fh, '<');", "'<'", f'open with two arguments: perl reads the mode out of the name, by its first characters; {SHAPE}')
r('open-bareword', "perl does not compile it: Bareword filehandle \"FH\" not allowed under 'no feature \"bareword_filehandles\"'.", "open(FH, '<', 'in.txt');", 'FH', f'open(FH, ...): a bareword file handle, which perl refuses under use v5.42 (D270); {SHAPE}')
r('open-stdin', 'perl opens the file as its stdin.', "open(STDIN, '<', 'in.txt');", 'STDIN', f'open(STDIN, ...): a bareword file handle, which perl keeps for its own (D270); {SHAPE}')
r('open-element', 'perl puts the handle in the element.', "my %h;\nopen($h{fh}, '<', 'in.txt');", '{', f"'{{' after open's first argument: it is my $fh or a scalar variable alone, not an element or anything worked out (D271); {SHAPE}")
r('open-my-array', 'perl dies: Can\'t use string ("0") as a symbol ref.', "open(my @fh, '<', 'in.txt');", '@fh', f"after 'my' in open, expected a scalar variable, found '@fh': {SHAPE}")
r('open-string-first', "perl opens the file as a handle named x, and warns: Name \"main::x\" used only once.", "open('x', '<', 'in.txt');", "'x'", "open's first argument is my $fh or a scalar variable, and here is 'x': take the handle into a my, and store it after (D271)")
r('open-mode-layer', 'perl opens the file, its bytes as they are (T690).', "open(my $fh, '<:raw', 'in.txt');", "'<:raw'", MODE.format("'<:raw'"))
r('open-mode-encoding', 'perl opens the file as UTF-8: here `use open` says it for every file (D280).', "open(my $fh, '<:encoding(UTF-8)', 'in.txt');", "'<:", MODE.format("'<:encoding(UTF-8)'"))
r('open-mode-plus', 'perl opens the file to read and to write.', "open(my $fh, '+<', 'in.txt');", "'+<'", MODE.format("'+<'"))
r('open-mode-variable', 'perl opens the file.', "my $m = '<';\nopen(my $fh, $m, 'in.txt');", '$m,', MODE.format("'$m'"))
r('open-mode-pipe', 'perl runs ls, and reads what it prints.', "open(my $fh, '-|', 'ls');", "'-|'", MODE.format("'-|'"))
r('open-mode-blank', 'perl opens the file: a blank after the mode is nothing to it.', "open(my $fh, '< ', 'in.txt');", "'< '", MODE.format("'< '"))
r('open-mode-interpolated', 'perl opens the file.', 'my $m = "";\nopen(my $fh, "<$m", \'in.txt\');', '"<$m"', MODE.format('"<$m"'))
r('open-four-arguments', "perl dies: More than one argument to open(,':perlio').", "open(my $fh, '<', 'in.txt', 'x');", ", 'x'", f'open with more than three arguments: {SHAPE}')
r('open-or-inside', 'perl warns, Useless use of a constant ("<") in void context, and dies: the or takes the whole list for its left side.', "open(my $fh, '<', 'in.txt' or die \"x\");", 'or', "'or' in open's arguments takes them all for its left side, to perl: put it after the closing bracket, open(...) or ...")
# ---- open as a statement (D274)
r('open-or-print', 'perl opens the file, and prints nothing.', IN.rstrip(';\n') + ' or print "no\\n";', 'or', OR.format('or', 'open'))
r('open-or-return', 'perl returns 0 when the file does not open.', "sub f() {\n    open(my $fh, '<', 'in.txt') or return 0;\n    return 1;\n}", 'or', OR.format('or', 'open'))
r('open-or-warn', 'perl warns when the file does not open.', IN.rstrip(';\n') + ' or warn "no\\n";', 'or', OR.format('or', 'open'))
r('open-and', 'perl opens the file, and says x.', IN.rstrip(';\n') + ' and print "x\\n";', 'and', OR.format('and', 'open'))
r('close-or-warn', 'perl closes the file.', IN + 'close($fh) or warn "x";', 'or', OR.format('or', 'close'))
r('open-my-in-a-value', 'perl opens the file, and $ok is 1.', "my $ok = open(my $fh, '<', 'in.txt');", 'my $fh', MY.format('fh'))
r('open-my-under-a-modifier', 'perl opens the file when $ok is true, and leaves $fh as it was when it is not.', "my $ok = 1;\nopen(my $fh, '<', 'in.txt') or die \"no\\n\" if $ok;", 'my $fh', 'my under a modifier: when the test fails, perl leaves in the variable what it last held; declare it in a statement of its own')
r('open-my-in-a-modifier', 'perl opens the file, and says x.', "say \"x\" if open(my $g, '<', 'in.txt');", 'my $g', MY.format('g'))
r('open-my-in-say', 'perl says 1.', "say open(my $g, '<', 'in.txt');", 'my $g', MY.format('g'))
# ---- a line read (D281)
r('readline-blanks', 'perl globs: the one name it gives is the handle\'s address.', IN + 'my $l = < $fh >;', '< $fh', GLOB)
r('readline-chain', 'perl does not compile it: the angle brackets end at the arrow.', 'my $r = [];\nmy $l = <$r->[0]>;', '<$r', "<$r->: a line is read from a file handle in a scalar variable, <$fh>; anything more in the angle brackets is a glob to perl (D281, T693): take the handle into a my first")
r('readline-subscript', 'perl does not compile it.', IN + 'my $c = <$fh>[0];', '[', "'[' after <$fh>: take the line into a my first, or the lines into an array")
r('readline-while-bare', 'perl stores each line in its global $_ (T511).', IN + 'while (<$fh>) {\n    say "line";\n}', '<$fh>', f"a <$fh> alone in a loop's test: perl stores each line in its global $_, which is not in the language (D212, T511); {WHILE}")
r('readline-if-no-else', 'perl warns: Value of <HANDLE> construct can be "0" (T693).', IN + 'if (my $l = <$fh>) {\n    print $l;\n}', '= <', 'a line assigned in the test of an if with no else: perl warns that the line can be "0", and wants it tested with defined (D222, T518); assign the line in a statement of its own, and test it with defined(...)')
r('readline-element-key', "perl reads the key's line first (T508).", IN + 'my %h;\n$h{<$fh>} = <$fh>;', '= <$fh>;', 'a line read into an element whose index, key or reference reads a line or calls a sub: perl works the element out first and then reads, against the order of every other assignment (D213, T508); take the index into a my first')
r('readline-element-opens', 'perl opens the file, and then reads the line.', IN + "my @a;\nmy $o;\n$a[open($o, '<', 'in.txt')] = <$fh>;", '= <$fh>;', 'a line read into an element whose index, key or reference reads a line or calls a sub: perl works the element out first and then reads, against the order of every other assignment (D213, T508); take the index into a my first')
r('readline-folded', 'perl reads every line: the constant is folded away (T519).', IN + 'my @l = (0 || <$fh>);', '||', "a line read beside a constant on the left of '||': perl folds the constant away as it compiles and reads the line as if it stood alone, in another order or tested with defined (D222, T519); take the constant out")
r('readline-until', 'perl tests the line for truth, with no defined (T501).', IN + 'my $l;\nprint "x" until $l = <$fh>;', '= <', f'a line read in the test of until: perl tests it with defined in some of these shapes and not others (D212, T501); {WHILE}')
r('readline-for-test', 'perl tests the line with defined (T501).', IN + 'for (my $i = 0; my $l = <$fh>; $i++) {\n    say $i;\n}', '= <', f'a line read in the test of a for (;;): perl tests it with defined there (D212, T501); {WHILE}')
r('eof-two', 'perl asks of 1, a handle of that name, and warns: Useless use of private variable in void context.', IN + 'say eof($fh, 1) ? 1 : 0;', ', 1', 'eof takes one file handle, eof($fh) (D281)')
# ---- writing to a handle (D278)
r('print-handle-brackets', 'perl prints a to the file: after a handle the brackets are no argument list (T684).', OUT + 'print $fh ("a");', '(', 'print to a file handle, and then (...): write the list without brackets of its own; to perl they would not hold all of it (T684)', 2)
r('say-handle-brackets-times', 'perl prints 9 to the file (T684).', OUT + 'say $fh (1 + 2) * 3;', '(1', 'say to a file handle, and then (...): write the list without brackets of its own; to perl they would not hold all of it (T684)')
r('print-block-brackets', 'perl prints a to the file.', OUT + 'print {$fh} ("a");', '("', 'print to a file handle, and then (...): write the list without brackets of its own; to perl they would not hold all of it (T684)')
r('print-handle-backslash', 'perl warns: Backslash found where operator expected (T684).', 'my @a;\n' + OUT + 'print $fh \\@a;', '$fh \\', 'print $fh \\...: perl takes $fh for a file handle here, and warns (T684); write print {$fh} \\...')
r('print-handle-sign', 'perl prints -1 to the file (T684).', OUT + 'print $fh -1;', '$fh -', "print $fh -1: perl takes $fh for a file handle here; put a blank after the '-', or none before it")
r('print-handle-isa', 'perl prints nothing: $x is a file handle to it.', 'my $x = 5;\nprint $x isa Foo;', '$x isa', 'print $x isa: perl takes $x for a file handle here; bracket the test')
r('print-handle-in-brackets', 'perl prints a to the file.', OUT + 'print($fh "a");', '$fh "', 'print($fh ...): perl takes $fh for a file handle here; a handle stands before the list with no bracket, print $fh ...; (D278)')
r('print-block-nothing', 'perl does not compile it.', OUT + 'print {$fh};', ';', 'print to a file handle with nothing to print: perl prints $_', 3)
r('print-handle-modifier-alone', 'perl does not compile it.', OUT + 'say {$fh} if 1;', 'if', 'say to a file handle with nothing to print: perl prints $_')
r('print-block-comma', 'perl does not compile it.', OUT + 'print {$fh}, "a";', ', "a"', "',' after the file handle: perl prints the handle itself; no comma stands between the handle and the list")
r('print-block-empty', 'perl does not compile it.', 'print {} "a";', '{', 'print { } with nothing in the braces: what stands there gives the file handle, print {$fh} ...;')
r('print-block-statements', 'perl prints a to the file, and warns of the first statement: Useless use of private variable in void context.', OUT + 'print {$fh; $fh} "a";', '; $fh}', "a brace first after print holds one expression, which gives the file handle to write to, and here ';' follows it (D278); write +{ ... } for a new hash")
r('printf-block-stdout', 'perl does not compile it under use v5.42: Bareword "STDOUT" not allowed while "strict subs" in use.', 'printf {STDOUT} "%s\\n", "x";', 'STDOUT', "printf {STDOUT}: STDOUT is written without the braces, printf STDOUT ...; in them stands what gives a file handle of the program's own (D278)")
r('printf-handle-format-variable', 'perl prints 1 to the file.', OUT + 'my $f = "%s";\nprintf $fh $f, 1;', '$f,', "printf's format is a string literal with no variable in it (D124): perl takes the first value of an array, or a string made as the program runs, for one (T274)")
# ---- close (D283)
r('close-nothing', 'perl closes the handle selected last: stdout.', 'close();', 'close', 'close() with no file handle: to perl it closes the handle selected last, which is not in the language (D283); write close($fh)')
r('close-two', 'perl closes the second, and warns: Useless use of private variable in void context.', IN + 'my $g = $fh;\nclose($fh, $g);', 'close', 'close takes 1 to 1 arguments, and here are 2')
r('close-bare-or-or', 'perl closes the file: close $fh || die is close($fh || die).', IN + 'close $fh || die "x";', '||', BARE.format("'||'", 'fh'))
r('close-bare-element', 'perl closes the handle in the element; here there is none, and it dies.', 'my %h;\nclose $h{fh};', '{', BARE.format("'{'", 'h'))
r('close-bare-comma', 'perl closes the file.', IN + 'close $fh, 1;', ',', BARE.format("','", 'fh'), 3)
# ---- $! (D273)
r('errno-assigned', 'perl sets errno.', '$! = 0;', '=', "the left side of '=' is a variable, an element, an array, a hash, or a list of them in brackets")
r('errno-in-braces', 'perl gives $!.', 'say ${!};', '${', "${!}: perl's $! is written $! (D273)")
r('errno-hash-element', 'perl gives an element of %!, whether the last error was that one.', 'say $!{ENOENT};', '$!', "$!{ is an element of perl's own %!, which is not in the language (D273)")
r('errno-array-element', 'perl gives an element of @!, and warns.', 'say $![0];', '$!', "$![ is an element of perl's own @!, which is not in the language (D273)")
r('errno-string-index', 'perl gives an element of @!, and warns (T689).', 'say "why: $![0]";', '[', ERRNO.format('['))
r('errno-string-key', 'perl gives an element of %! (T689).', 'say "why: $!{ENOENT}";', '{', ERRNO.format('{'))
r('errno-string-arrow', "perl dies: Can't use string as an ARRAY ref (T689).", 'say "why: $!->[0]";', '->', ERRNO.format('->['))
r('errno-heredoc-key', 'perl gives an element of %!.', 'print <<"END";\nwhy: $!{x}\nEND', '{', ERRNO.format('{'))
# ---- what is not in (D270)
r('binmode', 'perl sets the layer of the handle.', IN + 'binmode($fh);', 'binmode', "'binmode' is not in the language")
r('unlink', 'perl removes the file: step 21c.', "unlink('in.txt');", 'unlink', "'unlink' is not in the language")
r('opendir', 'perl opens the directory: step 21c.', "opendir(my $d, '.');", 'opendir', "'opendir' is not in the language")
r('seek', 'perl moves to the start of the file.', IN + 'seek($fh, 0, 0);', 'seek', "'seek' is not in the language")
r('file-test', 'perl says whether the file is there: step 21c.', "my $x = -e 'in.txt';", '-e', '-e: a minus hard against one letter is a file test, to perl; put a blank after the minus, or brackets round what it negates')
r('input-separator', 'perl reads whole files from here on.', 'local $/;', '$/', "after '$' comes a name: a letter or '_', then letters, digits and '_'")
r('line-number', 'perl gives the line number of the handle read last.', IN + 'my $l = <$fh>;\nsay $.;', '$.', "after '$' comes a name: a letter or '_', then letters, digits and '_'")
r('stdin-as-a-value', 'perl gives a reference to the glob of stdin.', 'my $in = \\*STDIN;', '\\', "\\ before '*': \\ takes a named array, a named hash or a scalar variable, \\@a, \\%h or \\$x (D110)")


def write(first):
    n = first
    for name, why, body, at, message, nth in T:
        program = f'# kind: refused\n# {why}\nuse v5.42;\n{body}\n'
        path = f't/{n}-file-{name}'
        open(path + '.pl', 'w', encoding='utf-8').write(program)
        k = program.index('use v5.42;')
        for _ in range(nth):
            k = program.index(at, k + 1)
        line = program.count('\n', 0, k) + 1
        col = len(program[program.rfind('\n', 0, k) + 1:k]) + 1
        open(path + '.expected', 'w', encoding='utf-8').write(f'{path}.pl:{line}:{col}: {message}\nexit: 1\n')
        n += 1


if __name__ == '__main__':
    if sys.argv[1] == '--perl':
        for name, why, body, at, message, nth in T:
            with tempfile.TemporaryDirectory() as d:
                open(os.path.join(d, 'in.txt'), 'w').write('a\nb\n')
                try:
                    r_ = subprocess.run([os.environ.get('CURLY_PERL', 'perl'), '-e', 'use v5.42;\n' + body], capture_output=True, text=True, timeout=10, input='', cwd=d)
                except subprocess.TimeoutExpired:
                    print(f'{name}: no end in 10 seconds')
                    continue
            print(f'{name}: exit {r_.returncode}; {r_.stdout!r}; {r_.stderr.strip()[:200]!r}')
    else:
        write(int(sys.argv[1]))
