# The independent review of step 21b

By a reader who did not build 21b, 2026-11-28, asked for a program the
compiler takes, that runs without a fault, and whose stdout, stderr,
exit status or files differ from perl 5.42's. `README.md` beside this
file is the builder's own review, which found three (T694 to T696).
**This one found three more, T697 to T699, one cause: perl takes a
handle before the rest of its statement is worked out.** Each is mended;
D287 is the reviewer's default, Stevan's to overturn.

## How

`reader/both.py` runs one program under perl and under the compiler,
each in a directory of its own, made fresh, holding the same files, with
the same stdin and environment, at most 256 open files, and a limit on
the processor's time and on what is written (T131). It compares stdout,
stderr, the exit status **and every file left in the directory**: the
builder's hunt did not look at the files, and T697 shows in a file.
`reader/drive.py` runs a file of cases through it. A fault or a refusal
is never a difference; a fault after stdout that perl does not have is
reported apart (`FAULT-AFTER-DIFFERENCE`). Every run is with a
collection at every allocation and poison, but those marked.

| File | What it holds |
|---|---|
| `reader/cases1.py` | Names of files: 42 names (a directory, a name that ends in a slash, one through a file, a newline in one, 300 and 5,000 characters, `-`, `&STDIN`, a pipe's spelling, undef, a number, a reference) under three modes and five programs; every write inside the run's own directory |
| `reader/cases2.py` | A handle as a value: opened again in place and its copies, in arrays, hashes, closures and subs, a `my` in every kind of loop, what `open`, `close` and `print` are worth, truth, `ref`, `==`, and every operator a reference faults under |
| `reader/cases3.py` | What a `die` exits with, and bytes: 56 programs, each with `use open` and without, over files of every byte, CR LF, NUL, a line of 100,000, a BOM, malformed and cut UTF-8, a noncharacter |
| `reader/cases4.py` | Step 21a's second reader's 2,275 cases of `<STDIN>` (where a list or a value is decided, the order of reads, loop tests, subs that give lines back), with a file's handle for stdin |
| `reader/cases5.py` | Programs by chance, by seed: opens in place, in blocks, in subs and closures, reads of every kind, stdin beside files, writes, closes, copies and drops, failed opens and `$!`, `try`, underflows, warnings, and seventeen ways to end |
| `reader/cases6.py` | What an uncaught `die` exits with after every sequence up to three long of eight things that touch a file or stdin, over three files (1,240), and 1,500 longer ones by chance from seventeen |
| `reader/cases7.py` | By hand: `eof`'s forms, a line assigned in every loop test, `<$fh>` in every place a value stands, the handle a message names (D279) in fifty arrangements, `$!` in strings beside what moves errno, numeric strings and what a `die` exits with after them, a statement over several lines, the handle before the list |
| `reader/cases8.py` | `open` and `close` as values and tests, where the handle's `my` is seen, `$!` beside a later `open` in every place a string stands, handles from subs and closures, `open`'s arguments in every shape |
| `reader/cases9.py` | `STDIN`, `STDOUT` and `STDERR` where a file's handle may stand; the braces of `print`; what may follow `print $fh `; what stands in angle brackets, and `<` as less-than hard against a variable |
| `reader/cases10.py` | What was found, as run: 35 programs |

About 300 more were run by hand through `both.py` to find where perl
frees, vivifies and warns.

## The numbers

10,292 programs in the cases files, each run once by perl and once by
the compiled program, and 762 of them again with no collection but
those the runtime asks for. As the tree stands after the mending:

| File | Programs | Same | Fault | Refused | WRONG |
|---|---|---|---|---|---|
| `cases1.py`, names | 560 | 447 | 113 | 0 | 0 |
| `cases2.py`, a handle as a value | 212 | 86 | 75 | 51 | 0 |
| `cases3.py`, exits and bytes | 112 | 84 | 28 | 0 | 0 |
| `cases4.py`, 21a's reader's cases | 2,275 | 503 | 1,356 | 416 | 0 |
| `cases5.py`, by chance (seeds 100 to 2,599, and 4,000 to 4,499; 3,000 to 3,599 without the stress knob) | 3,600 | 2,288 | 1,312 | 0 | 0 |
| `cases6.py`, errno (short, long) | 2,740 | 2,556 | 184 | 0 | 0 |
| `cases7.py`, by hand | 380 | 232 | 88 | 60 | 0 |
| `cases8.py`, `open` as a value, `$!` | 170 | 117 | 11 | 42 | 0 |
| `cases9.py`, the standard handles, braces, angle brackets | 208 | 93 | 24 | 91 | 0 |
| `cases10.py`, what was found | 35 | 12 | 2 | 21 | 0 |

**Before the mending**: `cases7.py` said WRONG of one program, the
first found (a `print` whose list assigns the handle's variable), and
`cases10.py`, written from it by hand, of 20 of its 35, with one more a
fault after writing what perl does not. The 2,500 random programs of
seeds 100 to 2,599 were run before the mending and found nothing: no
program by chance assigned a handle's variable inside the list written
to it. The three were found by asking what perl holds while it works
something else out, not by volume.

The driver's own mistakes, so that nobody chases them: two cases with
the same text once shared a directory (each run has its own now); and
`cases4.py` has two programs that never end under perl
(`while ($l .= <$fh>)`, T131), which the driver first let perl run for a
minute into gigabytes of memory, and now stops by the processor's time.
They show as `FAULT-AFTER-DIFFERENCE`, and are no difference.

## What was found

One cause, three faces. perl puts a handle on its stack, which counts
no references, and then works out the rest of the statement: the list of
a `print`, the name of an `open`. The compiler took the handle as a
value and kept it (T683), or took `open`'s handle after its name.

**T697, WRONG (a file, and stderr).**

    open(my $w, '>', 'o.txt') or die "no\n";
    sub drop() { $w = undef; return 's' }
    print $w drop(), "t";

perl: `o.txt` is empty, and stderr has `print() on unopened filehandle
at FILE line 3.` The compiler: `o.txt` holds `st`, stderr empty. `$w`
held the handle's only reference; the list dropped it; perl's handle was
freed in its hand. With a copy elsewhere (`my $c = $w;`) perl writes
`st`. So `say` and `printf`; so `print { $h{fh} } forget(), 't';` where
`forget` deletes the key, `print { $r->[0] } 'a', clear();` where `clear`
drops `$r`, and a closure that assigns `$w`. *Mended*: refused. What
gives the handle is named as an item of a list is (D76: a variable, an
element's array or hash, the head of a chain and what references reach),
and no item of the list may change it, itself or through a sub it calls.
A handle a call gives, `print { out() } ...`, is held by the call's
value and stays in. Tests: 6609 to 6614 (refused), 6632 (`same`: what a
list may do).

**T698, WRONG (stdout, stderr, the exit status).**

    open(my $o, '<', 'in.txt') or die "n\n";
    my $fh;
    sub f() { $fh = $o; return 'nonl.txt' }
    open($fh, '<', f()) or die "n\n";
    my $l = <$fh>; print $l; $l = <$o>; print $l;

perl: dies at the `open`, `Can't use an undefined value as filehandle
reference`, exit 25. The compiler: `x` and `y`, the two lines of
`nonl.txt`, exit 0: it worked the name out first, found `$o`'s handle in
`$fh`, and opened *that* again. perl had made a handle in `$fh` before
`f` ran, and `f` threw it away. The same with `open(my $fh, '<', g())`
where `g`, written below, assigns `$fh`; and where the name leaves the
variable undef while a copy lives, perl opens the copy's handle and
leaves `$fh` undef (three warnings on the next read). *Mended*: `open`
makes or takes its handle first, as perl does, and a name that can
change the variable is refused. Tests: 6615 to 6618.

**T699, WRONG (stdout).**

    my $fh;
    sub f() { return defined($fh) ? 'in.txt' : 'nonl.txt' }
    open($fh, '<', f()) or die "n\n";
    my $l = <$fh>; print $l;

perl: `a`, from `in.txt`. The compiler: `x`, from `nonl.txt`. By the
time the name is worked out the variable holds its handle: defined,
true, `ref` `GLOB`. So `open($fh, '<', $fh ? 'in.txt' : 'nonl.txt')`
with nothing called at all, a closure, and a `my` read by a sub below.
And `my $fh = 5; open($fh, '<', name());` where `name` prints: perl dies
of the `5` before `name` is called; the compiler printed what `name`
prints and then faulted. *Mended* by agreeing: the handle first. Tests:
6630 (`same`), 6631 (the fault, before the name).

Of `cases10.py`'s 35 programs the compiler as it was said WRONG of 20
and faulted after writing what perl does not of one; now 21 are
refused, 12 the same, 2 faults.

The builder's breakage "the path is worked out after the handle is
made" swapped the two to the order perl has, and was caught only because
the runtime took its arguments the other way round: no test asked which
came first. 6630 and 6631 do.

## What stood

- **D272, perl's errno.** Every sequence up to three long of a read, a
  read of every line, `eof`, an `open` that fails, one that works, a
  close and open again, a read of stdin and `eof(STDIN)`, over a file of
  lines, an empty one and one with no last newline: 1,240 programs,
  every exit status perl's. 1,500 longer ones with writes, closes,
  `try`, blocks that drop a handle: no difference. With `use open`, where
  perl's layers run Perl code as they read: no difference.
- **D273 and D284, `$!`.** Beside a later `open` in a list, a row of
  dots, a hash, a call's arguments, a `sort`'s block, a `for`'s list;
  after stdin's end, an underflow, forty numeric strings: the same or a
  fault. `my $why = $!;` copies perl's number with its words (`-$why`
  is `-2`, `$why + 0` is `2`): every place the number would show is a
  fault here, `not a numeric string`.
- **D276, a file open twice.** No path was found where a file is read
  back through a second handle while the first holds what it wrote. A
  dropped handle is closed by the collection the second `open` runs.
- **D279, the handle a message names.** Fifty arrangements by hand
  (closed, opened again, dropped, collected, an empty file, `eof` alone,
  stdin before and after) and the random programs: perl's text or a
  fault, never another text.
- **D278, perl's guess of a handle**, over what `cases9.py` adds to the
  builder's 2,036 programs: nothing.
- **21a's rules over a file's handle** (`cases4.py`): nothing; but 1,179
  of its 2,275 programs end at D279's fault, since 21a's reader counted
  lines with a `die` that has no newline, so that family says less than
  its size.
- **The files left behind** are perl's in every program that ran to its
  end, after `exit`, after an uncaught `die`.
- **256 open files.** A loop that opens 1,000 files and closes none runs
  as under perl; one that keeps every handle meets `Too many open files`
  at the same `open` as perl, the 254th, in this driver.

## Not WRONG, and worth knowing

- **A handle dropped at a brace is not closed until a collection sees
  it gone**, and a slot that still holds it keeps it: so
  `for my $i (1 .. 3) { open(my $fh, '>>', 'log.txt') or die; print $fh "$i\n"; }`
  is a fault at the second `open` (D276), because the `print` left the
  handle in a temporary; without the `print`, or in a sub called three
  times, it runs. `{ open(my $o, '>', 'f') ...; print $o ... }` and then
  `open(my $r, '<', 'f')` in the same function is the same fault. perl
  closes at the brace. It is loud, and a `close` mends it; it will be
  met.
- **Copying a file of UTF-8 without `use open`** faults at the first
  byte past ASCII written (D39, D280), where perl copies the bytes.
- **A list that only opens the handle again** (`print $w again(), "\n";`
  where `again` does `open($w, ...)`) is refused by T697's rule: an
  `open` is an assignment to its variable for every walk. perl writes to
  the new file.
- `print { $h[0] } 'a', ref(shift(@h));` is refused though perl prints:
  what `shift` gives back holds the handle.
- **T697's rule is blunt through a reference.** `print { $ctx->{out} }
  render($ctx, $item), "\n";` is refused when `render` stores through any
  reference at all (what references reach is one name, D109), though
  nothing drops the handle. `my $out = $ctx->{out};` first, and `print
  $out ...`, is in. A program that keeps its handle in a hash will meet
  this.

## What was run on the final tree

(2026-11-28, `JOBS=3 TIMEOUT=300`,
the machine shared) `make check`; `make test` (161 unit tests, 2,503
golden tests, the oracle over all of them, the census's check,
`DIFFERENCES.md`: `all: 0 failed`); `make golden-clang` (2,503 tests, 0
failed), which the builder had left unfinished; `make sanitize`, both
passes, poison on and off (2,503 tests, 0 failed, each), which the
builder had not run on the final tree; `make census` (1,349 SAME, 187
LOUD, 1,172 REFUSED, 4 UNJUDGED, no WRONG: nothing moved);
`claims.py` (1,579, the 20 that differ each a `roles` row with no roles
perl); `step21b-mutations.py` whole (118 of 119, the 119th the
builder's `open` worth `true`); the builder's `hunt.py` whole (3,453
programs, its README's counts again, nothing).

## What was not done

Nothing was run on a Mac. Nothing with a class (the branch was cut
before 17a). No file past 170,000 bytes. The tests are run as root, so
`Permission denied` was never met; a name through a file (`Not a
directory`), a directory to write (`Is a directory`), a name too long,
no such file and too many open files were. The driver gives perl and the
program the same open files as they start; `t/run.sh` and `t/checks.py`
were not checked for that, and a test that counts how many files open
before the system refuses would show a difference there. The step's
breakages were run again whole after the mending: 118 of 119 caught,
the 119th the one the builder had said nothing can see (`open` worth
`true` where perl's is `1`); five of the 119 are this review's, and one
of the builder's was rewritten (above).
