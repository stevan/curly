// The outside (step 21; D211 to D218): the program's arguments, its
// environment, its stdin, the status it exits with, and `printf` to a
// handle. rt.c includes this file, after format.c and unwind.c, whose
// static functions it uses.
//
// What comes from outside is bytes. perl makes each byte a character
// unless `use open ':std', ':encoding(UTF-8)'` said its standard streams
// are UTF-8, and then reads stdin as UTF-8 and warns of every byte that is
// not (T502, T503); `@ARGV` and `%ENV` are bytes either way.

// A string of `n` bytes, each a character: one byte past ASCII is two of
// UTF-8. The one allocation.
static rt_value bytes_as_characters(rt_ctx *cx, const char *b, size_t n) {
    uint64_t high = 0;
    for (size_t k = 0; k < n; k++) high += (unsigned char)b[k] >= 0x80;
    char *out;
    const rt_str *s = str_new(cx, n + high, n, &out);
    for (size_t k = 0; k < n; k++) {
        unsigned char c = (unsigned char)b[k];
        if (c < 0x80) {
            *out++ = (char)c;
        } else {
            *out++ = (char)(0xC0 | (c >> 6));
            *out++ = (char)(0x80 | (c & 0x3F));
        }
    }
    return rt_string(s);
}

// How many characters `n` bytes of UTF-8 are, or -1 where perl's
// `:encoding(UTF-8)` would not take them: a byte that begins nothing, a
// sequence cut short (by the end of the line or of the input, where perl
// drops the character in silence), an overlong form, a surrogate, past
// U+10FFFF, or a noncharacter (T502).
static int64_t utf8_characters(const unsigned char *b, size_t n) {
    int64_t chars = 0;
    for (size_t k = 0; k < n; chars++) {
        unsigned char c = b[k];
        if (c < 0x80) {
            k++;
            continue;
        }
        size_t more = c >= 0xC2 && c <= 0xDF ? 1 : c >= 0xE0 && c <= 0xEF ? 2 : c >= 0xF0 && c <= 0xF4 ? 3 : 0;
        if (more == 0) return -1;
        uint32_t u = c & (0x3F >> more);
        for (size_t j = 1; j <= more; j++) {
            if (k + j >= n || (b[k + j] & 0xC0) != 0x80) return -1;
            u = (u << 6) | (b[k + j] & 0x3F);
        }
        if ((more == 2 && u < 0x800) || (more == 3 && u < 0x10000) || u > 0x10FFFF) return -1;
        if (u >= 0xD800 && u <= 0xDFFF) return -1;
        if ((u >= 0xFDD0 && u <= 0xFDEF) || (u & 0xFFFE) == 0xFFFE) return -1;
        k += more + 1;
    }
    return chars;
}

// The next line of stdin, its newline kept, or the last without one; undef
// at the end of the input, and every time after (D211). The line's bytes
// are kept in the context between calls, so that a fault leaves nothing
// to free.
rt_value rt_readline(rt_ctx *cx) {
    size_t n = 0;
    int c;
    while ((c = getc(stdin)) != EOF) {
        if (n == cx->read_room) {
            size_t room = cx->read_room ? 2 * cx->read_room : 256;
            char *grown = realloc(cx->read_buf, room);
            if (grown == NULL) rt_fault(cx, "out of memory");
            cx->read_buf = grown;
            cx->read_room = room;
        }
        cx->read_buf[n++] = (char)c;
        if (c == '\n') break;
    }
    if (n == 0) return rt_undef();
    cx->stdin_lines += 1;
    if (!cx->out_utf8) return bytes_as_characters(cx, cx->read_buf, n);
    int64_t chars = utf8_characters((const unsigned char *)cx->read_buf, n);
    if (chars < 0) rt_fault(cx, "malformed UTF-8 read");
    char *out;
    const rt_str *s = str_new(cx, n, (uint64_t)chars, &out);
    memcpy(out, cx->read_buf, n);
    return rt_string(s);
}

// Where a list is wanted: every line that is left (T508). Each line is
// added before the next is made, and the list is in a slot.
void rt_list_add_lines(rt_ctx *cx, rt_value list) {
    for (;;) {
        rt_value line = rt_readline(cx);
        if (line.tag == RT_TAG_UNDEF) return;
        rt_list_add(cx, list, line);
    }
}

// `eof(STDIN)` (D214): whether a read would find nothing. A character is
// looked at and put back.
rt_value rt_eof_stdin(rt_ctx *cx) {
    (void)cx;
    int c = getc(stdin);
    if (c == EOF) return rt_bool(1);
    ungetc(c, stdin);
    return rt_bool(0);
}

// `@ARGV` (D215), filled into the array in `*argv`, a slot: each argument
// a string of its bytes.
void rt_argv(rt_ctx *cx, rt_value *argv) {
    for (int k = 1; k < cx->argc; k++) {
        rt_value arg = bytes_as_characters(cx, cx->argv[k], strlen(cx->argv[k]));
        rt_list_add(cx, *argv, arg);
    }
}

// `%ENV` (D216), filled into the hash in `*env`, a slot, in the order the
// environment has it, and then read-only. The name is kept in a slot of a
// frame of its own while the value is made.
extern char **environ;
void rt_environ(rt_ctx *cx, rt_value *env) {
    rt_value f[1];
    rt_frame frame;
    rt_enter(cx, &frame, f, 1);
    for (char **e = environ; *e != NULL; e++) {
        const char *eq = strchr(*e, '=');
        if (eq == NULL) continue;
        f[0] = bytes_as_characters(cx, *e, (size_t)(eq - *e));
        rt_value value = bytes_as_characters(cx, eq + 1, strlen(eq + 1));
        rt_helem_store(cx, *env, f[0], value);
    }
    rt_leave(cx, &frame);
    env->as.a->frozen |= RT_FROZEN_READONLY;
}

// `exit` (D217): the low eight bits of a whole number, what was printed
// flushed first. Not a `die`: no `try` sees it.
void rt_exit(rt_ctx *cx, rt_value status) {
    int64_t n = whole_number(cx, numeric(cx, status));
    fflush(stdout);
    fflush(stderr);
    exit((int)((uint64_t)n & 255));
}

// `printf STDERR FORMAT, LIST` (D218): what `sprintf` makes, written as
// `print STDERR` writes it (T500).
void rt_printf_err(rt_ctx *cx, rt_value list) {
    rt_value made = format(cx, list, "printf");
    emit_checked(cx, made, 0, 0);
    fflush(stdout);
    scratch none;
    const rt_str *s = to_str(cx, made, &none);
    fwrite(s->bytes, 1, s->len, stderr);
    fflush(stderr);
}
