// The matcher's limit on steps (D232, D244), at its edge: no program can
// reach it exactly, since how many steps a pattern takes is the machine's
// own count. A program of n JMPs and a MATCH takes n + 1 steps from one
// start; said to be one word long, its limit on the empty string is
// 10,000,000 and 4 for that word at the one place, so 10,000,004 steps
// match and one more is the fault (`under`, `over`); on a string of nine
// bytes it is 36 more (`grown-under`, `grown-over`).
//
// And /^.+b/ over a string of a million characters, taking all of it and
// giving it back one by one: as a SPLIT, an ANY and a JMP (`long`), which
// grows the machine's stack a frame a character, and as a RUN (`run`),
// which is one frame (D241). Both say what the cap counts before and
// after, the same: the machine's memory is counted while a match runs and
// given back (D243). Under a cap of 4 MB the first is `out of memory`
// and the second is not (`cap-long`, `cap-run`). Each is run with
// CURLY_RE_PLAIN too, the machine with no memory of where it has been.
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "rt.h"

static const char *which;

static void body(rt_ctx *cx) {
    rt_frame frame;
    rt_value slots[2] = { { 0 }, { 0 } };
    rt_enter(cx, &frame, slots, 2);
    cx->line = 3;
    static const int32_t none[] = { 0 };
    const char *what = strncmp(which, "cap-", 4) == 0 ? which + 4 : which;
    if (strcmp(what, "long") == 0 || strcmp(what, "run") == 0) {
        // SAVE 0; BOL; ANY; SPLIT back or on; CHAR 'b'; SAVE 1; MATCH.
        static const int32_t loop[] = { 15, 0, 6, 3, 13, 3, 7, 1, 'b', 15, 1, 0 };
        // SAVE 0; BOL; ANY; RUN 0 of ANY; CHAR 'b'; SAVE 1; MATCH.
        static const int32_t run[] = { 15, 0, 6, 3, 19, 0, 3, 1, 'b', 15, 1, 0 };
        rt_regex re = { loop, none, 0, 0, 0, 12, 0, 0 };
        if (strcmp(what, "run") == 0) {
            re.code = run;
            re.marks = 1;
        }
        static const rt_str a = { 1, 1, "a" };
        static const rt_str b = { 1, 1, "b" };
        slots[0] = rt_repeat(cx, rt_string(&a), rt_int(999999));
        slots[1] = rt_concat(cx, slots[0], rt_string(&b));
        uint64_t held = cx->held;
        rt_say(cx, rt_match(cx, &re, slots[1]));
        rt_say(cx, rt_match(cx, &re, slots[0]));
        fflush(stdout);
        printf("held %s\n", cx->held == held ? "the same" : "more");
    } else {
        int grown = strncmp(what, "grown-", 6) == 0;
        int64_t jumps = (strstr(what, "over") != NULL ? 10000004 : 10000003) + (grown ? 36 : 0);
        int32_t *code = malloc(sizeof(int32_t) * (size_t)(2 * jumps + 1));
        for (int64_t k = 0; k < jumps; k++) {
            code[2 * k] = 14;
            code[2 * k + 1] = (int32_t)(2 * k + 2);
        }
        code[2 * jumps] = 0;
        rt_regex re = { code, none, 0, 0, 0, 1, 0, 0 };
        static const rt_str empty = { 0, 0, "" };
        static const rt_str nine = { 9, 9, "ninebytes" };
        rt_value v = rt_match(cx, &re, rt_string(grown ? &nine : &empty));
        free(code);
        rt_say(cx, v);
    }
    rt_leave(cx, &frame);
}

int main(int argc, char **argv) {
    which = argc > 1 ? argv[1] : "under";
    return rt_run(body, "regex.pl");
}
