# The roles perl

perl 5.42.0 with Stevan's roles: the referee for a program with a role
in it (D181), his branch ported to 5.42.0 (D186). Every other program
is refereed by perl 5.42.0 alone (D10). `docs/PLAN.md`, step 17, "The
port, as built", has the account in brief; this file has all of it.

| File | |
|---|---|
| `roles-5.42.0.patch` | The patch, `patch -p1` from the top of perl-5.42.0's source |
| `build.sh` | Fetches perl-5.42.0.tar.gz (or takes `TARBALL`), checks its sha256, patches, builds, installs to `PREFIX` (default `/opt/perl-5.42-roles`), and checks the perl it installed has roles |
| `lib/Devel/PatchPerl/Plugin/CurlyRoles.pm` | The same patch as a `Devel::PatchPerl` plugin, for perlbrew and plenv |

## Building it

```
tools/perl-roles/build.sh                     # into /opt/perl-5.42-roles
tools/perl-roles/build.sh $HOME/perl-roles    # anywhere
```

About three minutes on four cores. With perlbrew (plenv's `perl-build`
reads the same variables):

```
PERL5LIB=$PWD/tools/perl-roles/lib PERL5_PATCHPERL_PLUGIN=CurlyRoles \
    perlbrew install perl-5.42.0 --as perl-5.42.0-roles
```

### Is it the roles perl?

`Devel::PatchPerl` only warns when a plugin dies, so a patch that
failed leaves a plain 5.42.0 under the roles name. Ask it:

```
perl -e 'use v5.42; use experimental "class";
    role R { method m { "roles" } } class C :does(R) { }
    print C->new->m, "\n"'
```

`roles`, or a syntax error from a perl that has none. `build.sh` asks
this itself and fails if the answer is wrong.

## What the patch is

From `stevan/perl5`, branch `slittle/roles-v3-pr` at `1446b62`
(2026-03-26), put on perl's own `v5.42.0` (`5551b97c`) in four
layers. The branch was cut from blead at 5.43.10, and its roles code
stands on blead's rework of classes since 5.42.0, so the roles commits
alone do not build on 5.42.0.

**1. Blead's class layer.** The 32 commits from `v5.42.0` to the
branch's base (`85ae2b2`) that touch `class.c`, `class.h`, `pad.c`
or `pad.h`, in order, but:

- six tree-wide cleanups taken for those four files alone, so that
  the commits after them apply: `801f8b89` (ARGS_ASSERT calls),
  `64ad8fb7` (no `STATIC`), `d129aa1c` (function headings),
  `b5004d8d` and `1c44630c` (ARGS_ASSERTs); `6f673187` (`apidoc_flag`
  lines) was taken the same way and then reverted, since 5.42.0's
  `autodoc.pl` refuses its lines;
- `cb60726e` skipped: it respells the constructor's `Unrecognised
  parameters` as `Unrecognized`, and 5.42.0's spelling is the one
  Curly is held to;
- in `3ed2439b` (`SAVEt_PADSV`) and `6c8256cc` (`padalloc_NO_SV`),
  `regen/embed.pl`'s list of visibility overrides left out, which
  5.42.0 does not have.

What this layer is made of: a method's `$self` processed as a
signature parameter (`b1f152e4`), accessors built through the
signature functions (`0b0c8732`), `OPpSELF_IN_PAD`, `SAVEt_PADSV`, no
pad SV for a field (`1c7eedee`), and the bug fixes on the way.

**2. Blead's signature functions**, which layer 1 calls, for `op.c`,
`embed.fnc` and `perly.y` alone: `c20e0454` (fields of the parser's
signature renamed), `4b060dfa` (`subsignature_append_fence_op`),
`0aba7db8` (the `subsignature_append_*` functions take pad offsets).
**Not `3c2e3561`** (`OP_MULTIPARAM`), which runs every signature by
new code: Curly holds signatures to 5.42 closely (T144), and nothing
here needs it.

**3. The roles**, Stevan's eleven commits: `1dec215` (roles v3),
`941c6f2`, `143162d`, `ec4cee5`, `99d1c12`, `35c1b48`, `8f6282f`,
`eceeac3`, `31cabac`, `40f5f64`, `80cb7dc`. Not `973224d`, which
follows a macro blead renamed after 5.42.0, nor `1446b62`, which
bumps `Module::CoreList` for blead.

**4. The port's own mending**:

- `perly.y`: blead had made each statement a rule of its own; the
  two `role` rules are written in 5.42.0's `barestmt`, as its `class`
  rules are (`subattrlist`, `package_version`, a block as a loop that
  runs once);
- `toke.c`: `force_word(s,BAREWORD,FALSE,TRUE)` for `role`, as
  5.42.0 calls it for `class`;
- `op.c`: two hunks of blead's that came in with the roles commit
  itself (`1dec215` was made on a newer blead than its parent) put
  back as 5.42.0 has them: `a762010`'s "will become fatal in Perl
  5.46" (5.42.0 says 5.44; `lib/warnings.t` and `lib/feature.t`
  caught it) and `3364ec3`'s fix to `find_lexical_cv`. Every other
  hunk of `1dec215` was read and is the roles';
- `lib/B/Deparse.pm`: its version stays 1.85;
- `t/role/role_compose.t`: `is(join(...))` for `is_deeply`, which no
  `t/test.pl` has, and `lib/B/Deparse-core.t`: `role` and `does`
  among the keywords it does not test, as `class` is. **Both fail on
  the branch too.**

The generated files are made again: `regen.pl` (`embed.h`,
`proto.h`, `opcode.h`, `opnames.h`, `pp_proto.h`,
`lib/B/Op_private.pm`), `regen_perly.pl` with bison 3.8.2
(`perly.act`, `perly.h`, `perly.tab`), and `regen/keywords.pl` with
`Devel::Tokenizer::C` 0.11 (`keywords.c`, `keywords.h`).

## How it was checked

- The branch's `t/role/` (10 files, 233 tests) and perl's `t/class/`:
  all pass. `op/signatures.t`, `op/universal.t`, `op/coresubs.t`,
  `op/coreamp.t`, `op/sub.t`, `uni/method.t` and `lib/B/Deparse.t`:
  all pass.
- perl's own suite, whole (`make test_harness`, from the tarball and
  the patch): 2,930 files, 1,339,352 tests, all pass but one,
  `lib/perl5db.t` 124, which fails on stock 5.42.0 on the same
  machine (its `perldoc` finds a system with the manuals taken out).
  The first build of the port failed three more files, each mended
  above: `lib/warnings.t` and `lib/feature.t` (the 5.46) and
  `lib/B/Deparse-core.t`.
- Curly's own oracle check, `CURLY_PERL=/opt/perl-5.42-roles/bin/perl
  python3 t/checks.py oracle`: all 1,950 golden tests hold, under
  eight hash seeds, with the roles perl as the oracle.
- `docs/briefs/claims.py --perl /opt/perl-5.42-roles/bin/perl`: of
  the 1,101 statements the documents make about perl 5.42, all hold
  but three: `17-role` and `17-does`, which are roles, and
  `17-method-count` (below).
- `patch -p1` and `patchperl` with the plugin make the same tree from
  the tarball.

## Where it is not perl 5.42.0

What blead's class layer fixed, which 5.42.0 gets wrong: an array
field initialised from an empty list (an assertion on a DEBUGGING
perl), refaliasing a field in a method, two faults of cloning a field
under threads, a `:reader` after a `strict` error. And one message:

```
class P { method m($x) { $x } } P->new->m();
```

dies `Too few arguments for subroutine 'P::m' (got 0; expected 1)`
under 5.42.0 and `(got 1; expected 2)` under the roles perl, which
counts `$self`. Curly faults a wrong count, and a fault is not caught
(D13), so no program of Curly's can print it.

## Making it again

The branch moves; the patch does not. To make it from a newer
commit of the branch, in a clone of `stevan/perl5` with `Perl/perl5`'s
`v5.42.0` tag fetched and enough history to reach it: a branch from
`v5.42.0`, the four layers above by `git cherry-pick -x` (the
restricted ones by `git show C -- FILES | git apply -3 --index`),
the same mending, the generated files made again, and `git diff
v5.42.0 > roles-5.42.0.patch`. Then `build.sh`, the tests above, and
`claims.py --perl`.

## Licence

The patch is perl's code and Stevan's, under perl's terms (the
Artistic License or the GPL), as `runtime/sort.c` is (D82): to be
accounted for when the repository gets a licence.
