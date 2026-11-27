# Step 22's adversarial review: what was found

Reviewer: Opus 5.5, 2026-11-27. I did not write the proposal. I read `PLAN.md`,
"### 22. Numbers and time", `briefs/claims22.py`, D35, D36, D40, D45, D48,
D112, D127, D131, D151 and T79, T92, T103. Every perl output below comes from
`/opt/perl-5.42/bin/perl` and is pasted as printed. Each program is run as
`use v5.42;` followed by the line shown.

The worktree already holds an uncommitted, partial build of step 22. I judged
the proposal by its text. Where it helped, I also ran that build (read-only,
through `bin/curlyc.ts`) and say what it printed, marked "build". The build is
not what was under review.

Summary: **one WRONG in the text** (finding 2, `abs` of a string with a point;
the partial build already avoids it), **one place where perl warns and the
proposal is silent** (finding 1, which the build has too), one false statement
about the evidence (finding 3), one ambiguity an obvious build gets wrong
(finding 4), and some notes. Nothing else I tried differs from perl. The
"tried and agreed" list is at the end.

---

## 1. WARNS: `&`, `|`, `^` with a numeric comparison as an operand

The proposal says: "`6 & 3 == 3` is perl's `6 & (3 == 3)`, 0, with perl's
precedence and **in silence**, as perl has it (T486)." That holds only because
both of T486's comparisons are constants: perl folds `3 == 3` before `ck_bitop`
looks. With a variable, perl warns:

```
my $y = 3; say 6 & $y == 3; say 6 & 3 == 3; my $z=6; say $z | $y < 3; say $z ^ $y <=> 1;
```
```
Possible precedence problem on bitwise & operator at ... line 2.
Possible precedence problem on bitwise | operator at ... line 2.
Possible precedence problem on bitwise ^ operator at ... line 2.
0
0
6
7
```

The comparison on the left warns too. The string comparisons, brackets and
`!` do not:

```
my $y = 3; say $y == 3 & 6; say $y eq 3 & 6; say 6 & $y lt 3; say 6 & ($y == 3); say 6 & !($y == 3); say 6 & -($y <=> 1);
```
```
Possible precedence problem on bitwise & operator at ... line 2.
0
0
0
0
0
6
```

- The proposal: runs in silence (D15 broken). Build: `my $y = 3; say 6 & $y == 3;` prints `0`, exit 0.
- `$x & $y == 0` is the classic bug this warning exists for, so programs will
  hit it.
- **Way out: refuse** an unbracketed numeric comparison (`== != < > <= >=
  <=>`) as either operand of `&`, `|` or `^`, the way T115 refuses `!`. Refuse
  it with constants too: that is stricter than perl, but simpler than
  modelling the fold. The assigning forms (`$x &= $y == 3`) do not warn, since
  perl skips `OPf_STACKED`, and can stay in. Correct T486's "in silence" and
  add a claims row with a variable.

## 2. WRONG as written: `abs` of a string with a point

The text says `abs` gives "an integral Num's (whole, below 2^53) the Int", and
that a string is read by D40 first. D40 makes `"1000000000000000.0"` a soft Num
1e15, which is whole and below 2^53, so by the text `abs` gives the Int and
prints `1000000000000000`. perl does not.

For a string with a point, `sv_2iv` sets only `IOKp`, never `IOK`. So `pp_abs`
takes its NV branch and gives a float. Once the string has been used as a
float, it gives an integer. **Two answers**, and the fresh one is the float:

```
for pre in '' 'my $t = $s + 1;' 'my $t = $s + 0.5;' 'my $t = $s | 0;' 'my $t = int($s);' 'my $t = $s * 1.0;' 'my $t = sqrt($s);' 'my $t = $s == 1;'
my $s = "1000000000000000.0"; PRE say abs($s); say int($s); say -$s;
```
```
(none)              : 1e+15 1000000000000000 -1e+15
my $t = $s + 1;     : 1e+15 1000000000000000 -1e+15
my $t = $s + 0.5;   : 1000000000000000 1000000000000000 -1000000000000000
my $t = $s | 0;     : 1e+15 1000000000000000 -1e+15
my $t = int($s);    : 1e+15 1000000000000000 -1e+15
my $t = $s * 1.0;   : 1e+15 1000000000000000 -1e+15
my $t = sqrt($s);   : 1000000000000000 1000000000000000 -1000000000000000
```

Note that `sqrt`, new at this step, is one of the uses that gives the string
its float past.

The same thing shows through the sign of a zero, with no printing involved:

```
say atan2(0, -abs("0.0"));
```
```
3.14159265358979
```

perl's `abs("0.0")` is the NV 0, and negated it is -0.0. By the text, `abs`
gives the Int 0, negated it is 0, and `atan2(0, 0)` prints `0`: **WRONG**.

- `int` is not affected: `pp_int`'s NV branch gives an integer (`SETu`/`SETi`),
  so `int("1000000000000000.0")` is `1000000000000000` whatever the past. It
  is also one answer at `"9007199254740993.0"` (`9007199254740992` after every
  past I tried).
- Build: it already gives a Num here. `say abs("1000000000000000.0");` faults
  with D36's message, and `say atan2(0, -abs("0.0"));` faults with "a negative
  zero to atan2". So the build is right and the text is not.
- **Way out: agree with perl's fresh answer and let the existing faults catch
  the past.** `abs` of a string that D40 reads as a point (soft) Num gives the
  Num, so D36 and T79/D202 apply. Say so in 22a, and add both programs above as
  fault tests: the 1e15 window, and `-abs("0.0")` into `atan2`.

## 3. False statement: the hex/oct evidence file does not exist

Q4 says the grammar was "held to perl by a search over every string of up to
four characters from a 21-letter alphabet (204,205 strings, nothing differs,
`briefs/step22-hexoct.py`)". There is no such file in the tree, committed or
not.

I wrote my own check of the text's rule, as I read it:

- hex: `(0[xX]|[xX])?` and then `(_?H(_?H)*)?`.
- oct: the six blanks, and then one of `0?[xX]` with hex digits, `0?[bB]` with
  binary ones, `0?[oO]` with octal ones, or octal ones alone, each with the
  same `_` rule.
- In both, the value must be at most 0xFFFFFFFF.

It ran over every string of up to four characters from
`0 1 7 8 9 a f F g x X b B o O _ space \t \n + - .`. perl ran the strings in
one program, with `$SIG{__WARN__}` noting each warning:

```
245411 strings; 22683 accepted by the text; 0 differ
```

So the rule is sound. **The file the proposal cites still has to be committed.**
The script is short:

```python
import itertools, re, subprocess, json
alpha = list("017f9gxXbBoO_ \t\n+-.") + ['8','a','F']
strs = [''.join(p) for n in range(0,5) for p in itertools.product(alpha, repeat=n)]
H='[0-9a-fA-F]'; O='[0-7]'; B='[01]'
def dig(D): return f'(?:_?{D}(?:_?{D})*)?'
hexre = re.compile(rf'(?:0[xX]|[xX])?{dig(H)}\Z')
octre = re.compile(rf'[ \t\n\r\f\v]*(?:0?[xX]{dig(H)}|0?[bB]{dig(B)}|0?[oO]{dig(O)}|{dig(O)})\Z')
def val(s, f):
    t = s.lstrip(' \t\n\r\f\v').replace('_','')
    if f=='hex':
        t = re.sub(r'^0?[xX]','',t); return int(t,16) if t else 0
    m = re.match(r'^0?([xXbBoO])(.*)$', t)
    base, r = ({'x':16,'b':2,'o':8}[m.group(1).lower()], m.group(2)) if m else (8, t)
    return int(r, base) if r else 0
open('strs.json','w').write(json.dumps(strs))
perl = r'''use v5.42; use JSON::PP; my $w; local $SIG{__WARN__} = sub { $w = 1 };
open my $fh, '<', 'strs.json'; local $/; my $a = decode_json(<$fh>);
for my $s (@$a) { for my $f ('hex','oct') { $w = 0; my $v = $f eq 'hex' ? hex($s) : oct($s);
  print "$f\t", ($w ? "W" : "S"), "\t$v\n"; } }'''
out = subprocess.run(['/opt/perl-5.42/bin/perl','-e',perl],capture_output=True,text=True).stdout.splitlines()
bad = acc = 0
for i, s in enumerate(strs):
    for j, (f, rx) in enumerate((('hex',hexre),('oct',octre))):
        _, st, v = out[2*i+j].split('\t')
        if rx.match(s):
            acc += 1
            if st != 'S' or int(v) != val(s, f): bad += 1; print('DIFF', f, repr(s), st, v)
print(len(strs), 'strings;', acc, 'accepted by the text;', bad, 'differ')
```

Some corners the text should spell out, because a builder will guess at them:

- A trailing `_` in octal is silent in perl, but not in binary:
  - `say oct("07_");` prints `7`, no warning.
  - `say oct("0b1_");` prints `Illegal binary digit '_' ignored` and `1`.

  Both are faults under the text, which is right.
- `oct("_7")`, `oct("0_7")`, `oct("o_7")` and `oct("b_1")` are all silent
  (`7 7 7 1`), and the text accepts them.
- "Blanks" means D40's six ASCII ones, and nothing more:
  - `say oct("\t\f\r\x0b7");` prints `7`.
  - `say oct("\x{a0}7");` and `say oct("\x{85}7");` print `0` in silence.

  A builder who reaches for a Unicode whitespace test would print `7` for
  those: WRONG. Name the six. The build faults, which is right.

## 4. Ambiguity: `srand`'s value is "N"

22c says: "its value is N, or the string `0 but true` for 0". But perl's value
is the unsigned integer `grok_number` read from N's string, not N itself:

```
say srand("042"); say srand("00"); say srand("9223372036854775807"); say srand("18446744073709551615"); say srand("18446744073709551616"); say srand(9223372036854775807); my $v = srand(5); say $v + 1; say srand(1e14); say srand(999999999999999.0);
```
```
Integer overflow in srand at ... line 2.
42
0 but true
9223372036854775807
18446744073709551615
18446744073709551615
9223372036854775807
6
100000000000000
999999999999999
```

- A build that hands back its argument prints `042` for `srand("042")`:
  **WRONG**. The build prints `42`, which is right.
- "A string of digits alone" says nothing about digits past 2^63 - 1.
  - `srand("18446744073709551615")` is silent in perl, and its value is an
    unsigned integer the language does not have.
  - `"18446744073709551616"` warns.
- **Way out:**
  - The value is the Int that the digits are, or the Int that the whole Num
    is. For zero it is `0 but true`.
  - A string of digits whose number is 2^63 or more is a fault, which D40's
    `integer overflow` already gives if the string is read by D40's digit
    rule.
  - Write it that way, and add `srand("042")` to the tests.

## 5. Loud, but it will be met: every `~` of a value of 0 or more faults

`~$x` is 2^63 or more for every `$x >= 0`, so the idiom `$flags & ~$mask`
always faults:

```
say ~int 1.5 & 7;
```
```
6
```

Build: `fault: a bitwise answer of 2^63 or more: perl's is an unsigned integer,
which the language does not have`.

This is loud, so it is not a WRONG. But "every answer below agrees" hides the
fact that `~` is only usable on negative numbers. Two ways to handle it:

- **Record it** in `DIFFERENCES.md` as met often, which I recommend.
- Or take `A & ~B` in as one operation: and-not, whose answer is below 2^63
  whenever A is 0 or more.

The proposal's `DIFFERENCES.md` line names "`~0` and any unsigned answer a
fault". It should say plainly that this covers `~` of any number that is not
negative, and `& ~MASK`.

## 6. Note: `&.5`, `|.5`, `^.5`, `~.5` are perl's string operators

perl takes the longest token, so a dot hard after the operator makes it
stringwise:

```
say 6 &.5;      # 4
say 7 |.5;      # 7
say 1 ^.5;      # (an empty-looking line: "1" ^. "5" is "\x04")
say ~.5;        # one byte, ~."5"
```

A lexer that takes `&` and then the number `.5` prints `0` for the first one:
**WRONG**. The build refuses all four (`'&.' is not in the language yet`),
which is right. Two things to fix around that:

- The proposal says these stay **Cut** (T46), but the build's message says
  "yet". Make the message say they are cut.
- Add refusal tests written with no blank (`6 &.5`, `~.5`). The refusal is
  only safe while the longest-token rule stays.

## 7. Note: D151 and errno

These leave errno alone in perl: `srand()`, an unseeded `rand()`, `time`,
`hex("ffffffff")`, and `sin` or `sqrt` of a subnormal made by division. A
`die "x\n"` after each exits `255`.

On glibc, `atan2` with a subnormal answer and `sin` of a subnormal argument do
not set errno. `exp(-745.2)` does (34). Over 400,000 arguments next to the
point where `exp`'s answer drops below DBL_MIN, I found none where glibc sets
ERANGE and the answer is still normal.

So "a result that underflowed, or that set errno" covers perl on this machine.
Two requirements for the runtime:

- **Clear errno before each libm call and read it right after.** A stale errno
  from somewhere else would only add faults (loud), but nobody could explain
  them.
- Macs: macOS's libm never sets errno, so the check for a subnormal answer, or
  a zero from a nonzero argument, is the one that does the work there.

## 8. Note: a shift by -2^63

T476 has `1 << -9223372036854775808` as `0`. "A negative count shifts the
other way" invites `-count` on an `int64_t`, which is undefined for INT64_MIN.
`make sanitize` would catch it, but only if there is a golden test for it. Make
sure there is one.

## 9. Note: the file-handle guess and `atan2`

The text extends the guess "after `say` or `print`". perl applies it after
`atan2(` as well, as after `substr(`:

```
my $x = 3; say atan2($x -1, 1);
```
```
Missing comma after first argument to atan2 function ... (compile error, exit 255)
```
```
my $x = 3; say atan2($x <<1, 1);
```
```
Can't find string terminator "1" anywhere before EOF ... (exit 255)
```

The build refuses both, and `~1` too. The named unary operators (`int($x
-1)`, `hex($x -1)`, `rand`, `srand`, `abs($x <<1)`) are not list operators,
and perl reads them as arithmetic (`2`, `2`, `1`, `2`, `6`), as the build
does. Say in 22b that `atan2(` joins `substr(` and `index(`, and add a test.

---

## Tried and agreed

All of these were run under perl. Where I ran the build too, it agreed or
refused.

- **The assigning forms are the variable, read late**:
  - `my $x = 0; say(($x |= 1) + ($x |= 2));` prints `6`.
  - `my $x = 1; say(($x <<= 1) + ($x <<= 1));` prints `8`.
  - `my $x = 1; say $x + ($x <<= 3);` prints `16`.
  - `my $x = 1; say $x . ($x |= 6);` prints `77`, and D57 refuses it.
- **Named unary precedence**:
  - `sqrt (4) * 9` is `18`, `int (7.5) / 2` is `3.5`, `2 ** int 3.5` is `8`.
  - `-int 3.5 ** 2` is `-12`, `1 << 2 ** 2` is `16`, `int 3.9 <=> 3` is `0`.
  - `sort int @a` is `sort(int(@a))`, which prints `3`.
  - `map { hex } @a` is refused, since with no argument it is `$_`.
- **`rand` and `time`**:
  - `say rand -1;` is silent and negative, `say rand +1;` is silent,
    `say rand, 1;` is fine.
  - `say time -1 > 0` is fine, `say time <<1` is a shift,
    `time x 0 eq ""` works.
  - `$h{time}` is the key `time`.
- **The sequence of `rand` under perl's merge**: `reverse sort { int(rand(3))
  - 1 } 1 .. 12`, in-place `@c = reverse sort {...} @c`, and `map { int rand 6
  }` all print what perl prints over three seeds.
- **Negative zero**:
  - `-$x` for `$x = 0.0` goes through `sqrt`, `sin`, `int`, `abs`, `hex`,
    `oct`, `srand` (`0 but true`) and `"" .`, printing `0` in both.
  - `abs("-0.0")`, `abs(" -0.0 ")`, `abs("-0e0")`, `int("-0.0")`,
    `-int(0.0)`, `-abs(0.0)` and `-int(±0.5)` into `atan2` all give `0` in
    perl, consistent with the text.
  - I found no path where the text gives +0 and perl gives -0.0, other than
    finding 2.
- **The past**:
  - `int` of a string with a point always takes the NV: `"9007199254740993.0"`
    and `"123456789012345678.0"` give one answer after `+ 0.5`, `| 0` and
    `+ 1`.
  - Every other window is D36's, D45's or T79's, and already faults.
- **Folding**: `if ($x = E)` warns `Found = in conditional` in perl, and the
  build refuses it, for E = `sqrt(4)`, `~-1`, `-abs(3)`, `int(3)+1`,
  `atan2(1,1)`, `oct "7"`, `2 ^ 3`, `exp 0`, `cos 0`, `hex("ff") >> 1`,
  `log(1)+1` and `abs(-1.5)`.
- **The file-handle guess**: `say $x &int(3);`, `say $x &abs(3);`,
  `say $x &true;`, `say $x &time;` and `print $x &hex("3")` all die in perl
  (`Can't use string ("6") as a symbol ref`). The existing rule, "`&` hard
  against a name", covers them. `say $x ?2:3` is a ternary in 5.42, and agrees.
- **Longest tokens**: `=~`, `!~` and `^^=` are refused as longest tokens,
  `! ~$x` is `1` in both, and `2**63 >> 1` faults, where perl prints
  `4611686018427387904`.
