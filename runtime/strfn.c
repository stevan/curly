// `ucfirst`, `lcfirst`, `rindex`, and what `chomp` and `chop` make of a
// variable (step 16c; D129 to D131), which rt.c includes.

// Past ASCII by perl's own tables since step 16d (D257), in more16d.c.
rt_value rt_ucfirst(rt_ctx *cx, rt_value a) {
    return case_string(cx, a, 2);
}

rt_value rt_lcfirst(rt_ctx *cx, rt_value a) {
    return case_string(cx, a, 3);
}

// `rindex`: where `t` last begins in `s`, ending at or before the
// position plus its own length, which is then moved into the string, as
// perl has it: so a position below zero finds nothing but the empty
// string (T281). Where that sum passes the Ints perl has two answers, by
// whether the string is UTF-8 inside.
static rt_value rfind(rt_ctx *cx, rt_value a, rt_value b, int has_position, rt_value position) {
    scratch x, y;
    const rt_str *s = to_str(cx, a, &x);
    const rt_str *t = to_str(cx, b, &y);
    int64_t size = (int64_t)s->chars;
    int64_t end = size;
    if (has_position) {
        int64_t p = whole_number(cx, numeric(cx, position));
        if (__builtin_add_overflow(p, (int64_t)t->chars, &end)) rt_fault(cx, "an rindex position this far past the end has two answers in perl");
        if (end < 0) end = 0;
        if (end > size) end = size;
    }
    int64_t last = end - (int64_t)t->chars;
    if (last < 0) return rt_int(-1);
    // Bytes are compared, at the start of a character only, from the last
    // place it may begin, backwards.
    for (int64_t at = (int64_t)offset_of(s, (uint64_t)last); at >= 0; at--) {
        if (continues(s->bytes[at])) continue;
        if (memcmp(s->bytes + at, t->bytes, t->len) == 0) return rt_int((int64_t)chars_in(s, (uint64_t)at));
    }
    return rt_int(-1);
}

rt_value rt_rindex2(rt_ctx *cx, rt_value a, rt_value b) {
    return rfind(cx, a, b, 0, b);
}

rt_value rt_rindex3(rt_ctx *cx, rt_value a, rt_value b, rt_value position) {
    return rfind(cx, a, b, 1, position);
}

// What `chomp($x)` stores in `$x` (D131): a Str less the newline at its
// end, if it has one; any other value as it is, since a number's string
// has no newline and perl leaves the number (T279), and a reference too,
// whose address ends in no newline (step 13a). undef is D48's fault.
rt_value rt_chomp(rt_ctx *cx, rt_value a) {
    if (a.tag == RT_TAG_UNDEF) rt_fault(cx, "undef where a string is wanted");
    if (a.tag != RT_TAG_STR) {
        if (a.tag != RT_TAG_INT && a.tag != RT_TAG_NUM && a.tag != RT_TAG_BOOL && !rt_ref_tag(a.tag)) rt_fault(cx, "not a value");
        return a;
    }
    const rt_str *s = alive(cx, a.as.s);
    if (s->len == 0 || s->bytes[s->len - 1] != '\n') return a;
    char *bytes;
    const rt_str *less = str_new(cx, s->len - 1, s->chars - 1, &bytes);
    s = alive(cx, a.as.s);
    memcpy(bytes, s->bytes, s->len - 1);
    return rt_string(less);
}

// What `chop($x)` stores: the value made a string as `.` makes one, less
// its last character (`chop` of 1.5 is `1.`).
rt_value rt_chop(rt_ctx *cx, rt_value a) {
    scratch x;
    const rt_str *s = to_str(cx, a, &x);
    uint64_t chars = s->chars > 0 ? s->chars - 1 : 0;
    uint64_t len = offset_of(s, chars);
    char *bytes;
    const rt_str *less = str_new(cx, len, chars, &bytes);
    alive(cx, s);
    if (len > 0) memcpy(bytes, s->bytes, len);
    return rt_string(less);
}
