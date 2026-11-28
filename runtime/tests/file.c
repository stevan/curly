// Files and handles (step 21b; D276, D277, D279), for what no compiled
// program can show: that a collection closes the file of a handle nothing
// holds, and writes what was held back; that a write the system refuses is
// a fault; and what a message does once the handle read last is collected.
// The argument says which case. The files are made under build/unit, by
// the process's number, and taken away at the end.
#include <fcntl.h>
#include <inttypes.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include "rt.h"

static const char *which;
static char path[128];
static rt_str name = { 0, 0, path, RT_STR_CONSTANT };
static const rt_str TEXT = { 5, 5, "kept\n", RT_STR_CONSTANT };
static const rt_str MSG = { 3, 3, "msg", RT_STR_CONSTANT };

static int is(const char *wanted) {
    return strcmp(which, wanted) == 0;
}

// `print $handle TEXT`, as the generated code writes it: the handle the
// list's first item.
static void print_to(rt_ctx *cx, rt_value *list, rt_value handle) {
    *list = rt_array_new(cx);
    rt_list_add(cx, *list, rt_handle_out(cx, handle));
    rt_list_add(cx, *list, rt_string(&TEXT));
    rt_print_fh_list(cx, *list);
}

static void body(rt_ctx *cx) {
    rt_value f[4];
    rt_frame frame;
    rt_enter(cx, &frame, f, 4);
    cx->line = 1;
    if (is("reap")) {
        // One handle kept, one dropped with text not yet written.
        f[0] = rt_handle_new(cx);
        rt_open_write(cx, rt_string(&name), f[0]);
        print_to(cx, &f[1], f[0]);
        f[2] = rt_handle_new(cx);
        f[3] = rt_string(&name);
        printf("open: %" PRIu64 "\n", rt_file_count(cx));
        f[0] = rt_undef();
        f[1] = rt_undef();
        rt_collect(cx);
        printf("after a collection: %" PRIu64 "\n", rt_file_count(cx));
        // What it held back is in the file: another handle reads it.
        printf("opens to read: %" PRId64 "\n", rt_open_read(cx, f[3], f[2]).as.i);
        f[1] = rt_readline_fh(cx, f[2]);
        rt_print(cx, f[1]);
        printf("open: %" PRIu64 "\n", rt_file_count(cx));
        rt_close(cx, f[2]);
        printf("closed: %" PRIu64 "\n", rt_file_count(cx));
    }
    if (is("twice")) {
        // A second open of a file open for writing: a collection first,
        // which closes a handle nothing holds, and then no fault.
        f[0] = rt_handle_new(cx);
        rt_open_write(cx, rt_string(&name), f[0]);
        print_to(cx, &f[1], f[0]);
        f[0] = rt_undef();
        f[1] = rt_undef();
        f[2] = rt_handle_new(cx);
        printf("opens to read: %" PRId64 "\n", rt_open_read(cx, rt_string(&name), f[2]).as.i);
        f[1] = rt_readline_fh(cx, f[2]);
        rt_print(cx, f[1]);
        // And with the writer held, the fault.
        f[0] = rt_handle_new(cx);
        f[3] = rt_handle_new(cx);
        rt_close(cx, f[2]);
        rt_open_append(cx, rt_string(&name), f[0]);
        fflush(stdout);
        rt_open_read(cx, rt_string(&name), f[3]);
        printf("not reached\n");
    }
    if (is("write-failed")) {
        // The file's descriptor is the lowest that is free: it is closed
        // behind the handle's back, and what was held back cannot be
        // written when the handle is closed.
        int fd = open("/dev/null", O_RDONLY);
        close(fd);
        f[0] = rt_handle_new(cx);
        rt_open_write(cx, rt_string(&name), f[0]);
        print_to(cx, &f[1], f[0]);
        close(fd);
        printf("written\n");
        fflush(stdout);
        unlink(path);
        rt_close(cx, f[0]);
        printf("not reached\n");
    }
    if (is("last-read-lines") || is("last-read-none")) {
        // The handle read last is collected: a message with no newline is
        // a fault if it had given a line, and names nothing if not.
        f[0] = rt_handle_new(cx);
        rt_open_write(cx, rt_string(&name), f[0]);
        print_to(cx, &f[1], f[0]);
        rt_close(cx, f[0]);
        rt_open_read(cx, rt_string(&name), f[0]);
        f[1] = is("last-read-lines") ? rt_readline_fh(cx, f[0]) : rt_eof_fh(cx, f[0]);
        f[0] = rt_undef();
        rt_collect(cx);
        printf("open after the collection: %" PRIu64 "\n", rt_file_count(cx));
        fflush(stdout);
        unlink(path);
        f[2] = rt_array_new(cx);
        rt_list_add(cx, f[2], rt_string(&MSG));
        rt_warn(cx, f[2]);
        printf("warned\n");
    }
    fflush(stdout);
    unlink(path);
    rt_leave(cx, &frame);
}

int main(int argc, char **argv) {
    which = argc > 1 ? argv[1] : "";
    snprintf(path, sizeof path, "build/unit/file-test-%ld.txt", (long)getpid());
    name.len = name.chars = strlen(path);
    return rt_run(body, "file.pl");
}
