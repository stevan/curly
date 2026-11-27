#!/usr/bin/env python3
"""t/2000 to t/2003, and the faults from t/2020: the whole container
through a reference (step 13b; D107, D108, D114).

The definition, which is all this file knows of the language:

  EXPR->@*  @{ EXPR }        the array a reference points at
  EXPR->%*  %{ EXPR }        the hash
  EXPR->$#* $#{ EXPR }       the array's last index
  EXPR->@[...]  EXPR->@{...} a slice of either

Each stands where `@a`, `%h`, `$#a` and their slices stand: in a list
its values (a hash's keys and values by turns), where one value is
wanted its count (`$#` its last index), under `push`, `pop`, `shift`,
`unshift`, `splice`, `keys`, `values`, `delete` of a slice, in the list
of a `for`, `map`, `grep` and `sort`, among a call's arguments, and on
the left of `=`. **Reading through undef, or through an element or a key
that is not there, is a fault**, `undef where a reference is wanted`,
and through anything else that is not the reference wanted `not a
reference to an array` (or `to a hash`). **`push`, `unshift`, `splice`,
an assignment to the whole and a slice on the left make what they go
through**, as a store through an element does: every hop that is undef
or not there becomes a new array or hash, the variable at the head too;
not a loop's variable, which is a fault (T250), nor anything but a
variable or an element at the head (T252). A loop over a container
through a reference freezes it, and every container on the way to it,
whoever changes it (D114, T251).

The model is Python, whose lists and dicts are references already: what
a program prints is worked out here, and `show` prints a structure in a
form the test's own `show` sub prints too (keys sorted). perl is the
second derivation: t/checks.py oracle holds every .expected of a test
without a `kind:` to what perl 5.42 prints, and each fault test's output
to the start of it.

2000 reads, 2001 the builtins that change a container through one, and
what they make, 2002 assignments to the whole and to slices, 2003 loops,
sorts, maps, greps and subs over one. 2020 on each fault once.

Every command that writes a file, one a line (t/checks.py runs them all):

    python3 t/models/whole.py --program 2000 > t/2000-whole-reads.pl
    python3 t/models/whole.py 2000 > t/2000-whole-reads.expected
    python3 t/models/whole.py --program 2001 > t/2001-whole-changes.pl
    python3 t/models/whole.py 2001 > t/2001-whole-changes.expected
    python3 t/models/whole.py --program 2002 > t/2002-whole-assignments.pl
    python3 t/models/whole.py 2002 > t/2002-whole-assignments.expected
    python3 t/models/whole.py --program 2003 > t/2003-whole-in-loops-and-subs.pl
    python3 t/models/whole.py 2003 > t/2003-whole-in-loops-and-subs.expected
    python3 t/models/whole.py --program 2020 > t/2020-fault-whole-read-undef-list.pl
    python3 t/models/whole.py 2020 > t/2020-fault-whole-read-undef-list.expected
    python3 t/models/whole.py --program 2021 > t/2021-fault-whole-read-undef-braces.pl
    python3 t/models/whole.py 2021 > t/2021-fault-whole-read-undef-braces.expected
    python3 t/models/whole.py --program 2022 > t/2022-fault-whole-read-undef-count.pl
    python3 t/models/whole.py 2022 > t/2022-fault-whole-read-undef-count.expected
    python3 t/models/whole.py --program 2023 > t/2023-fault-whole-read-undef-tested.pl
    python3 t/models/whole.py 2023 > t/2023-fault-whole-read-undef-tested.expected
    python3 t/models/whole.py --program 2024 > t/2024-fault-whole-read-undef-last-index.pl
    python3 t/models/whole.py 2024 > t/2024-fault-whole-read-undef-last-index.expected
    python3 t/models/whole.py --program 2025 > t/2025-fault-whole-read-undef-last-index-braces.pl
    python3 t/models/whole.py 2025 > t/2025-fault-whole-read-undef-last-index-braces.expected
    python3 t/models/whole.py --program 2026 > t/2026-fault-whole-read-undef-pop.pl
    python3 t/models/whole.py 2026 > t/2026-fault-whole-read-undef-pop.expected
    python3 t/models/whole.py --program 2027 > t/2027-fault-whole-read-undef-shift.pl
    python3 t/models/whole.py 2027 > t/2027-fault-whole-read-undef-shift.expected
    python3 t/models/whole.py --program 2028 > t/2028-fault-whole-read-undef-slice.pl
    python3 t/models/whole.py 2028 > t/2028-fault-whole-read-undef-slice.expected
    python3 t/models/whole.py --program 2029 > t/2029-fault-whole-read-undef-join.pl
    python3 t/models/whole.py 2029 > t/2029-fault-whole-read-undef-join.expected
    python3 t/models/whole.py --program 2030 > t/2030-fault-whole-read-undef-reverse.pl
    python3 t/models/whole.py 2030 > t/2030-fault-whole-read-undef-reverse.expected
    python3 t/models/whole.py --program 2031 > t/2031-fault-whole-read-undef-sort.pl
    python3 t/models/whole.py 2031 > t/2031-fault-whole-read-undef-sort.expected
    python3 t/models/whole.py --program 2032 > t/2032-fault-whole-read-undef-for.pl
    python3 t/models/whole.py 2032 > t/2032-fault-whole-read-undef-for.expected
    python3 t/models/whole.py --program 2033 > t/2033-fault-whole-read-undef-map.pl
    python3 t/models/whole.py 2033 > t/2033-fault-whole-read-undef-map.expected
    python3 t/models/whole.py --program 2034 > t/2034-fault-whole-read-undef-grep.pl
    python3 t/models/whole.py 2034 > t/2034-fault-whole-read-undef-grep.expected
    python3 t/models/whole.py --program 2035 > t/2035-fault-whole-read-undef-sort-block.pl
    python3 t/models/whole.py 2035 > t/2035-fault-whole-read-undef-sort-block.expected
    python3 t/models/whole.py --program 2036 > t/2036-fault-whole-read-undef-arguments.pl
    python3 t/models/whole.py 2036 > t/2036-fault-whole-read-undef-arguments.expected
    python3 t/models/whole.py --program 2037 > t/2037-fault-whole-read-undef-in-a-list.pl
    python3 t/models/whole.py 2037 > t/2037-fault-whole-read-undef-in-a-list.expected
    python3 t/models/whole.py --program 2038 > t/2038-fault-whole-read-undef-add.pl
    python3 t/models/whole.py 2038 > t/2038-fault-whole-read-undef-add.expected
    python3 t/models/whole.py --program 2039 > t/2039-fault-whole-read-undef-hash.pl
    python3 t/models/whole.py 2039 > t/2039-fault-whole-read-undef-hash.expected
    python3 t/models/whole.py --program 2040 > t/2040-fault-whole-read-undef-hash-braces.pl
    python3 t/models/whole.py 2040 > t/2040-fault-whole-read-undef-hash-braces.expected
    python3 t/models/whole.py --program 2041 > t/2041-fault-whole-read-undef-hash-count.pl
    python3 t/models/whole.py 2041 > t/2041-fault-whole-read-undef-hash-count.expected
    python3 t/models/whole.py --program 2042 > t/2042-fault-whole-read-undef-keys.pl
    python3 t/models/whole.py 2042 > t/2042-fault-whole-read-undef-keys.expected
    python3 t/models/whole.py --program 2043 > t/2043-fault-whole-read-undef-values.pl
    python3 t/models/whole.py 2043 > t/2043-fault-whole-read-undef-values.expected
    python3 t/models/whole.py --program 2044 > t/2044-fault-whole-read-undef-keys-count.pl
    python3 t/models/whole.py 2044 > t/2044-fault-whole-read-undef-keys-count.expected
    python3 t/models/whole.py --program 2045 > t/2045-fault-whole-read-undef-hash-slice.pl
    python3 t/models/whole.py 2045 > t/2045-fault-whole-read-undef-hash-slice.expected
    python3 t/models/whole.py --program 2046 > t/2046-fault-whole-read-undef-delete-slice.pl
    python3 t/models/whole.py 2046 > t/2046-fault-whole-read-undef-delete-slice.expected
    python3 t/models/whole.py --program 2047 > t/2047-fault-whole-read-undef-hash-for.pl
    python3 t/models/whole.py 2047 > t/2047-fault-whole-read-undef-hash-for.expected
    python3 t/models/whole.py --program 2048 > t/2048-fault-whole-read-through-missing-key.pl
    python3 t/models/whole.py 2048 > t/2048-fault-whole-read-through-missing-key.expected
    python3 t/models/whole.py --program 2049 > t/2049-fault-whole-read-through-missing-index.pl
    python3 t/models/whole.py 2049 > t/2049-fault-whole-read-through-missing-index.expected
    python3 t/models/whole.py --program 2050 > t/2050-fault-whole-read-through-undef-element.pl
    python3 t/models/whole.py 2050 > t/2050-fault-whole-read-through-undef-element.expected
    python3 t/models/whole.py --program 2051 > t/2051-fault-whole-read-through-missing-deep.pl
    python3 t/models/whole.py 2051 > t/2051-fault-whole-read-through-missing-deep.expected
    python3 t/models/whole.py --program 2052 > t/2052-fault-whole-read-a-hash-as-an-array.pl
    python3 t/models/whole.py 2052 > t/2052-fault-whole-read-a-hash-as-an-array.expected
    python3 t/models/whole.py --program 2053 > t/2053-fault-whole-read-an-array-as-a-hash.pl
    python3 t/models/whole.py 2053 > t/2053-fault-whole-read-an-array-as-a-hash.expected
    python3 t/models/whole.py --program 2054 > t/2054-fault-whole-read-a-number.pl
    python3 t/models/whole.py 2054 > t/2054-fault-whole-read-a-number.expected
    python3 t/models/whole.py --program 2055 > t/2055-fault-whole-read-a-string.pl
    python3 t/models/whole.py 2055 > t/2055-fault-whole-read-a-string.expected
    python3 t/models/whole.py --program 2056 > t/2056-fault-whole-last-index-of-a-hash.pl
    python3 t/models/whole.py 2056 > t/2056-fault-whole-last-index-of-a-hash.expected
    python3 t/models/whole.py --program 2057 > t/2057-fault-whole-slice-of-the-other-kind.pl
    python3 t/models/whole.py 2057 > t/2057-fault-whole-slice-of-the-other-kind.expected
    python3 t/models/whole.py --program 2058 > t/2058-fault-whole-read-a-call-giving-undef.pl
    python3 t/models/whole.py 2058 > t/2058-fault-whole-read-a-call-giving-undef.expected
    python3 t/models/whole.py --program 2059 > t/2059-fault-whole-push-through-a-hash.pl
    python3 t/models/whole.py 2059 > t/2059-fault-whole-push-through-a-hash.expected
    python3 t/models/whole.py --program 2060 > t/2060-fault-whole-push-through-empty-string.pl
    python3 t/models/whole.py 2060 > t/2060-fault-whole-push-through-empty-string.expected
    python3 t/models/whole.py --program 2061 > t/2061-fault-whole-push-through-false.pl
    python3 t/models/whole.py 2061 > t/2061-fault-whole-push-through-false.expected
    python3 t/models/whole.py --program 2062 > t/2062-fault-whole-splice-through-a-number.pl
    python3 t/models/whole.py 2062 > t/2062-fault-whole-splice-through-a-number.expected
    python3 t/models/whole.py --program 2063 > t/2063-fault-whole-assign-through-the-other-kind.pl
    python3 t/models/whole.py 2063 > t/2063-fault-whole-assign-through-the-other-kind.expected
    python3 t/models/whole.py --program 2064 > t/2064-fault-whole-slice-store-through-the-other-kind.pl
    python3 t/models/whole.py 2064 > t/2064-fault-whole-slice-store-through-the-other-kind.expected
    python3 t/models/whole.py --program 2065 > t/2065-fault-whole-hop-of-the-other-kind.pl
    python3 t/models/whole.py 2065 > t/2065-fault-whole-hop-of-the-other-kind.expected
    python3 t/models/whole.py --program 2066 > t/2066-fault-whole-push-through-a-call.pl
    python3 t/models/whole.py 2066 > t/2066-fault-whole-push-through-a-call.expected
    python3 t/models/whole.py --program 2067 > t/2067-fault-whole-push-through-a-choice.pl
    python3 t/models/whole.py 2067 > t/2067-fault-whole-push-through-a-choice.expected
    python3 t/models/whole.py --program 2068 > t/2068-fault-whole-assign-through-or.pl
    python3 t/models/whole.py 2068 > t/2068-fault-whole-assign-through-or.expected
    python3 t/models/whole.py --program 2069 > t/2069-fault-whole-push-through-loop-variable.pl
    python3 t/models/whole.py 2069 > t/2069-fault-whole-push-through-loop-variable.expected
    python3 t/models/whole.py --program 2070 > t/2070-fault-whole-assign-through-it.pl
    python3 t/models/whole.py 2070 > t/2070-fault-whole-assign-through-it.expected
    python3 t/models/whole.py --program 2071 > t/2071-fault-whole-push-through-it-in-a-map.pl
    python3 t/models/whole.py 2071 > t/2071-fault-whole-push-through-it-in-a-map.expected
    python3 t/models/whole.py --program 2072 > t/2072-fault-whole-odd-hash-assigned.pl
    python3 t/models/whole.py 2072 > t/2072-fault-whole-odd-hash-assigned.expected
    python3 t/models/whole.py --program 2073 > t/2073-fault-whole-odd-hash-assigned-braces.pl
    python3 t/models/whole.py 2073 > t/2073-fault-whole-odd-hash-assigned-braces.expected
    python3 t/models/whole.py --program 2074 > t/2074-fault-whole-slice-store-before-the-start.pl
    python3 t/models/whole.py 2074 > t/2074-fault-whole-slice-store-before-the-start.expected
    python3 t/models/whole.py --program 2075 > t/2075-fault-whole-splice-past-the-end.pl
    python3 t/models/whole.py 2075 > t/2075-fault-whole-splice-past-the-end.expected
    python3 t/models/whole.py --program 2076 > t/2076-fault-whole-frozen-push.pl
    python3 t/models/whole.py 2076 > t/2076-fault-whole-frozen-push.expected
    python3 t/models/whole.py --program 2077 > t/2077-fault-whole-frozen-store.pl
    python3 t/models/whole.py 2077 > t/2077-fault-whole-frozen-store.expected
    python3 t/models/whole.py --program 2078 > t/2078-fault-whole-frozen-pop.pl
    python3 t/models/whole.py 2078 > t/2078-fault-whole-frozen-pop.expected
    python3 t/models/whole.py --program 2079 > t/2079-fault-whole-frozen-shift.pl
    python3 t/models/whole.py 2079 > t/2079-fault-whole-frozen-shift.expected
    python3 t/models/whole.py --program 2080 > t/2080-fault-whole-frozen-unshift.pl
    python3 t/models/whole.py 2080 > t/2080-fault-whole-frozen-unshift.expected
    python3 t/models/whole.py --program 2081 > t/2081-fault-whole-frozen-splice.pl
    python3 t/models/whole.py 2081 > t/2081-fault-whole-frozen-splice.expected
    python3 t/models/whole.py --program 2082 > t/2082-fault-whole-frozen-assign.pl
    python3 t/models/whole.py 2082 > t/2082-fault-whole-frozen-assign.expected
    python3 t/models/whole.py --program 2083 > t/2083-fault-whole-frozen-slice-store.pl
    python3 t/models/whole.py 2083 > t/2083-fault-whole-frozen-slice-store.expected
    python3 t/models/whole.py --program 2084 > t/2084-fault-whole-frozen-through-a-name.pl
    python3 t/models/whole.py 2084 > t/2084-fault-whole-frozen-through-a-name.expected
    python3 t/models/whole.py --program 2085 > t/2085-fault-whole-frozen-named-through-a-reference.pl
    python3 t/models/whole.py 2085 > t/2085-fault-whole-frozen-named-through-a-reference.expected
    python3 t/models/whole.py --program 2086 > t/2086-fault-whole-frozen-hash-values.pl
    python3 t/models/whole.py 2086 > t/2086-fault-whole-frozen-hash-values.expected
    python3 t/models/whole.py --program 2087 > t/2087-fault-whole-frozen-hash-whole.pl
    python3 t/models/whole.py 2087 > t/2087-fault-whole-frozen-hash-whole.expected
    python3 t/models/whole.py --program 2088 > t/2088-fault-whole-frozen-hash-assign.pl
    python3 t/models/whole.py 2088 > t/2088-fault-whole-frozen-hash-assign.expected
    python3 t/models/whole.py --program 2089 > t/2089-fault-whole-frozen-hash-delete-slice.pl
    python3 t/models/whole.py 2089 > t/2089-fault-whole-frozen-hash-delete-slice.expected
    python3 t/models/whole.py --program 2090 > t/2090-fault-whole-frozen-on-the-way.pl
    python3 t/models/whole.py 2090 > t/2090-fault-whole-frozen-on-the-way.expected
    python3 t/models/whole.py --program 2091 > t/2091-fault-whole-frozen-in-a-map.pl
    python3 t/models/whole.py 2091 > t/2091-fault-whole-frozen-in-a-map.expected
    python3 t/models/whole.py --program 2092 > t/2092-fault-whole-frozen-in-a-grep.pl
    python3 t/models/whole.py 2092 > t/2092-fault-whole-frozen-in-a-grep.expected
    python3 t/models/whole.py --program 2093 > t/2093-fault-whole-frozen-in-a-sort.pl
    python3 t/models/whole.py 2093 > t/2093-fault-whole-frozen-in-a-sort.expected
    python3 t/models/whole.py --program 2094 > t/2094-fault-whole-frozen-from-a-sub.pl
    python3 t/models/whole.py 2094 > t/2094-fault-whole-frozen-from-a-sub.expected
    python3 t/models/whole.py --program 2095 > t/2095-fault-whole-slice-past-the-end-in-a-loop.pl
    python3 t/models/whole.py 2095 > t/2095-fault-whole-slice-past-the-end-in-a-loop.expected
    python3 t/models/whole.py --program 2096 > t/2096-fault-whole-slice-no-key-in-a-loop.pl
    python3 t/models/whole.py 2096 > t/2096-fault-whole-slice-no-key-in-a-loop.expected
    python3 t/models/whole.py --program 2097 > t/2097-fault-whole-slice-past-the-end-in-a-map.pl
    python3 t/models/whole.py 2097 > t/2097-fault-whole-slice-past-the-end-in-a-map.expected
    python3 t/models/whole.py --program 2098 > t/2098-fault-whole-slice-past-the-end-in-arguments.pl
    python3 t/models/whole.py 2098 > t/2098-fault-whole-slice-past-the-end-in-arguments.expected
    python3 t/models/whole.py --program 2099 > t/2099-fault-whole-joined-reference.pl
    python3 t/models/whole.py 2099 > t/2099-fault-whole-joined-reference.expected
    python3 t/models/whole.py --program 2100 > t/2100-fault-whole-sorted-references.pl
    python3 t/models/whole.py 2100 > t/2100-fault-whole-sorted-references.expected
"""

import sys

UNDEF_REF = 'undef where a reference is wanted'
NOT_ARRAY = 'not a reference to an array'
NOT_HASH = 'not a reference to a hash'
FROZEN = 'an array was changed while a foreach is over it'
HFROZEN = 'a hash was changed while a foreach is over it'
ODD = 'an odd number of values for a hash'
SLICE_PAST = 'a slice past the end of the array, where perl would make the elements'
KEY_PAST = 'a slice with a key that is not there, where perl would make it'
BEFORE = 'an element before the start of the array'
STRING = 'a reference where a string is wanted'
SPLICE_PAST = 'splice past the end of the array'

class Fault(Exception):
    pass

# ---- values: an int, a str, None for undef, a list or a dict.

def lit(v):
    if v is None:
        return 'undef'
    if isinstance(v, int):
        return str(v)
    if isinstance(v, str):
        return f'"{v}"'
    if isinstance(v, list):
        return '[' + ', '.join(lit(x) for x in v) + ']'
    return '{' + ', '.join(f'{k} => {lit(x)}' for k, x in v.items()) + '}'

def fresh(v):
    if isinstance(v, list):
        return [fresh(x) for x in v]
    if isinstance(v, dict):
        return {k: fresh(x) for k, x in v.items()}
    return v

def show(v):
    """What the test's `show` sub prints of a value."""
    if v is None:
        return 'u'
    if isinstance(v, list):
        return '[' + ','.join(show(x) for x in v) + ']'
    if isinstance(v, dict):
        return '{' + ','.join(f'{k}:{show(v[k])}' for k in sorted(v)) + '}'
    return str(v)

SHOW = [
    'sub show($v) {',
    '    return "u" unless defined $v;',
    '    return "[" . join(",", map { show($_) } $v->@*) . "]" if ref($v) eq "ARRAY";',
    '    return "{" . join(",", map { $_ . ":" . show($v->{$_}) } sort keys $v->%*) . "}" if ref($v) eq "HASH";',
    '    return $v;',
    '}',
]

def get(c, k):
    if isinstance(c, list):
        return c[k] if -len(c) <= k < len(c) else None
    return c.get(k)

def kind_of(hash):
    return dict if hash else list

def through(v, hash):
    """What the whole container is, read through v (D107)."""
    if v is None:
        raise Fault(UNDEF_REF)
    if not isinstance(v, kind_of(hash)):
        raise Fault(NOT_HASH if hash else NOT_ARRAY)
    return v

def put(c, k, v):
    if isinstance(c, list):
        if k < -len(c):
            raise Fault(BEFORE)
        if k < 0:
            k += len(c)
        while len(c) <= k:
            c.append(None)
    c[k] = v

# ---- a program and what it prints

class Prog:
    def __init__(self):
        self.lines = []
        self.out = []
        self.env = {}
        self.n = 0
        # The subs, which stand at the top of the file (D72).
        self.subs = []

    def say(self, text, printed):
        self.lines.append(text)
        self.out.append(printed)

    # A place: ('$', name) a scalar, with subscripts after it, each an
    # int (an index) or a str (a key); ('@', name) or ('%', name) a named
    # array's or hash's element, its subscripts the element's and after.
    def head(self, base, subs):
        """The text of the reference: a variable, or an element."""
        def sub(k):
            return f'[{k}]' if isinstance(k, int) else f'{{{k}}}'
        kind, name = base
        if kind == '$':
            text = f'${name}' + (('->' + sub(subs[0])) if subs else '')
            rest = subs[1:]
        else:
            text, rest = f'${name}' + sub(subs[0]), subs[1:]
        self.n += 1
        for k in rest:
            text += ('->' if self.n % 2 else '') + sub(k)
        return text

    def at(self, base, subs):
        """The value at a place, read through (D107)."""
        kind, name = base
        if kind == '$':
            v = self.env['$' + name]
            for k in subs:
                v = get(through(v, isinstance(k, str)), k)
            return v
        v = self.env[kind + name]
        for k in subs:
            v = get(through(v, isinstance(k, str)), k)
        return v

    def whole(self, base, subs, hash):
        return through(self.at(base, subs), hash)

    def made(self, base, subs, hash):
        """The container at a place, every hop made on the way, and it
        too (T248)."""
        kind, name = base
        if kind == '$' and not subs:
            if self.env['$' + name] is None:
                self.env['$' + name] = kind_of(hash)()
            return through(self.env['$' + name], hash)
        c = self.env['$' + name] if kind == '$' else self.env[kind + name]
        if kind == '$':
            if c is None:
                c = self.env['$' + name] = kind_of(isinstance(subs[0], str))()
            c = through(c, isinstance(subs[0], str))
        wants = [isinstance(k, str) for k in subs[1:]] + [hash]
        for k, want in zip(subs, wants):
            v = get(c, k)
            if v is None:
                v = kind_of(want)()
                put(c, k, v)
            c = through(v, want)
        return c

    def spelled(self, base, subs, form, braces):
        """`HEAD->@*` or `@{ HEAD }`, and the rest of the forms."""
        h = self.head(base, subs)
        if braces:
            return {'@': f'@{{{h}}}', '%': f'%{{ {h} }}', '#': f'$#{{{h}}}'}[form]
        return {'@': f'{h}->@*', '%': f'{h}->%*', '#': f'{h}->$#*'}[form]

    def dump(self, name):
        self.say(f'say(show(${name}));', show(self.env['$' + name]))

    def my(self, name, v):
        self.lines.append(f'my ${name} = {lit(v)};')
        self.env['$' + name] = fresh(v)

    def block(self, f):
        outer = self.env
        self.env = dict(outer)
        self.lines.append('{')
        f(self)
        self.lines.append('}')
        self.env = outer

STRUCTURES = [
    [1, [2, 3], {'k': 'v', 'n': [4, None]}, [], 'end'],
    {'a': {'b': {'c': 5}}, 'list': [[6, 7], [8]], 'e': {}, 'z': 0},
    [[[[9, 10]]]],
    {'x': [{'y': [11, 12, 13]}]},
]

def containers(v, path=()):
    """Every path to a container, the empty one first."""
    found = []
    if isinstance(v, (list, dict)):
        found.append(list(path))
        for k in (range(len(v)) if isinstance(v, list) else sorted(v)):
            found += containers(v[k], path + (k,))
    return found

def items(c):
    return ','.join(show(x) for x in c)

SHOWN = 'map { show($_) }'

def case_reads(p):
    for s in STRUCTURES:
        def one(p, s=s):
            p.my('r', s)
            for n, path in enumerate(containers(s)):
                braces = n % 2 == 1
                c = p.at(('$', 'r'), path)
                if isinstance(c, list):
                    p.say(f'say(scalar({p.spelled(("$", "r"), path, "@", braces)}));', str(len(c)))
                    p.say(f'say({p.spelled(("$", "r"), path, "#", not braces)});', str(len(c) - 1))
                    p.say(f'say(join(",", {SHOWN} {p.spelled(("$", "r"), path, "@", not braces)}));', items(c))
                    if c:
                        # (Past the end, a slice in the list of a `map` is
                        # a fault, where perl would make the elements:
                        # T177. Assigned, it is undef.)
                        idx = [0, -1]
                        p.say(f'say(join(",", {SHOWN} {p.head(("$", "r"), path)}->@[{", ".join(map(str, idx))}]));', ','.join(show(get(c, k)) for k in idx))
                        v = len(p.lines)
                        p.lines.append(f'my @s{v} = {p.head(("$", "r"), path)}->@[0, {len(c)}];')
                        p.say(f'say(scalar(@s{v}), defined($s{v}[1]) ? "d" : "u");', '2u')
                        p.say(f'say({p.spelled(("$", "r"), path, "@", braces)} ? "some" : "none", {p.spelled(("$", "r"), path, "@", not braces)} + 1);', f'some{len(c) + 1}')
                    else:
                        p.say(f'say({p.spelled(("$", "r"), path, "@", braces)} ? "some" : "none");', 'none')
                else:
                    p.say(f'say(scalar({p.spelled(("$", "r"), path, "%", braces)}));', str(len(c)))
                    p.say(f'say(join(",", sort keys {p.spelled(("$", "r"), path, "%", not braces)}));', ','.join(sorted(c)))
                    p.say(f'say(join(",", sort {SHOWN} values {p.spelled(("$", "r"), path, "%", braces)}));', ','.join(sorted(show(x) for x in c.values())))
                    p.say(f'say(scalar(keys {p.spelled(("$", "r"), path, "%", braces)}), scalar(values {p.spelled(("$", "r"), path, "%", not braces)}));', f'{len(c)}{len(c)}')
                    if c:
                        ks = sorted(c)[:2]
                        p.say(f'say(join(",", {SHOWN} {p.head(("$", "r"), path)}->@{{{", ".join(lit(k) for k in ks)}}}));', ','.join(show(c.get(k)) for k in ks))
                        v = len(p.lines)
                        p.lines.append(f'my @k{v} = {p.head(("$", "r"), path)}->@{{{lit(ks[0])}, "nope"}};')
                        p.say(f'say(scalar(@k{v}), defined($k{v}[1]) ? "d" : "u");', '2u')
                    p.say(f'say(join(",", sort {SHOWN} {p.spelled(("$", "r"), path, "%", braces)}));', ','.join(sorted([show(k) for k in c] + [show(x) for x in c.values()])))
        p.block(one)
    def named(p):
        p.lines += ['my @a = ([1, 2], {k => [3]});', 'my %h = (x => [4, 5, 6], y => {z => 7});']
        p.say('say(scalar($a[0]->@*), scalar(@{$a[1]{k}}), $a[0]->$#*, $#{$h{x}});', '2112')
        p.say('say(join(",", $a[1]{k}->@*, @{$h{x}}, sort keys %{$h{y}}));', '3,4,5,6,z')
        p.say('say(join(",", $h{x}->@[2, 0], $a[1]->@{"k"}->[0]));'.replace(', $a[1]->@{"k"}->[0]', ''), '6,4')
    p.block(named)
    def heads(p):
        p.subs += ['sub pair() {', '    return [7, 8];', '}']
        p.lines += ['my $c = 1;', 'my $x = [1];', 'my $y = [2, 3];']
        p.say('say(join(",", pair()->@*), scalar(@{ pair() }), pair()->$#*);', '7,821')
        p.say('say(join(",", [4, 5]->@*), scalar(@{ [6] }), $#{ [1, 2, 3] }, join(",", sort keys %{ +{q => 1, p => 2} }));', '4,512p,q')
        p.say('say(join(",", @{ $c ? $y : $x }), scalar(($x)->@*), join(",", @{ $x }));', '2,311')
        p.say('say(join(",", +{a => [9]}->{a}->@*), join(",", [[1, 2]]->[0]->@[1, 0]));', '92,1')
    p.block(heads)
    def counts(p):
        p.lines += ['my $r = [5, 6, 7];', 'my $h = {a => 1, b => 2};', 'my $e = [];']
        p.say('say($r->@* + 0, $r->@* * 2, $r->$#* - 1, $r->@* == 3 ? "three" : "not", @{$e} || "empty");', '361threeempty')
        p.say('say("n=" . $r->@*, " k=" . keys $h->%*, " h=" . %{$h});', 'n=3 k=2 h=2')
        p.lines += ['my $n = $r->@*;', 'my $m = %{$h};', 'my $l = $#{$e};']
        p.say('say($n, $m, $l);', '32-1')
        p.lines += ['my $g = grep { $_ > 5 } $r->@*;', 'my $twice = map { ($_, $_) } $r->@*;']
        p.say('say($g, $twice);', '26')
        p.lines += ['my ($first, @rest) = $r->@*;', 'my @copy = @{$r};', 'my %hc = $h->%*;', '$copy[0] = 9;']
        p.say('say($first, "|", join(",", @rest), "|", $r->[0], $copy[0], "|", join(",", map { "$_$hc{$_}" } sort keys %hc));', '5|6,7|59|a1,b2')
        p.say('say(join(",", reverse $r->@*), "|", join("-", @{$r}), "|", join(",", sort { $b <=> $a } $r->@*));', '7,6,5|5-6-7|7,6,5')
        p.say('say(join(",", sort $h->%*));', '1,2,a,b')
    p.block(counts)

def case_changes(p):
    def from_undef(p):
        p.lines.append('my $r;')
        p.env['$r'] = None
        ops = [
            ('push $r->@*, 1, 2;', lambda: p.made(('$', 'r'), [], False).extend([1, 2])),
            ('unshift @{$r}, 0;', lambda: p.made(('$', 'r'), [], False).insert(0, 0)),
        ]
        for text, f in ops:
            p.lines.append(text)
            f()
            p.dump('r')
        p.lines.append('my $h;')
        p.env['$h'] = None
        p.lines.append('push $h->{list}->@*, "a";')
        p.made(('$', 'h'), ['list'], False).append('a')
        p.lines.append('push @{$h->{list}}, "b";')
        p.made(('$', 'h'), ['list'], False).append('b')
        p.lines.append('push $h->{deep}[2]{more}->@*, 3;')
        p.made(('$', 'h'), ['deep', 2, 'more'], False).append(3)
        p.lines.append('unshift $h->{deep}[0]->@*, 4, 5;')
        p.made(('$', 'h'), ['deep', 0], False)[0:0] = [4, 5]
        p.dump('h')
        p.lines.append('my $s;')
        p.env['$s'] = None
        p.lines.append('splice($s->@*, 0, 0, 7, 8);')
        p.made(('$', 's'), [], False)[0:0] = [7, 8]
        p.lines.append('splice(@{$s->[5]}, 0, 0, 9);')
        p.made(('$', 's'), [5], False)[0:0] = [9]
        p.dump('s')
    p.block(from_undef)
    def into(p):
        p.my('r', [1, 2, 3, 4, 5])
        p.lines.append('my @gone = splice($r->@*, 1, 2);')
        gone = p.env['$r'][1:3]
        del p.env['$r'][1:3]
        p.say('say(join(",", @gone));', items(gone))
        p.dump('r')
        p.lines.append('my @also = splice(@{$r}, 1, 1, "x", "y");')
        also = p.env['$r'][1:2]
        p.env['$r'][1:2] = ['x', 'y']
        p.say('say(join(",", @also));', items(also))
        p.lines.append('splice($r->@*, 3);')
        del p.env['$r'][3:]
        p.dump('r')
        p.lines.append('splice(@{$r}, -1, 1);')
        del p.env['$r'][-1:]
        p.dump('r')
        for word, side in (('pop', -1), ('shift', 0), ('pop', -1)):
            c = p.env['$r']
            v = c.pop(side) if c else None
            p.lines.append(f'my $v{p.n} = {word} {"$r->@*" if side else "@{$r}"};')
            p.say(f'say(defined($v{p.n}) ? $v{p.n} : "u");', show(v))
            p.n += 1
        p.dump('r')
        p.my('t', {'a': [1], 'b': {'c': [2, 3]}})
        p.lines.append('push $t->{a}->@*, 4;')
        p.env['$t']['a'].append(4)
        p.lines.append('my $last = pop $t->{b}{c}->@*;')
        last = p.env['$t']['b']['c'].pop()
        p.lines.append('unshift @{$t->{b}->{c}}, $last;')
        p.env['$t']['b']['c'].insert(0, last)
        p.lines.append('push $t->{new}->@*, scalar($t->{a}->@*);')
        p.made(('$', 't'), ['new'], False).append(len(p.env['$t']['a']))
        p.dump('t')
        p.lines += ['my @a = ([1]);', 'my %h;', 'push $a[0]->@*, 2;', 'push $a[2]->@*, 3;', 'push @{$h{k}}, 4;', 'push $h{k}->@*, 5;']
        p.say('say(show(\\@a), show(\\%h));', '[[1,2],u,[3]]{k:[4,5]}')
        p.lines += ['my $c = [1, 2];', 'push $c->@*, $c->@*;', 'unshift $c->@*, scalar($c->@*);']
        p.say('say(show($c));', '[4,1,2,1,2]')
    p.block(into)
    def deletes(p):
        p.my('h', {'a': 1, 'b': 2, 'c': 3, 'd': [4]})
        p.lines.append('my @d = delete $h->@{"a", "c", "nope"};')
        d = [p.env['$h'].pop(k, None) for k in ('a', 'c', 'nope')]
        p.say('say(join(",", map { show($_) } @d));', items(d))
        p.dump('h')
        p.lines.append('delete $h->@{"b"};')
        p.env['$h'].pop('b')
        p.dump('h')
        p.my('n', {'x': {'p': 1, 'q': 2}})
        p.lines.append('my @e = delete $n->{x}->@{"q"};')
        e = [p.env['$n']['x'].pop('q')]
        p.say('say(join(",", @e));', items(e))
        p.dump('n')
    p.block(deletes)

def case_assign(p):
    def whole(p):
        p.lines.append('my $r;')
        p.env['$r'] = None
        p.lines.append('$r->@* = (1, 2, 3);')
        c = p.made(('$', 'r'), [], False)
        c[:] = [1, 2, 3]
        p.dump('r')
        p.lines.append('@{$r} = ($r->@*, 4);')
        c[:] = c + [4]
        p.dump('r')
        p.lines.append('$r->@* = reverse $r->@*;')
        c.reverse()
        p.dump('r')
        p.lines.append('@{$r} = ();')
        c[:] = []
        p.dump('r')
        p.lines.append('my $h;')
        p.env['$h'] = None
        p.lines.append('$h->%* = (a => 1, b => [2]);')
        p.made(('$', 'h'), [], True).update({'a': 1, 'b': [2]})
        p.lines.append('%{$h->{inner}} = (c => 3, c => 4);')
        p.made(('$', 'h'), ['inner'], True).update({'c': 4})
        p.lines.append('$h->{list}->@* = (5);')
        p.made(('$', 'h'), ['list'], False)[:] = [5]
        p.dump('h')
        p.lines.append('$h->%* = ();')
        p.env['$h'].clear()
        p.dump('h')
        p.lines += ['my @a = (1, 2);', 'my $ra = \\@a;', '$ra->@* = (7, 8, 9);', 'my %g = (k => 1);', 'my $rg = \\%g;', '%{$rg} = (j => 2);']
        p.say('say("@a", join(",", map { "$_$g{$_}" } sort keys %g));', '7 8 9j2')
        p.lines += ['my $x;', 'my $s = [0];', '($x, $s->@*) = (1, 2, 3);', 'my $t;', '($t->@*) = (4, 5);', 'my $y;', 'my $u = {};', '($y, %{$u}) = ("p", a => 1);']
        p.say('say($x, show($s), show($t), $y, show($u));', '1[2,3][4,5]p{a:1}')
    p.block(whole)
    def slices(p):
        p.lines.append('my $r;')
        p.env['$r'] = None
        p.lines.append('$r->@[0, 2] = ("a", "c");')
        c = p.made(('$', 'r'), [], False)
        put(c, 0, 'a')
        put(c, 2, 'c')
        p.dump('r')
        p.lines.append('$r->@[1, 4] = ("b");')
        put(c, 1, 'b')
        put(c, 4, None)
        p.dump('r')
        p.lines.append('$r->@[-1, -5] = (5, 1);')
        put(c, -1, 5)
        put(c, -5, 1)
        p.dump('r')
        p.lines.append('my $h;')
        p.env['$h'] = None
        p.lines.append('$h->@{"x", "y"} = (1, 2);')
        hh = p.made(('$', 'h'), [], True)
        hh.update({'x': 1, 'y': 2})
        p.lines.append('$h->{in}->@{"p", "q"} = (3);')
        p.made(('$', 'h'), ['in'], True).update({'p': 3, 'q': None})
        p.lines.append('$h->{l}->@[1] = (4);')
        put(p.made(('$', 'h'), ['l'], False), 1, 4)
        p.dump('h')
        p.lines.append('my @parts = $h->@{"y", "x"};')
        p.say('say(join(",", @parts));', '2,1')
    p.block(slices)

def case_loops(p):
    def loops(p):
        p.lines += ['my $r = [1, 2, 3];', 'my $t = 0;', 'for my $x ($r->@*) {', '    $t += $x;', '}']
        p.say('say($t);', '6')
        p.lines += ['for my $x (@{$r}, 10) {', '    print($x, " ");', '}', 'say("");']
        p.out.append('1 2 3 10 ')
        p.lines += ['for my $i (0 .. $r->$#*) {', '    say($i, ":", $r->[$i]);', '}']
        p.out += ['0:1', '1:2', '2:3']
        p.lines += ['my $h = {b => [2, 3], a => [1]};', 'for my $k (sort keys $h->%*) {', '    say($k, "=", join(",", $h->{$k}->@*));', '}']
        p.out += ['a=1', 'b=2,3']
        p.say('say(join(",", sort map { scalar($_->@*) } values $h->%*));', '1,2')
        p.lines += ['for my $k (sort keys %{$h}) {', '    delete $h->{$k};', '}']
        p.say('say(scalar(%{$h}));', '0')
        p.lines += ['my $grid = [[1, 2], [3, 4]];', 'for my $row ($grid->@*) {', '    say(join(" ", map { $_ * 10 } $row->@*));', '}']
        p.out += ['10 20', '30 40']
        p.lines += ['my $s = 0;', '$s += $_ for $grid->[1]->@*;']
        p.say('say($s);', '7')
        p.lines += ['for ($grid->@*) {', '    push $_->@*, 0;', '}']
        p.say('say(show($grid));', '[[1,2,0],[3,4,0]]')
        p.lines += ['my $w = [3, 1, 2];', 'for my $x ($w->@[2, 0]) {', '    say($x);', '}']
        p.out += ['2', '3']
        p.lines += ['my $words = {one => 1, two => 2, three => 3};', 'for my $x ($words->@{"two", "one"}) {', '    say($x);', '}']
        p.out += ['2', '1']
    p.block(loops)
    def lists(p):
        p.lines += ['my $r = [5, 3, 9, 1];', 'my $h = {x => 2, y => 1};']
        p.say('say(join(",", sort { $a <=> $b } $r->@*), "|", join(",", sort { $h->{$a} <=> $h->{$b} } keys $h->%*));', '1,3,5,9|y,x')
        p.say('say(join(",", map { $_ + 1 } @{$r}), "|", join(",", grep { $_ > 3 } $r->@*));', '6,4,10,2|5,9')
        p.say('say(join(",", map { $_ * 2 } sort { $a <=> $b } values $h->%*));', '2,4')
        p.say('say(join(",", map { $_ } $r->@[1, 2], @{$r}[0 .. 0]));'.replace(', @{$r}[0 .. 0]', ''), '3,9')
        p.lines += ['my @sorted = sort { $a <=> $b } $r->@*;', '$r->@* = sort { $b <=> $a } $r->@*;']
        p.say('say("@sorted", "|", join(",", $r->@*));', '1 3 5 9|9,5,3,1')
        p.lines += ['my $u = [];', '$u->[0] = 3;', '$u->[3] = 1;', '$u->@* = sort { ($a // 0) <=> ($b // 0) } $u->@*;']
        p.say('say(join(",", map { $_ // "u" } $u->@*));', 'u,u,1,3')
    p.block(lists)
    def subs(p):
        p.subs += ['sub total(@xs) {', '    my $t = 0;', '    $t += $_ for @xs;', '    return $t;', '}',
                    'sub items($r) {', '    return $r->@*;', '}', 'sub pairs($h) {', '    return map { $_ . $h->{$_} } sort keys $h->%*;', '}',
                    'sub count($r) {', '    return scalar(@{$r});', '}', 'sub grow($r, $n) {', '    push $r->@*, $n;', '    return;', '}']
        p.lines += ['my $r = [1, 2, 3];']
        p.say('say(total($r->@*), total(@{$r}, 4), total($r->@[0, 2]));', '6104')
        p.lines += ['my @got = items($r);']
        p.say('say(scalar(@got), join(",", items([7, 8])), join(",", pairs({b => 2, a => 1})));', '37,8a1,b2')
        p.say('say(count($r), count([]));', '30')
        p.lines += ['my $e;', 'grow($r, 4);', 'my $f = [];', 'grow($f, 5);']
        p.say('say(join(",", $r->@*), show($f));', '1,2,3,4[5]')
        p.subs += ['sub opts($x, %o) {', '    return $x . join(",", map { "$_=$o{$_}" } sort keys %o);', '}']
        p.lines += ['my $o = {b => 2, a => 1};']
        p.say('say(opts("o:", $o->%*), opts("e:", %{ {} }));'.replace(', opts("e:", %{ {} })', ''), 'o:a=1,b=2')
    p.block(subs)

SAME = {
    '2000': ('whole-reads', case_reads),
    '2001': ('whole-changes', case_changes),
    '2002': ('whole-assignments', case_assign),
    '2003': ('whole-in-loops-and-subs', case_loops),
}

# ---- the faults: each program says 1, does the one thing, and says 2.

FAULTS = []

def fault(name, lines, message, at=None):
    FAULTS.append((name, lines, message, at))

# Reading through what is not a reference (D107): every way of using the
# whole container that reads, through undef.
READS = [('list', 'my @x = $r->@*;'), ('braces', 'my @x = @{$r};'), ('count', 'say(scalar($r->@*));'),
         ('tested', 'say("some") if $r->@*;'), ('last-index', 'say($r->$#*);'), ('last-index-braces', 'say($#{$r});'),
         ('pop', 'my $x = pop $r->@*;'), ('shift', 'my $x = shift @{$r};'), ('slice', 'my @x = $r->@[0];'),
         ('join', 'say(join(",", $r->@*));'), ('reverse', 'my @x = reverse $r->@*;'), ('sort', 'my @x = sort $r->@*;'),
         ('for', 'for my $x ($r->@*) {\n}'), ('map', 'my @x = map { $_ } $r->@*;'), ('grep', 'my @x = grep { 1 } @{$r};'),
         ('sort-block', 'my @x = sort { $a <=> $b } $r->@*;'), ('arguments', 'sub f(@x) {\n    return;\n}\nf($r->@*);'),
         ('in-a-list', 'say(1, $r->@*);'), ('add', 'say($r->@* + 1);')]
HREADS = [('hash', 'my %x = $r->%*;'), ('hash-braces', 'my %x = %{$r};'), ('hash-count', 'say(scalar(%{$r}));'),
          ('keys', 'my @k = sort keys $r->%*;'), ('values', 'my @v = sort values %{$r};'), ('keys-count', 'say(scalar(keys $r->%*));'),
          ('hash-slice', 'my @x = $r->@{"a"};'), ('delete-slice', 'delete $r->@{"a"};'), ('hash-for', 'for my $x (values $r->%*) {\n}')]
# (A loop's fault is its own line's: its list is worked out there.)
for name, code in READS + HREADS:
    fault(f'read-undef-{name}', ['my $r;'] + code.split('\n'), UNDEF_REF, 1 if name.endswith('for') else None)
fault('read-through-missing-key', ['my $h = {};', 'say(scalar($h->{list}->@*));'], UNDEF_REF)
fault('read-through-missing-index', ['my @a;', 'my @x = @{$a[2]};'], UNDEF_REF)
fault('read-through-undef-element', ['my $r = [undef];', 'say(scalar(keys $r->[0]->%*));'], UNDEF_REF)
fault('read-through-missing-deep', ['my $r = {a => {}};', 'my $n = $r->{a}{b}->$#*;'], UNDEF_REF)
fault('read-a-hash-as-an-array', ['my $r = {};', 'my @x = $r->@*;'], NOT_ARRAY)
fault('read-an-array-as-a-hash', ['my $r = [1, 2];', 'my %x = %{$r};'], NOT_HASH)
fault('read-a-number', ['my $r = 5;', 'say(scalar($r->@*));'], NOT_ARRAY)
fault('read-a-string', ['my $r = "a";', 'my @k = sort keys $r->%*;'], NOT_HASH)
fault('last-index-of-a-hash', ['my $r = {a => 1};', 'say($r->$#*);'], NOT_ARRAY)
fault('slice-of-the-other-kind', ['my $r = [1];', 'my @x = $r->@{"a"};'], NOT_HASH)
fault('read-a-call-giving-undef', ['sub f() {', '    return undef;', '}', 'my @x = f()->@*;'], UNDEF_REF)
# A store through what is defined and not the reference wanted (T234).
fault('push-through-a-hash', ['my $r = {};', 'push $r->@*, 1;'], NOT_ARRAY)
fault('push-through-empty-string', ['my $r = "";', 'push @{$r}, 1;'], NOT_ARRAY)
fault('push-through-false', ['my $r = false;', 'unshift $r->@*, 1;'], NOT_ARRAY)
fault('splice-through-a-number', ['my $r = [5];', 'splice($r->[0]->@*, 0, 0, 1);'], NOT_ARRAY)
fault('assign-through-the-other-kind', ['my $r = [];', '$r->%* = (a => 1);'], NOT_HASH)
fault('slice-store-through-the-other-kind', ['my $r = {};', '$r->@[0] = (1);'], NOT_ARRAY)
fault('hop-of-the-other-kind', ['my $r = {a => [1]};', 'push $r->{a}{b}->@*, 1;'], NOT_HASH)
# Only a variable or an element is made (T252); a read-only one holding
# undef is not made either (T250).
fault('push-through-a-call', ['sub f() {', '    return undef;', '}', 'push f()->@*, 1;'], UNDEF_REF)
fault('push-through-a-choice', ['my ($r, $s);', 'my $c = 1;', 'push @{ $c ? $r : $s }, 1;'], UNDEF_REF)
fault('assign-through-or', ['my ($r, $s);', '($r || $s)->@* = (1);'], UNDEF_REF)
fault('push-through-loop-variable', ['my @l = (undef);', 'for my $x (@l) {', '    push $x->@*, 1;', '}'], UNDEF_REF, 2)
fault('assign-through-it', ['my @m = (undef);', '$_->@* = (1) for @m;'], UNDEF_REF)
fault('push-through-it-in-a-map', ['my @m = (undef);', 'my @n = map { push $_->@*, 1 } @m;'], UNDEF_REF)
# The odd list (T244) and before the start.
fault('odd-hash-assigned', ['my $r;', '$r->%* = (1, 2, 3);'], ODD)
fault('odd-hash-assigned-braces', ['my $r = {};', '%{$r} = ("a");'], ODD)
fault('slice-store-before-the-start', ['my $r = [1];', '$r->@[-3] = (1);'], BEFORE)
fault('splice-past-the-end', ['my $r = [1];', 'splice($r->@*, 3, 0, 1);'], SPLICE_PAST)
# The freeze is the container's, whatever reaches it (T237, D114, T251).
fault('frozen-push', ['my $r = [1, 2];', 'my $s = $r;', 'for my $x ($r->@*) {', '    push $s->@*, 3;', '    last;', '}'], FROZEN, 3)
fault('frozen-store', ['my $r = [1, 2];', 'my $s = $r;', 'for my $x (@{$r}) {', '    $s->[0] = 3;', '    last;', '}'], FROZEN, 3)
fault('frozen-pop', ['my $r = [1, 2];', 'my $s = $r;', 'for my $x ($r->@*) {', '    my $y = pop $s->@*;', '    last;', '}'], FROZEN, 3)
fault('frozen-shift', ['my $r = [1, 2];', 'my $s = $r;', 'for my $x ($r->@*) {', '    my $y = shift @{$s};', '    last;', '}'], FROZEN, 3)
fault('frozen-unshift', ['my $r = [1, 2];', 'my $s = $r;', 'for my $x ($r->@*) {', '    unshift $s->@*, 0;', '    last;', '}'], FROZEN, 3)
fault('frozen-splice', ['my $r = [1, 2];', 'my $s = $r;', 'for my $x ($r->@*) {', '    splice($s->@*, 0, 1);', '    last;', '}'], FROZEN, 3)
fault('frozen-assign', ['my $r = [1, 2];', 'my $s = $r;', 'for my $x ($r->@*) {', '    $s->@* = ();', '    last;', '}'], FROZEN, 3)
fault('frozen-slice-store', ['my $r = [1, 2];', 'my $s = $r;', 'for my $x ($r->@*) {', '    $s->@[0] = (5);', '    last;', '}'], FROZEN, 3)
fault('frozen-through-a-name', ['my @a = (1, 2);', 'my $r = \\@a;', 'for my $x ($r->@*) {', '    push @a, 3;', '    last;', '}'], FROZEN, 3)
fault('frozen-named-through-a-reference', ['my @a = (1, 2);', 'my $r = \\@a;', 'for my $x (@a) {', '    push $r->@*, 3;', '    last;', '}'], FROZEN, 3)
fault('frozen-hash-values', ['my $h = {a => 1};', 'my $g = $h;', 'for my $v (values $h->%*) {', '    $g->{b} = 2;', '    last;', '}'], HFROZEN, 3)
fault('frozen-hash-whole', ['my $h = {a => 1};', 'my $g = $h;', 'for my $v (%{$h}) {', '    delete $g->{a};', '    last;', '}'], HFROZEN, 3)
fault('frozen-hash-assign', ['my $h = {a => 1};', 'my $g = $h;', 'for my $v (values $h->%*) {', '    $g->%* = ();', '    last;', '}'], HFROZEN, 3)
fault('frozen-hash-delete-slice', ['my $h = {a => 1};', 'my $g = $h;', 'for my $v ($h->@{"a"}) {', '    delete $g->@{"a"};', '    last;', '}'], HFROZEN, 3)
fault('frozen-on-the-way', ['my $h = {l => [1, 2]};', 'my $g = $h;', 'for my $x ($h->{l}->@*) {', '    $g->{m} = 1;', '    last;', '}'], HFROZEN, 3)
fault('frozen-in-a-map', ['my $r = [1, 2];', 'my $s = $r;', 'my @l = map { push $s->@*, 3 } $r->@*;'], FROZEN)
fault('frozen-in-a-grep', ['my $r = [1, 2];', 'my $s = $r;', 'my @l = sort { $a <=> $b } grep { push $s->@*, 1 } @{$r};'], FROZEN)
fault('frozen-in-a-sort', ['my $r = [2, 1];', 'my $s = $r;', 'my @l = sort { push $s->@*, 0; $a <=> $b } $r->@*;'], FROZEN)
fault('frozen-from-a-sub', ['my $r = [1, 2];', 'sub grow($s) {', '    push $s->@*, 3;', '    return;', '}', 'for my $x ($r->@*) {', '    grow($r);', '    last;', '}'], FROZEN, 2)
# A slice past the end, where perl would make it (T161, T216).
fault('slice-past-the-end-in-a-loop', ['my $r = [1];', 'for my $x ($r->@[0, 3]) {', '}'], SLICE_PAST, 1)
fault('slice-no-key-in-a-loop', ['my $r = {a => 1};', 'for my $x ($r->@{"a", "b"}) {', '}'], KEY_PAST, 1)
fault('slice-past-the-end-in-a-map', ['my $r = [1];', 'my @l = map { $_ } $r->@[2];'], SLICE_PAST)
fault('slice-past-the-end-in-arguments', ['my $r = [1];', 'sub f(@x) {', '    return;', '}', 'f($r->@[0, 1]);'], SLICE_PAST)
# A reference among the values, where a string is wanted (D112).
fault('joined-reference', ['my $r = [[1]];', 'say(join(",", $r->@*));'], STRING)
fault('sorted-references', ['my $r = [[1], [2]];', 'my @s = sort $r->@*;'], STRING)

def commands():
    out = []
    for number, (name, _) in SAME.items():
        out.append(f'    python3 t/models/whole.py --program {number} > t/{number}-{name}.pl')
        out.append(f'    python3 t/models/whole.py {number} > t/{number}-{name}.expected')
    for n, (name, _, _, _) in enumerate(FAULTS):
        number = 2020 + n
        out.append(f'    python3 t/models/whole.py --program {number} > t/{number}-fault-whole-{name}.pl')
        out.append(f'    python3 t/models/whole.py {number} > t/{number}-fault-whole-{name}.expected')
    return '\n'.join(out) + '\n'

HEAD = '# model: t/models/whole.py\nuse v5.42;\n'

def main(argv):
    if argv == ['--commands']:
        sys.stdout.write(commands())
        return
    assert commands() in __doc__, 'the commands in the docstring are not the tests: python3 t/models/whole.py --commands'
    want_program = argv[0] == '--program'
    number = argv[-1]
    if number in SAME:
        name, case = SAME[number]
        p = Prog()
        case(p)
        indent = 0
        body = []
        for line in SHOW + p.subs + p.lines:
            for l in line.split('\n'):
                t = l.strip()
                if t.startswith('}'):
                    indent -= 1
                body.append('    ' * indent + t)
                if t.endswith('{'):
                    indent += 1
        sys.stdout.write(HEAD + '\n'.join(body) + '\n' if want_program else '\n'.join(p.out) + '\n')
        return
    n = int(number) - 2020
    name, lines, message, at = FAULTS[n]
    program = '# kind: fault\n' + HEAD + 'say(1);\n' + '\n'.join(lines) + '\nsay(2);\n'
    if want_program:
        sys.stdout.write(program)
        return
    # The line of the statement that faults: the last of `lines`, or the
    # one `at` says (a loop's own, for what its list does).
    line = 5 + (at if at is not None else len(lines) - 1)
    sys.stdout.write(f'1\nfault: {message} at t/{number}-fault-whole-{name}.pl line {line}.\nexit: 1\n')

if __name__ == '__main__':
    main(sys.argv[1:])
