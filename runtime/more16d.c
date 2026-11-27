// Step 16d's runtime: what the census's reading asked for and D120 left.
// Included by rt.c, after the rest, so that its helpers are in scope.

// `$#a = N;` (D251): the array made N + 1 long, cut or grown with undefs.
// N is a whole number as an index is (cut toward zero), from -1 up: perl
// empties the array in silence for anything below -1, which is no
// spelling of an empty array a program means.
void rt_last_index_store(rt_ctx *cx, rt_value array, rt_value n) {
    int64_t i = whole_of(cx, n);
    if (i < -1) rt_fault(cx, "an array's last index set below -1");
    rt_array *a = changing(cx, array);
    uint64_t count = (uint64_t)(i + 1);
    if (count > ARRAY_MAX) rt_fault(cx, "array too long");
    if (count <= a->count) {
        a->count = count;
        return;
    }
    reserve(cx, a, count);
    while (a->count < count) a->items[a->count++] = rt_undef();
}

// ---- case past ASCII (step 16d, D257)

#include "cases16d.c"

// What `which` of perl's case functions makes of one character, past
// ASCII: the row of its table, or NULL where the character is itself.
enum { CASE_UC, CASE_LC, CASE_UCFIRST, CASE_LCFIRST };

static const rt_case *case_row(int which, uint32_t c) {
    const rt_case *t = which == CASE_UC ? case_uc : which == CASE_LC ? case_lc : which == CASE_UCFIRST ? case_ucfirst : case_lcfirst;
    size_t n = which == CASE_UC ? sizeof case_uc / sizeof *case_uc : which == CASE_LC ? sizeof case_lc / sizeof *case_lc
        : which == CASE_UCFIRST ? sizeof case_ucfirst / sizeof *case_ucfirst : sizeof case_lcfirst / sizeof *case_lcfirst;
    size_t lo = 0, hi = n;
    while (lo < hi) {
        size_t mid = lo + (hi - lo) / 2;
        if (t[mid].from == c) return &t[mid];
        if (t[mid].from < c) lo = mid + 1;
        else hi = mid;
    }
    return NULL;
}

static int utf8_size(uint32_t c) {
    return c < 0x80 ? 1 : c < 0x800 ? 2 : c < 0x10000 ? 3 : 4;
}

static int utf8_put(char *to, uint32_t c) {
    int size = utf8_size(c);
    if (size == 1) {
        to[0] = (char)c;
    } else {
        to[0] = (char)((0xF00 >> size & 0xFF) | c >> 6 * (size - 1));
        for (int k = 1; k < size; k++) to[k] = (char)(0x80 | (c >> 6 * (size - 1 - k) & 0x3F));
    }
    return size;
}

// One character as `which` maps it: written at `to` when it is not NULL;
// the bytes and characters it makes are added to the counts.
static void case_one(int which, uint32_t c, char *to, uint64_t *bytes, uint64_t *chars) {
    uint32_t out[3];
    int count = 1;
    out[0] = c;
    if (c < 0x80) {
        if ((which == CASE_UC || which == CASE_UCFIRST) && c >= 'a' && c <= 'z') out[0] = c - 'a' + 'A';
        if ((which == CASE_LC || which == CASE_LCFIRST) && c >= 'A' && c <= 'Z') out[0] = c - 'A' + 'a';
    } else {
        const rt_case *row = case_row(which, c);
        if (row != NULL) {
            count = row->count;
            for (int k = 0; k < count; k++) out[k] = row->to[k];
        }
    }
    for (int k = 0; k < count; k++) {
        int size = to != NULL ? utf8_put(to + *bytes, out[k]) : utf8_size(out[k]);
        *bytes += (uint64_t)size;
        *chars += 1;
    }
}

// `uc`, `lc`, `ucfirst` and `lcfirst` of a whole string, by perl's own
// tables (a string mapped a character at a time, as perl maps it), counted
// and then written, one allocation. perl's `uc` of two U+0345 together
// makes one U+0399 (T664): a fault, the one place a character's
// neighbours change what it becomes.
static rt_value case_string(rt_ctx *cx, rt_value a, int which) {
    scratch x;
    const rt_str *s = to_str(cx, a, &x);
    int first = which == CASE_UCFIRST || which == CASE_LCFIRST;
    uint64_t bytes = 0, chars = 0;
    uint32_t before = 0;
    for (uint64_t at = 0; at < s->len;) {
        int size;
        uint32_t c = decode(s->bytes + at, &size);
        if (which == CASE_UC && c == 0x345 && before == 0x345) rt_fault(cx, "uc of two U+0345 together: perl makes them one character");
        before = c;
        if (first && at > 0) {
            bytes += (uint64_t)size;
            chars += 1;
        } else {
            case_one(which, c, NULL, &bytes, &chars);
        }
        at += (uint64_t)size;
    }
    char *out;
    const rt_str *changed = str_new(cx, bytes, chars, &out);
    s = alive(cx, s);
    uint64_t made = 0, counted = 0;
    for (uint64_t at = 0; at < s->len;) {
        int size;
        uint32_t c = decode(s->bytes + at, &size);
        if (first && at > 0) {
            memcpy(out + made, s->bytes + at, (size_t)size);
            made += (uint64_t)size;
        } else {
            case_one(which, c, out, &made, &counted);
        }
        at += (uint64_t)size;
    }
    return rt_string(changed);
}

// `\Q` (step 16d, D256): a backslash before every character that is not
// a letter, a digit or `_` in ASCII, and before the characters past ASCII
// perl's `quotemeta` quotes, which its table gives.
static int quoted(uint32_t c) {
    if (c < 0x80) return !((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_');
    size_t lo = 0, hi = sizeof case_quoted / sizeof *case_quoted;
    while (lo < hi) {
        size_t mid = lo + (hi - lo) / 2;
        if (c < case_quoted[mid][0]) hi = mid;
        else if (c > case_quoted[mid][1]) lo = mid + 1;
        else return 1;
    }
    return 0;
}

rt_value rt_quotemeta(rt_ctx *cx, rt_value a) {
    scratch x;
    const rt_str *s = to_str(cx, a, &x);
    uint64_t more = 0;
    for (uint64_t at = 0; at < s->len;) {
        int size;
        more += quoted(decode(s->bytes + at, &size));
        at += (uint64_t)size;
    }
    char *out;
    const rt_str *q = str_new(cx, s->len + more, s->chars + more, &out);
    s = alive(cx, s);
    uint64_t made = 0;
    for (uint64_t at = 0; at < s->len;) {
        int size;
        if (quoted(decode(s->bytes + at, &size))) out[made++] = '\\';
        memcpy(out + made, s->bytes + at, (size_t)size);
        made += (uint64_t)size;
        at += (uint64_t)size;
    }
    return rt_string(q);
}

// ---- `substr` of four (step 16d, D254)

// The string `substr($s, OFFSET, LENGTH, REPLACEMENT)` leaves in `$s`: the
// piece three arguments would take, by the same rule (a start below zero
// counts from the end, and so does a length; outside the string a fault,
// where perl dies with four), and the replacement in its place.
rt_value rt_substr4(rt_ctx *cx, rt_value a, rt_value offset, rt_value count, rt_value put) {
    scratch x, y;
    const rt_str *s = to_str(cx, a, &x);
    int64_t off = whole_number(cx, numeric(cx, offset));
    int64_t n = whole_number(cx, numeric(cx, count));
    const rt_str *r = to_str(cx, put, &y);
    int64_t size = (int64_t)s->chars;
    int64_t start = off < 0 ? off + size : off;
    int64_t end = size;
    if (n >= 0 && __builtin_add_overflow(start, n, &end)) end = INT64_MAX;
    if (n < 0) end = size + n;
    if (start > size || (start < 0 && end < 0)) rt_fault(cx, "substr outside of string");
    if (start < 0) start = 0;
    if (end > size) end = size;
    if (end < start) end = start;
    uint64_t from = offset_of(s, (uint64_t)start);
    uint64_t to = offset_of(s, (uint64_t)end);
    uint64_t len = from + r->len + (s->len - to);
    uint64_t chars = (uint64_t)start + r->chars + ((uint64_t)size - (uint64_t)end);
    char *bytes;
    const rt_str *made = str_new(cx, len, chars, &bytes);
    s = alive(cx, s);
    r = alive(cx, r);
    memcpy(bytes, s->bytes, from);
    memcpy(bytes + from, r->bytes, r->len);
    memcpy(bytes + from + r->len, s->bytes + to, s->len - to);
    return rt_string(made);
}

// ---- `scalar reverse` (step 16d, D258)

// perl's `scalar reverse` of a list with nothing in it reverses `$_`
// (T672), which the language does not have there: a fault.
void rt_reverse_some(rt_ctx *cx, rt_value list) {
    if (array_of(cx, list)->count == 0) rt_fault(cx, "scalar reverse of an empty list: perl reverses $_");
}

// The characters of a string in the other order: what `scalar reverse
// LIST` makes of the list, joined with nothing first (by the caller, into a
// slot, so that this allocates once, last).
rt_value rt_reverse_string(rt_ctx *cx, rt_value a) {
    scratch x;
    const rt_str *s = to_str(cx, a, &x);
    char *bytes;
    const rt_str *made = str_new(cx, s->len, s->chars, &bytes);
    s = alive(cx, s);
    uint64_t to = s->len;
    for (uint64_t at = 0; at < s->len;) {
        int size;
        decode(s->bytes + at, &size);
        to -= (uint64_t)size;
        memcpy(bytes + to, s->bytes + at, (size_t)size);
        at += (uint64_t)size;
    }
    return rt_string(made);
}
