# The reviews of step 21a

Two. The first is the builder's own (`contexts.py`, `first-run.txt`,
`second-run.txt`; `docs/PLAN.md`, step 21, "What the review found"): no
second agent could be started in the session that built 21a. It found
T516.

The second is this file's: a reader who did not write 21a, 2026-11-28,
asked for a program the compiler takes, that runs without a fault, and
writes to stdout or stderr, or exits with, what perl 5.42 does not.
**It found six**, T517 to T522 in `docs/TRAPS.md`, each mended; D222 and
D223 are the reviewer's defaults, Stevan's to overturn.

## How

`reader/drive.py` runs each case of a cases file under perl and under
the compiler, both given the same stdin, arguments and environment, and
compares stdout, stderr and the exit status, each apart. A fault or a
refusal is never a difference; a warning of perl's that the compiled
program does not fault for is one, since stderr differs (D15).

| File | What it holds |
|---|---|
| `reader/cases1.py` | `<STDIN>` where a list or one value is decided: constructors, slices, calls, `return`, `\|\|`, `? :`, closures; `chomp(my $x = EXPR)` of every kind |
| `reader/cases2.py` | `, <STDIN> line N.` on `die` and `warn` (T516), and `eof(STDIN)` |
| `reader/cases3.py` | Input: 83 inputs (empty, no last newline, `\r\n`, NUL, a line of 70,000 bytes, bytes past ASCII, every malformed shape of UTF-8, a BOM, a character cut at the end and in the middle) under five programs, with `use open` and without |
| `reader/cases4.py` | `exit`: its values, its precedence, where it leaves from |
| `reader/cases5.py` | `@ARGV` and `%ENV`: every operation, references to them, the read-only bit through a reference, bytes |
| `reader/cases6.py` | `STDOUT` and `STDERR` after `say`, `print` and `printf`, and the word elsewhere |
| `reader/cases7.py` | Order: an element assigned a line (D213), two reads in one expression, a read beside a sub that reads; a sub that gives lines back, in every place a call stands |
| `reader/cases8.py` | A constant beside a line read, and a line assigned in every shape of loop test |
| `reader/cases9.py` | T516 again, in subs, `try`, closures; `chomp` of an assignment, more |
| `reader/cases10.py` | After the mending: a sub that gives a readline back, 24 shapes of what it gives by four ways of giving by eleven ways of calling it |

Some 250 more programs were run by hand to find where perl warns, folds
and tests with `defined`; the ones that matter are rows of
`briefs/claims21.py` (T517 to T522, 42 rows).

## The numbers

3,829 runs of about 2,400 programs. **Before the mending** the driver
said WRONG of 127 runs, three of them its own mistakes (below); **after
it**: 2,572 the same, 621 faults, 634 refusals, no WRONG, and 2 that did
not end in 30 seconds under the stress knob (`cases3.py`, a line of
70,000 bytes taken apart a character at a time: slow, not wrong).

The driver's own mistakes, so that nobody chases them: it first gave
the compiled program the collector's knobs and perl not, so `keys %ENV`
differed by three (the harness gives both the same, D220); and two
threads once wrote one program's file at the same time, and perl read it
empty.

## What it found

Each is in `docs/TRAPS.md` with perl's answer, and a row of `claims21.py`.

**T517, WRONG (stderr).** `exit - 1;` with any stdin.
perl: exits 255, stderr `Warning: Use of "exit" without parentheses is
ambiguous at FILE line 2.` The compiler: exits 255, stderr empty. So
`exit-1;` and `exit + 1;`. It is T94, which `length - 5` has been
refused for since step 3: `exit`'s argument is a named unary operator's.
*Mended*: T94's rule in the lexer takes `exit` too. Refused: 4851 to 4853.

**T518, WRONG (stderr).** `if (my $l = <STDIN>) { print $l }`, stdin
`a\n`. perl: `a`, and stderr `Value of <HANDLE> construct can be "0";
test with defined() at FILE line 2.` The compiler: `a`, stderr empty.
perl warns wherever a line assigned is the left operand of `&&` or
`||`, which is what an `if` or `unless` with nothing after its block
is, a modifier too; it says nothing of an `if` with an `else` or an
`elsif`, of an `elsif`'s own test, of the test of `? :`, under `!`, on
the right of `&&`, or before `//`. `LANGUAGE.md` gave `if (my $l =
<STDIN>)` as its example of a line tested for truth "as in perl".
*Mended*: refused where perl warns, and before `//` (D222). Refused:
4854 to 4864. Where perl is silent it stays in: 4892, a `same` test.

**T519, WRONG (stdout).** `my %h; $h{<STDIN>} = 1 ? <STDIN> : 2; print
%h;`, stdin `a\nb\n`. perl: `a\nb\n` (key `a`). The compiler: `b\na\n`
(key `b`). perl folds the constant test away as it compiles; what is
left is T508-order's assignment, which works the element out first, and
D213's check looked only for a readline written there. The same with `1
&& <STDIN>`, `"" || <STDIN>`, `2 > 1 ? ... : ...`, `length("a") ? ...`.
*Mended*: a line read, or `=` of one, as the operand a constant test
leaves is refused (D222; "constant" is D53's `folds`). Refused: 4865 to
4867, 4872.

**T520, WRONG (stdout).** `my $l; while (1 && ($l = <STDIN>)) { print
"[$l]" }`, stdin `a\n0`. perl: `[a\n][0]`. The compiler: `[a\n]`. The
constant folded away, the test is T501's, and perl tests it with
`defined`. So `while (1 ? <STDIN> : 0)` (perl's `$_`), `for (; 1 && ($l
= <STDIN>);)`, and `... while !0 && ($l = <STDIN>);`, the last two being
shapes D212 refuses when they are written plainly. *Mended*: T519's
refusal. Refused: 4868 to 4871.

**T521, WRONG (stdout).** `sub f() { return <STDIN> } f(); print
<STDIN>;`, stdin `a\nb\nc\n`. perl: `b\nc\n`. The compiler: nothing: it
read every line in `f`. perl hands "nothing wanted" on to what a sub
called for nothing gives back, and a readline there reads one line: one
for `(<STDIN>, 1)`, two for `(<STDIN>, <STDIN>)`, one for `(<STDIN>) x
2`, through `? :`, `||`, a last statement and a call handed on; a slice
of a list, `sort` and `[ ]` read all whatever is wanted. *Mended* by
agreeing: the list a sub gives back is built `given`, and an item of it
that takes its context from where it stands reads one line, or is called
for nothing, when the sub was (`codegen.ts`, `addItem`). `same` test:
4890, which shows the count of lines after each call in a caught
`die`'s message.

**T522, WRONG (stdout).** `sub f() { chomp(my $x = <STDIN>) } say
f();`, stdin `a\n`. perl: `1`. The compiler: `a`. And `map {
chomp(my $x = $_) } LIST`, perl `1 1 ...`, the compiler the chomped
strings. D219 made the statement an assignment so that its `my` is the
block's, and an assignment is a value where a sub or a block ends.
*Mended*: it has no value, as `chomp($x);` has none (D130): a fault when
a call uses it, refused as the value of a `map`'s, `grep`'s or `sort`'s
block. Tests: 4873, 4874 (refused), 4880, 4881 (faults), 4891 (`same`:
called for nothing).

## Notes: not WRONG

- **The two streams in one pipe.** `say "a"; die "d\n";` with `2>&1`:
  perl writes `d` and then `a` (stdout is held in its buffer; to a
  terminal it goes at each newline), a compiled program `a` and then
  `d`: it writes what it has for stdout before anything it writes to
  stderr. Each stream alone is perl's, and the tests compare them apart
  (D149). `LANGUAGE.md`, "warn, and stderr", says so now.
- **`PATH` was the machine's** for perl and for the program (D220): a
  `same` test that printed `$ENV{PATH}` passed every check on the
  machine that wrote its `.expected`, and would fail on the next. It is
  `/usr/bin:/bin` for both now (D223), with a fixture,
  `t/checks/same-env-path`. No such test existed.
- **Stricter than it has to be**: `($l = <STDIN>) // "f"` is refused
  with `&&` and `||`, where perl is silent (D222); every line read
  beside a constant test is refused, `my @l = (0 || <STDIN>);` too,
  which had been the same as perl; `$s .= <STDIN>` at the end of the
  input is D48's fault where perl appends nothing in silence (the
  builder's, and safe); `my $l = f();` of a sub that gives `<STDIN>`
  back is D18's fault where perl reads one line.
- **`exit` in a `sort`'s block, a `foreach`, a `try`, a sub among a
  list's items**: all perl's. `exit` of every number tried (to 2^64 and
  past, negative, a Num, a string) is perl's or a fault.
- **Malformed UTF-8**: of 83 inputs under five programs with `use
  open`, every one perl warns of faults, and every one that runs to the
  end is perl's, the BOM and U+10FFFD among them.
- **`%ENV` through a reference**: `$r->{X} = 1`, `delete $r->{X}`,
  `$r->%* = ()`, `$r->@{...} = ...`, `$r->{X}++`, `$r->{N}{a} = 1` and
  a store in a sub handed `\%ENV` are each `%ENV is read-only`.

## What was not done

`contexts.py` was not run again after the mending (a thousand compiles
on a machine with a load of 39): `second-run.txt` is the builder's run,
and some of its programs are refused now (`if (my $l = <STDIN>) { ... }`
with no `else`, and the constant tests). `step21-mutations.py` was not
extended: each mend's tests were seen red before it (the driver's WRONG
for each is what they were written from). Files, 21b and 21c, are not
looked at: they are not built.
