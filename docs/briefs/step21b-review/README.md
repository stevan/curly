# The review of step 21b

The builder's own, done as passes apart from the proposal and the
build: no second agent could be started in the session that built 21b
(its tools did not include one). Step 21a's builder said the same, and
a second reader then found six ways to be WRONG that the builder's pass
had not; so take this for what it is, and have 21b read by someone who
did not write it.

## What was run

`errno.py`: the one claim D272 rests on, that among everything the
language has only `open`, a read that meets the end of its input, and a
number that underflows (D151) change perl's errno. Every golden test
perl runs to its end is run again with `$! = 77;` after its pragmas, and
says what `$!` is as it ends. Of 295: 258 end with 77; 17 with 0, each
of which reads stdin to its end; 4 with 34 (ERANGE), each an underflow
D151 already faults an uncaught `die` after; 16 end by `exit`, which
says nothing. Rerun it whenever a step adds something that could move
errno.

`hunt.py`: programs by rule and by chance, each run by perl and by the
compiler in a directory of its own with the same files, and stdout,
stderr and the exit status each compared. A fault or a refusal is never
a difference.

| Family | Programs | Same | Fault | Refused | WRONG |
|---|---|---|---|---|---|
| `contexts`: 21a's 74 places a readline stands, with `<$fh>`, under four files, with `use open` and without | 438 | 371 | 37 | 30 | 0 |
| `values`: a handle in every place a value stands | 65 | 25 | 37 | 3 | 0 |
| `print`: what follows `print $x ` and `say $x `, for a handle and for a number; the braces | 311 | 130 | 104 | 77 | 0 |
| `errno`: `$!`, and what a `die` exits with, after each thing that moves perl's errno, alone and in pairs | 494 | 224 | 270 | 0 | 0 |
| `bytes`: ten files of bytes under eight programs, with `use open` and without | 160 | 91 | 69 | 0 | 0 |
| `random`: sequences of opens, reads, writes, closes, copies, messages and deaths, by seed | 260 | 120 | 140 | 0 | 0 |

(The `errno` and `values` rows are from before D284, which refuses some
of what they then ran: their programs that read `$!` outside a string
are refusals now.) 1,728 programs, and the hunt found nothing.

## What was found, and how

Both by reading what perl says of `open` and of `$!` against what was
built, and asking of each argument what a value of the language loses
that perl's has; each then confirmed with perl (`claims21.py`, T694 and
T695).

**T694, WRONG (stdout).** `my @n = ("in.txt"); open(my $fh, "<", @n) or
die "no\n"; print scalar(<$fh>);` perl: `a`, the file's first line. The
compiler: `no`. What follows `open`'s mode is a list, to perl; the
compiler took the array for its count and tried to open a file called
`1`. So `open($fh, "<", <STDIN>)`, which reads every line. *Mended*: a
name that is a list by how it is written is refused (D285); 6592 to
6596.

**T695, WRONG (stdout).** `open(my $n, "<", "nope"); say $!, g();`
where `g` opens a directory to write. perl: `Is a directory|`. The
compiler: `No such file or directory|`. `$!` is perl's own variable,
read when the operator it is an operand of runs: after the rest of a
list, of a row of dots, of a key. A sum that underflows in between
changes it too. *Mended*: `$!` stands in a string, which is made where
it stands, or alone on the right of `=` to a scalar variable, and is
refused anywhere else (D284); 6597 to 6603.

## Not WRONG, and written down

- **The file a program writes is the same at its end**, but a program
  whose stdout is redirected to a file it also opens is outside what
  D276 looks at (it knows the handles the program opened).
- **A `die` with no newline while a file is being read is a fault**
  (D279), in every program that checks its input line by line and dies
  of a bad one. It is the strictest thing 21b does, and the one most
  likely to be met.
- **A handle dropped and its file read back in the same block** is a
  fault where the dropped handle is still in a slot the collector sees
  (a `my` in a block of the same function that has ended): perl closed
  it at the brace. From a sub that has returned it is closed.
- **`scalar(<$fh>)`** is refused, as `scalar(<STDIN>)` is (21a).

## What was not done

No second reader. The hunt's programs are short, and none uses a class
(the branch was cut before step 17a). `%e`-style formats to a handle and
files larger than a megabyte were not tried. Nothing was run on a Mac:
errno's numbers there are the same for the errors met here (2, 21, 25),
but `isatty` on a plain file leaving ENOTTY is what the runtime asks the
system, not what it assumes.
