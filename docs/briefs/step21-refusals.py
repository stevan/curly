#!/usr/bin/env python3
# Writes step 21a's refusal tests from a table written by hand: the program,
# the text the message points at (its column is counted here, from the
# program's own text), and the message. Nothing here asks the compiler.
# What perl does with each is in its comment, from perl 5.42 run plain with
# an empty stdin (`python3 docs/briefs/step21-refusals.py --perl` prints
# each again).
#
#     python3 docs/briefs/step21-refusals.py 4800
import subprocess
import sys
T = []
def r(name, why, body, at, message, nth=1):
    T.append((name, why, body, at, message, nth))

WRITE = 'write while (my $line = <STDIN>) { ... }'
UNTIL = f"a line read in the test of until: perl tests it with defined in some of these shapes and not others (D212, T501); {WRITE}"
MOD = f"a line read in the test of a while modifier: perl tests it with defined in some of these shapes and not others (D212, T501); {WRITE}"
ELEM = 'a line read into an element whose index, key or reference reads a line or calls a sub: perl works the element out first and then reads, against the order of every other assignment (D213, T508); take the index into a my first'
GLOB = "'<' where a value begins is a readline or a glob to perl: the readlines of the language are <STDIN> and <$fh>, a scalar variable hard against both angle brackets (D211, D281)"
AFTER_EXIT = "{} after exit's argument: exit takes only what binds more tightly than a named unary operator, and perl warns of the rest; bracket the argument, exit(...)"

# ---- the loop's tests (D212)
r('while-bare', "perl stores each line in its global $_ (T511).", 'while (<STDIN>) {\n    say "line";\n}', '<STDIN>', f"a <STDIN> alone in a loop's test: perl stores each line in its global $_, which is not in the language (D212, T511); {WRITE}")
r('while-bare-brackets', "perl stores each line in its global $_.", 'while ((<STDIN>)) {\n    say "line";\n}', '<STDIN>', f"a <STDIN> alone in a loop's test: perl stores each line in its global $_, which is not in the language (D212, T511); {WRITE}")
r('until-assigned', "perl runs it, and tests the line for truth, with no defined (T501).", 'my $l;\nuntil ($l = <STDIN>) {\n    last;\n}', '= <', UNTIL)
r('until-my', "perl runs it, and tests the line for truth.", 'until (my $l = <STDIN>) {\n    last;\n}', '= <', UNTIL)
r('while-modifier', "perl runs it, and tests the line with defined (T501).", 'my $l;\nprint $l while $l = <STDIN>;', '= <', MOD)
r('until-modifier', "perl runs it, and on an empty stdin prints x without end.", 'my $l;\nprint "x" until $l = <STDIN>;', '= <', UNTIL)
r('modifier-bare', "perl stores each line in its global $_.", 'say "line" while <STDIN>;', '<STDIN>', f"a <STDIN> alone in a loop's test: perl stores each line in its global $_, which is not in the language (D212, T511); {WRITE}")
r('for-test', "perl runs it, and tests the line with defined (T501).", 'for (my $i = 0; my $l = <STDIN>; $i++) {\n    say $i;\n}', '= <', f"a line read in the test of a for (;;): perl tests it with defined there (D212, T501); {WRITE}")
r('for-test-assigned', "perl runs it, and tests the line with defined.", 'my $l;\nfor (my $i = 0; $l = <STDIN>; $i++) {\n    say $i;\n}', '= <', f"a line read in the test of a for (;;): perl tests it with defined there (D212, T501); {WRITE}")
# ---- an element assigned a line (D213)
r('element-key-reads', "perl reads the key's line first, then the value's (T508).", 'my %h;\n$h{<STDIN>} = <STDIN>;', '= <STDIN>;', ELEM)
r('element-index-calls', "perl calls f before it reads the line.", 'my @a;\nsub f() {\n    return 0;\n}\n$a[f()] = <STDIN>;', '= <STDIN>;', ELEM)
r('chain-head-calls', "perl calls f before it reads.", 'sub f() {\n    return [];\n}\nf()->[0] = <STDIN>;', '= <STDIN>;', ELEM)
r('element-in-while', "perl calls f and then reads, each time round.", 'my @a;\nsub f() {\n    return 0;\n}\nwhile ($a[f()] = <STDIN>) {\n    last;\n}', '= <STDIN>)', ELEM)
r('element-eof-key', "perl asks eof first, then reads.", 'my %h;\n$h{eof(STDIN)} = <STDIN>;', '= <STDIN>;', ELEM)
# ---- readline's other shapes (D211)
r('diamond', "perl reads the files named in @ARGV, or stdin (T513).", 'my $l = <>;', '<>', "<> reads the files named in @ARGV, or stdin, and is not in the language (D211): read stdin with <STDIN>")
r('double-diamond', "perl reads the files named in @ARGV, or stdin.", 'my $l = <<>>;', '<<>>', "<<>> reads the files named in @ARGV, or stdin, and is not in the language (D211): read stdin with <STDIN>")
r('bareword-handle', "perl refuses it: Bareword filehandle not allowed (T513).", 'my $l = <FH>;', '<FH>', "<FH>: a bareword file handle, which is not in the language (D211); stdin is read with <STDIN>")
r('stdout-read', "perl reads nothing, and warns: Filehandle STDOUT opened only for output.", 'my $l = <STDOUT>;', '<STDOUT>', "<STDOUT>: a bareword file handle, which is not in the language (D211); stdin is read with <STDIN>")
# (Step 21b took `<$fh>` in: the row is what is still refused, an element.)
r('lexical-handle', "perl globs: the one name it gives is the handle's address (T693).", 'my %h;\nmy $l = <$h{fh}>;', '<$h', "<$h{fh}>: a line is read from a file handle in a scalar variable, <$fh>; anything more in the angle brackets is a glob to perl (D281, T693): take the handle into a my first")
r('glob', "perl lists the files that match (T513).", 'my @f = <*.pl>;', '<*.pl>', GLOB)
r('readline-word', "perl reads a line.", 'my $l = readline(STDIN);', 'readline', "expected a value, found 'readline'")
r('subscript-after', "perl does not compile it.", 'my $l = <STDIN>[0];', '[', "'[' after <STDIN>: take the line into a my first, or the lines into an array")
r('arrow-after', "perl dies: Can't use an undefined value as an ARRAY reference.", 'my $l = <STDIN>->[0];', '->', "'->' after <STDIN>: take the line into a my first, or the lines into an array")
r('alone', "perl reads a line and drops it.", '<STDIN>;', '<STDIN>', "this statement only has a value, and nothing is done with it: perl warns that it is useless")
r('stdin-alone', "perl does not compile it: Bareword \"STDIN\" not allowed while strict subs in use.", 'my $h = STDIN;', 'STDIN', 'STDIN is read by <STDIN>, and asked of by eof(STDIN), and stands nowhere else (D211)')
r('print-to-stdin', "perl prints nothing, and warns: Filehandle STDIN opened only for input.", 'print STDIN "x";', 'STDIN', 'print STDIN: stdin is read, not written')
# ---- eof (D214)
r('eof-empty', "perl asks of the files named in @ARGV, or stdin (T509).", 'say eof() ? 1 : 0;', 'eof', 'eof() is the files named in @ARGV, or stdin, to perl, and not in the language (D214): eof(STDIN)')
r('eof-bare', "perl asks of the handle last read (T509).", 'my $l = <STDIN>;\nsay eof ? 1 : 0;', 'eof', 'eof is written with brackets, eof(STDIN) or eof($fh): eof alone is the handle perl read last (D214)')
r('eof-no-brackets', "perl asks of STDIN.", 'say eof STDIN ? 1 : 0;', 'eof', 'eof is written with brackets, eof(STDIN) or eof($fh): eof alone is the handle perl read last (D214)')
r('eof-stdout', "perl says true, and warns: Filehandle STDOUT opened only for output.", 'say eof(STDOUT) ? 1 : 0;', 'STDOUT', 'eof(STDOUT): eof takes STDIN, or a file handle in a variable, eof($fh) (D214, D281)')
# (Step 21b took `eof($fh)` in: the row is `eof $fh`, without brackets.)
r('eof-variable', "perl dies: Can't use an undefined value as a symbol reference.", 'my $fh;\nsay eof $fh ? 1 : 0;', 'eof', 'eof is written with brackets, eof(STDIN) or eof($fh): eof alone is the handle perl read last (D214)')
# ---- exit (D217)
r('exit-or', "perl exits 0, and warns: Possible precedence issue with control flow operator (T506).", 'exit 0 || 3;', '||', AFTER_EXIT.format("'||'"))
r('exit-less', "perl exits 2, and warns (T506).", 'exit 2 < 3;', '<', AFTER_EXIT.format("'<'"))
r('exit-bracket-plus', "perl exits 1, and warns.", 'exit(1) + 5;', '+', AFTER_EXIT.format("'+'"))
r('exit-comma', "perl exits 1, and warns: Useless use of a constant (2) in void context.", 'exit 1, 2;', ',', AFTER_EXIT.format("','"))
r('exit-value', "perl exits 3.", 'my $x = exit 3;', 'exit', "exit is a statement, not a value: write 'exit if ...;' or 'exit unless ...;'")
r('exit-or-statement', "perl exits 2.", 'my $x = 0;\n$x or exit 2;', 'or', "'or' after a statement joins it to what follows, to perl, which binds 'or' more loosely than '=': write it as an if")
r('exit-my', "perl does not compile it: Can't modify exit in scalar assignment.", 'exit my $x = 3;', '=', AFTER_EXIT.format("'='"))
# ---- @ARGV and %ENV (D215, D216)
r('my-argv', "perl takes it in silence, and the arguments are hidden (T505).", 'my @ARGV = (1);', 'my', 'my @ARGV: perl takes it, and the program\'s own then hides the arguments (D215); give it another name')
r('my-env', "perl takes it in silence, and the environment is hidden (T505).", 'my %ENV;', 'my', 'my %ENV: perl takes it, and the program\'s own then hides the environment (D216); give it another name')
r('my-argv-in-a-list', "perl takes it.", 'my ($x, @ARGV) = (1, 2);', '@ARGV', 'my @ARGV: perl takes it, and the program\'s own then hides the arguments (D215); give it another name')
r('program-name', "perl prints the path it was given (T510).", 'say $0;', '$0', "after '$' comes a name: a letter or '_', then letters, digits and '_'")
# ---- handles (D218)
r('printf-bracket', "perl prints 1 (T500).", 'printf(STDOUT "%d\\n", 1);', 'STDOUT', 'STDOUT stands right after say, print or printf, a blank between and no bracket before it: printf STDOUT ...;')
r('say-bracket-handle', "perl prints x.", 'say(STDERR "x");', 'STDERR', 'STDERR stands right after say, print or printf, a blank between and no bracket before it: printf STDERR ...;')
r('stdout-nothing', "perl prints $_, and warns that it is undef.", 'print STDOUT;', ';', 'print STDOUT with nothing to print: perl prints $_', 2)
r('stdout-brackets', "perl prints 1.", 'say STDOUT (1);', '(', 'say STDOUT (...): write the list without brackets of its own, say STDOUT ...;')
r('printf-stderr-format-variable', "perl prints 1 on stderr.", 'my $f = "%d\\n";\nprintf STDERR $f, 1;', '$f', "printf's format is a string literal with no variable in it (D124): perl takes the first value of an array, or a string made as the program runs, for one (T274)", 2)
# ---- chomp of an assignment (D219)
r('chomp-assign-list', "perl chomps both.", 'chomp(my ($x, $y) = ("a\\n", "b\\n"));', 'my', "chomp(...) takes one scalar variable, or the assignment of one, chomp(my $x = ...) (D219)")
r('chomp-assign-op', "perl chomps $x.", 'my $x = "a";\nchomp($x .= "\\n");', '$x', "chomp takes one scalar variable here, chomp($x): its value, an array, a hash, an element and $_ are not in the language (D130)", 2)
r('chop-assign', "perl chops it.", 'chop(my $x = "ab");', 'my', "chomp takes one scalar variable here, chomp($x): its value, an array, a hash, an element and $_ are not in the language (D130)".replace('chomp', 'chop'))
r('chomp-assign-array', "perl chomps every element.", 'chomp(my @l = ("a\\n"));', 'my', "chomp(...) takes one scalar variable, or the assignment of one, chomp(my $x = ...) (D219)")

# ---- found by the adversarial review of 21a (D222; T517 to T520, T522):
# a table of its own, written from 4851 on
#
#     python3 docs/briefs/step21-refusals.py --review 4851
REVIEW = []
def v(name, why, body, at, message, nth=1):
    REVIEW.append((name, why, body, at, message, nth))

def TESTED(where):
    return f'a line assigned {where}: perl warns that the line can be "0", and wants it tested with defined (D222, T518); assign the line in a statement of its own, and test it with defined(...)'
def FOLDED(what):
    return f'a line read beside a constant {what}: perl folds the constant away as it compiles and reads the line as if it stood alone, in another order or tested with defined (D222, T519); take the constant out'

# T517: exit's argument is a named unary operator's, and so is perl's warning (T94).
v('exit-minus-blank', 'perl exits 255, and warns: Use of "exit" without parentheses is ambiguous (T517).', 'exit - 1;', '-', 'exit -: perl warns that this is ambiguous: write exit(-...)')
v('exit-minus-hard', 'perl exits 255, and warns: Use of "exit-1" without parentheses is ambiguous.', 'exit-1;', '-', 'exit -: perl warns that this is ambiguous: write exit(-...)')
v('exit-plus-blank', 'perl exits 1, and warns that it is ambiguous.', 'exit + 1;', '+', 'exit +: perl warns that this is ambiguous: write exit(+...)')
# T518: a line assigned where perl warns that it can be "0".
v('if-no-else', "perl prints the line, and warns: Value of <HANDLE> construct can be \"0\"; test with defined() (T518).", 'if (my $l = <STDIN>) {\n    print $l;\n}', '= <', TESTED('in the test of an if with no else'))
v('unless-block', "perl warns: Value of <HANDLE> construct can be \"0\".", 'my $l;\nunless ($l = <STDIN>) {\n    say "end";\n}', '= <', TESTED('in the test of an unless with no else'))
v('if-modifier', "perl warns: Value of <HANDLE> construct can be \"0\".", 'my $l;\nprint "t" if $l = <STDIN>;', '= <', TESTED('in the test of an if with no else'))
v('unless-modifier', "perl warns: Value of <HANDLE> construct can be \"0\".", 'my $l;\nsay "end" unless $l = <STDIN>;', '= <', TESTED('in the test of an unless with no else'))
v('if-element', "perl warns of an element assigned a line too.", 'my @a;\nif ($a[0] = <STDIN>) {\n    print $a[0];\n}', '= <', TESTED('in the test of an if with no else'))
v('and-left', "perl warns: Value of <HANDLE> construct can be \"0\".", 'my $l;\nmy $x = ($l = <STDIN>) && 1;', '= <', TESTED("on the left of '&&'"))
v('or-left', "perl warns: Value of <HANDLE> construct can be \"0\".", 'my $l;\nmy $x = ($l = <STDIN>) || "f";', '= <', TESTED("on the left of '||'"))
v('dor-left', "perl runs it in silence: refused with && and ||, the reviewer's default (D222).", 'my $l;\nmy $x = ($l = <STDIN>) // "f";', '= <', TESTED("on the left of '//'"))
v('while-and-left', "perl warns, and tests the line for truth, with no defined.", 'my $l;\nwhile (($l = <STDIN>) && 1) {\n    print $l;\n}', '= <', TESTED("on the left of '&&'"))
v('elsif-and-left', "perl warns here, though of an elsif's whole test it does not.", 'my $l;\nif (@ARGV) {\n    say "args";\n} elsif (($l = <STDIN>) && 1) {\n    print $l;\n}', '= <', TESTED("on the left of '&&'"))
v('sort-block-and-left', "perl warns: Value of <HANDLE> construct can be \"0\".", 'my $l;\nmy @a = sort { ($l = <STDIN>) && 0 } 1, 2;', '= <', TESTED("on the left of '&&'"))
# T519: perl folds a constant test away, and then reads the element first.
v('folded-ternary-element', "perl reads the key's line first, then the value's: the constant is folded away (T519).", 'my %h;\n$h{<STDIN>} = 1 ? <STDIN> : 2;', '?', FOLDED('test'))
v('folded-and-element', "perl reads the key's line first.", 'my %h;\n$h{<STDIN>} = 1 && <STDIN>;', '&&', FOLDED("on the left of '&&'"))
v('folded-or-list', "perl reads every line: refused with the rest (D222).", 'my @l = (0 || <STDIN>);', '||', FOLDED("on the left of '||'"))
# T520: and then tests a loop's line with defined.
v('folded-while', "perl folds the 1 away and tests the line with defined: a last line 0 is read (T520).", 'my $l;\nwhile (1 && ($l = <STDIN>)) {\n    print $l;\n}', '&&', FOLDED("on the left of '&&'"))
v('folded-while-bare', "perl folds the test to <STDIN>, and stores each line in its global $_.", 'while (1 ? <STDIN> : 0) {\n    say "line";\n}', '?', FOLDED('test'))
v('folded-for', "perl tests the line with defined.", 'my $l;\nfor (my $i = 0; 1 && ($l = <STDIN>); $i++) {\n    print $l;\n}', '&&', FOLDED("on the left of '&&'"))
v('folded-while-modifier', "perl tests the line with defined.", 'my $l;\nprint $l while 1 && ($l = <STDIN>);', '&&', FOLDED("on the left of '&&'"))
v('folded-then-left', "perl folds the empty string away, and then warns: Value of <HANDLE> construct can be \"0\".", 'my $l;\nmy $x = "" || ($l = <STDIN>) || 2;', '||', FOLDED("on the left of '||'"))
# T522: chomp of an assignment is worth a count to perl, and nothing here.
v('chomp-assign-map-value', "perl gives 1, the characters chomp took (T522).", 'my @l = map { chomp(my $x = $_) } "a\\n";', 'chomp', "map's block ends in an expression, which is its value")
v('chomp-assign-sort-value', "perl sorts by what chomp took, 0 each time.", 'my @l = sort { chomp(my $x = $a) } 2, 1;', 'chomp', "sort's block ends in an expression, which is its value")


def write(first, table=None):
    n = first
    for name, why, body, at, message, nth in (T if table is None else table):
        program = f'# kind: refused\n# {why}\nuse v5.42;\n{body}\n'
        path = f't/{n}-io-{name}'
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
        import os
        for name, why, body, at, message, nth in T + REVIEW:
            try:
                r_ = subprocess.run([os.environ.get('CURLY_PERL', 'perl'), '-e', 'use v5.42;\n' + body], capture_output=True, text=True, timeout=10, input='')
            except subprocess.TimeoutExpired:
                print(f'{name}: no end in 10 seconds')
                continue
            print(f'{name}: exit {r_.returncode}; {r_.stdout!r}; {r_.stderr.strip()[:200]!r}')
    elif sys.argv[1] == '--review':
        write(int(sys.argv[2]), REVIEW)
    else:
        write(int(sys.argv[1]))
