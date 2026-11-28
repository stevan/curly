// Files and handles (step 21b; D270 to D283). rt.c includes this file,
// after io.c, whose reading it uses.
//
// **A handle is a reference** (D271): `RT_TAG_GLOB`, with a block of the
// collector's for its payload, an array's that holds nothing. What the
// handle is for, the file, is an `rt_file` on the context's list, found by
// its block. A collection closes the file of every handle it did not
// reach, between its mark and its sweep (`files_reap`), and the program's
// end closes the rest (`files_release`): perl closes a file the moment
// its handle's last reference goes, and nothing a program reads can tell
// the difference, because no file is open twice when one of the two is
// for writing (D276).
//
// **perl's errno** (D272) is `cx->perl_errno`: an `open` sets it, and a
// read that meets the end of its input (io.c). `cx->open_failed` says
// the last `open` failed, which is when `$!` may be read (D273).

enum { FILE_CLOSED = 0, FILE_READ = 1, FILE_WRITE = 2 };

typedef struct rt_file {
    struct rt_file *next;
    rt_array *block;        // the handle's
    FILE *f;                // NULL when it is not open
    int mode;
    int ended;              // the end was met: no read looks again (T681)
    uint64_t lines;         // perl's `$.`: `close` sets it to 0, an `open` again does not (T685)
    dev_t dev;              // which file it is, while it is open
    ino_t ino;
} rt_file;

#define NOT_HANDLE "not a file handle"

// The file of a handle. The one found is moved to the front: a program
// reads the same handle again and again.
static rt_file *file_of(rt_ctx *cx, rt_value handle) {
    if (handle.tag != RT_TAG_GLOB) {
        if (handle.tag == RT_TAG_UNDEF) rt_fault(cx, "undef where a file handle is wanted");
        if (!a_scalar(handle.tag)) rt_fault(cx, "not a value");
        rt_fault(cx, NOT_HANDLE);
    }
    if (handle.as.a->dead) rt_internal(cx, "a file handle was used after it was collected");
    for (rt_file **link = &cx->files; *link; link = &(*link)->next) {
        rt_file *f = *link;
        if (f->block != handle.as.a) continue;
        *link = f->next;
        f->next = cx->files;
        cx->files = f;
        return f;
    }
    rt_internal(cx, "a file handle that has no file");
}

// A file closed: what was written to it written. Whether that worked is
// the caller's to ask.
static int file_shut(rt_file *f) {
    if (f->f == NULL) return 0;
    int failed = ferror(f->f);
    if (fclose(f->f) != 0) failed = 1;
    f->f = NULL;
    f->mode = FILE_CLOSED;
    f->ended = 0;
    return failed && 1;
}

static void files_release(rt_ctx *cx) {
    while (cx->files) {
        rt_file *f = cx->files;
        cx->files = f->next;
        file_shut(f);
        free(f);
    }
    cx->last_file = NULL;
}

// Between a collection's mark and its sweep: the handles not reached.
static void files_reap(rt_ctx *cx) {
    rt_file **link = &cx->files;
    while (*link) {
        rt_file *f = *link;
        if (f->block == NULL || ((rt_block *)f->block - 1)->marked & REACHED) {
            link = &f->next;
            continue;
        }
        *link = f->next;
        // The handle read last, gone: whether perl still names it in a
        // message is not known (D279).
        if (cx->last_read == 2 && cx->last_file == f->block) {
            cx->last_read = f->lines != 0 ? 3 : 0;
            cx->last_file = NULL;
        }
        file_shut(f);
        free(f);
    }
}

static uint64_t file_lines(rt_ctx *cx) {
    if (cx->last_read == 3) return 1;
    for (rt_file *f = cx->files; f; f = f->next) if (f->block == cx->last_file) return f->lines;
    return 0;
}

uint64_t rt_file_count(rt_ctx *cx) {
    uint64_t n = 0;
    for (rt_file *f = cx->files; f; f = f->next) n += f->f != NULL;
    return n;
}

// A new handle, not open. The file's record is on the context's list
// before the handle is allocated, so that a fault there leaves nothing
// behind; a collection there finds a record with no handle yet, and
// leaves it be.
rt_value rt_handle_new(rt_ctx *cx) {
    rt_file *f = calloc(1, sizeof *f);
    if (f == NULL) rt_fault(cx, "out of memory");
    f->next = cx->files;
    cx->files = f;
    rt_value v = rt_array_new(cx);
    v.tag = RT_TAG_GLOB;
    f->block = v.as.a;
    return v;
}

// What `open` leaves in its variable (D271): a new handle where it held
// undef, the handle it held, and a fault for anything else, as perl dies
// (T685).
rt_value rt_handle(rt_ctx *cx, rt_value v) {
    if (v.tag == RT_TAG_UNDEF) return rt_handle_new(cx);
    if (v.tag == RT_TAG_GLOB) return v;
    if (!a_scalar(v.tag)) rt_fault(cx, "not a value");
    rt_fault(cx, "open's variable holds what is not a file handle");
}

// Whether the program has `path`'s file open in a way that an `open` for
// `mode` may not join (D276). (The handle being opened is closed by now.)
static int open_twice(rt_ctx *cx, const char *path, int mode) {
    struct stat st;
    if (stat(path, &st) != 0) return 0;
    for (rt_file *g = cx->files; g; g = g->next) {
        if (g->f == NULL || g->dev != st.st_dev || g->ino != st.st_ino) continue;
        if (g->mode == FILE_WRITE || mode == FILE_WRITE) return 1;
    }
    return 0;
}

static rt_value file_open(rt_ctx *cx, rt_value path, rt_value handle, int mode, int flags) {
    rt_file *f = file_of(cx, handle);
    // The name, as bytes (D275): perl's bytes for a character past ASCII
    // are by the string's past, and a NUL ends the name to the system.
    scratch number;
    const rt_str *s = to_str(cx, path, &number);
    if (s->len != s->chars) rt_fault(cx, "a character past ASCII in a file's name");
    if (memchr(s->bytes, 0, s->len) != NULL) rt_fault(cx, "a NUL in a file's name");
    // (Kept in the context's buffer for a line, so that a fault leaves
    // nothing to free.)
    if (s->len + 1 > cx->read_room) {
        char *grown = realloc(cx->read_buf, s->len + 1);
        if (grown == NULL) rt_fault(cx, "out of memory");
        cx->read_buf = grown;
        cx->read_room = s->len + 1;
    }
    char *name = cx->read_buf;
    memcpy(name, s->bytes, s->len);
    name[s->len] = '\0';
    // perl closes what the handle had open first (T685), and the count of
    // lines goes on.
    if (file_shut(f)) rt_fault(cx, "write to a file failed");
    if (open_twice(cx, name, mode)) {
        // A handle nothing holds is closed by a collection, as perl closed
        // it when it was dropped.
        rt_collect(cx);
        if (open_twice(cx, name, mode)) rt_fault(cx, "open of a file the program has open, one of the two for writing");
    }
    int fd = open(name, flags | O_CLOEXEC, 0666);
    if (fd < 0 && (errno == EMFILE || errno == ENFILE)) {
        // Too many files open: the ones nothing holds are closed.
        rt_collect(cx);
        fd = open(name, flags | O_CLOEXEC, 0666);
    }
    // An `open` sets errno either way (D272, T680), and a number that
    // underflowed before it shows no more (D151).
    cx->underflowed = 0;
    if (fd < 0) {
        cx->perl_errno = errno;
        cx->open_failed = 1;
        return rt_undef();
    }
    struct stat st;
    if (fstat(fd, &st) != 0 || !S_ISREG(st.st_mode)) {
        close(fd);
        rt_fault(cx, "open of what is not a plain file");
    }
    // perl asks whether the file is a terminal, and what that leaves in
    // errno is what an uncaught `die` exits with: ENOTTY (T680).
    errno = 0;
    if (!isatty(fd)) cx->perl_errno = errno;
    cx->open_failed = 0;
    f->f = fdopen(fd, mode == FILE_READ ? "r" : "w");
    if (f->f == NULL) {
        close(fd);
        rt_fault(cx, "out of memory");
    }
    f->mode = mode;
    f->ended = 0;
    f->dev = st.st_dev;
    f->ino = st.st_ino;
    return rt_int(1);
}

rt_value rt_open_read(rt_ctx *cx, rt_value handle, rt_value path) {
    return file_open(cx, path, handle, FILE_READ, O_RDONLY);
}

rt_value rt_open_write(rt_ctx *cx, rt_value handle, rt_value path) {
    return file_open(cx, path, handle, FILE_WRITE, O_WRONLY | O_CREAT | O_TRUNC);
}

rt_value rt_open_append(rt_ctx *cx, rt_value handle, rt_value path) {
    return file_open(cx, path, handle, FILE_WRITE, O_WRONLY | O_CREAT | O_APPEND);
}

// `close` (D277, D283): 1. perl gives false for a handle that is not
// open, in silence (T687): a fault. The count of lines is 0 again.
rt_value rt_close(rt_ctx *cx, rt_value handle) {
    rt_file *f = file_of(cx, handle);
    if (f->f == NULL) rt_fault(cx, "close of a file handle that is not open");
    f->lines = 0;
    if (file_shut(f)) rt_fault(cx, "write to a file failed");
    return rt_int(1);
}

static rt_file *file_to_read(rt_ctx *cx, rt_value handle, const char *what) {
    rt_file *f = file_of(cx, handle);
    char said[96];
    if (f->f == NULL) {
        snprintf(said, sizeof said, "%s of a file handle that is not open", what);
        rt_fault(cx, said);
    }
    if (f->mode != FILE_READ) {
        snprintf(said, sizeof said, "%s of a file handle opened for writing", what);
        rt_fault(cx, said);
    }
    // The handle read last, which a message asks of (D279).
    cx->last_read = 2;
    cx->last_file = f->block;
    return f;
}

rt_value rt_readline_fh(rt_ctx *cx, rt_value handle) {
    rt_file *f = file_to_read(cx, handle, "read");
    return read_line(cx, f->f, &f->ended, &f->lines);
}

void rt_list_add_lines_fh(rt_ctx *cx, rt_value list, rt_value handle) {
    for (;;) {
        rt_value line = rt_readline_fh(cx, handle);
        if (line.tag == RT_TAG_UNDEF) return;
        rt_list_add(cx, list, line);
    }
}

rt_value rt_eof_fh(rt_ctx *cx, rt_value handle) {
    rt_file *f = file_to_read(cx, handle, "eof");
    return rt_bool(at_end(f->f, &f->ended));
}

// The handle `print` is given, looked at before its list is worked out
// (T683): what it gives is kept, so a store to the variable in the list
// changes nothing.
rt_value rt_handle_out(rt_ctx *cx, rt_value handle) {
    file_of(cx, handle);
    return handle;
}

static rt_file *file_to_write(rt_ctx *cx, rt_value handle) {
    rt_file *f = file_of(cx, handle);
    if (f->f == NULL) rt_fault(cx, "write to a file handle that is not open");
    if (f->mode != FILE_WRITE) rt_fault(cx, "write to a file handle opened for reading");
    return f;
}

// Every value looked at before any is written, as `say` does; a file's
// characters are stdout's (D280).
//
// The handle is the list's first item: it was worked out first, and what
// it gave is kept there (T683).
static rt_file *file_first(rt_ctx *cx, rt_array *a) {
    if (a->count == 0 || a->items[0].tag != RT_TAG_GLOB) rt_internal(cx, "a list written to a file handle that does not begin with one");
    return file_to_write(cx, a->items[0]);
}

static void emit_list_file(rt_ctx *cx, rt_value list, int newline) {
    rt_array *a = array_of(cx, list);
    rt_file *f = file_first(cx, a);
    for (uint64_t n = 1; n < a->count; n++) emit_checked(cx, a->items[n], 0, 0);
    for (uint64_t n = 1; n < a->count; n++) {
        char buf[32];
        rt_value v = a->items[n];
        if (v.tag == RT_TAG_INT || v.tag == RT_TAG_NUM) {
            int k = format_number(cx, v, buf);
            fwrite(buf, 1, (size_t)k, f->f);
        } else {
            scratch none;
            const rt_str *s = to_str(cx, v, &none);
            fwrite(s->bytes, 1, s->len, f->f);
        }
    }
    if (newline) putc('\n', f->f);
    if (ferror(f->f)) rt_fault(cx, "write to a file failed");
}

void rt_say_fh_list(rt_ctx *cx, rt_value list) {
    emit_list_file(cx, list, 1);
}

void rt_print_fh_list(rt_ctx *cx, rt_value list) {
    emit_list_file(cx, list, 0);
}

void rt_printf_fh(rt_ctx *cx, rt_value list) {
    rt_file *f = file_first(cx, array_of(cx, list));
    rt_value made = format_from(cx, list, "printf", 1);
    emit_checked(cx, made, 0, 0);
    scratch none;
    const rt_str *s = to_str(cx, made, &none);
    // (The allocation may have run a collection: the handle is in a slot,
    // and its file is where it was.)
    fwrite(s->bytes, 1, s->len, f->f);
    if (ferror(f->f)) rt_fault(cx, "write to a file failed");
}

// `$!` (D273): the system's words for why the last `open` failed, and a
// fault when the last `open` did not fail, or none was tried, or errno has
// moved since: perl's `$!` is then whatever was left there.
rt_value rt_errstr(rt_ctx *cx) {
    if (!cx->open_failed || cx->underflowed) rt_fault(cx, "$! where no open has just failed");
    const char *text = strerror(cx->perl_errno);
    return bytes_as_characters(cx, text, strlen(text));
}
