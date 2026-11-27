// The matcher's limit on steps (D232), at its edge: no program can reach
// it exactly, since how many steps a pattern takes is the machine's own
// count. A program of n JMPs and a MATCH takes n + 1 steps from one start,
// on the empty string; 10,000,000 steps match and one more is the fault.
// And a match over a string of a million characters, `.*` taking all of it
// and giving them back one by one, which grows the machine's stack.
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
    if (strcmp(which, "long") == 0) {
        // SAVE 0; BOL; ANY; SPLIT back or on; CHAR 'b'; SAVE 1; MATCH: /^.+b/.
        static const int32_t code[] = { 15, 0, 6, 3, 13, 3, 7, 1, 'b', 15, 1, 0 };
        rt_regex re = { code, none, 0, 0, 0 };
        static const rt_str a = { 1, 1, "a" };
        static const rt_str b = { 1, 1, "b" };
        slots[0] = rt_repeat(cx, rt_string(&a), rt_int(999999));
        slots[1] = rt_concat(cx, slots[0], rt_string(&b));
        rt_say(cx, rt_match(cx, &re, slots[1]));
        rt_say(cx, rt_match(cx, &re, slots[0]));
    } else {
        int64_t jumps = strcmp(which, "over") == 0 ? 10000000 : 9999999;
        int32_t *code = malloc(sizeof(int32_t) * (size_t)(2 * jumps + 1));
        for (int64_t k = 0; k < jumps; k++) {
            code[2 * k] = 14;
            code[2 * k + 1] = (int32_t)(2 * k + 2);
        }
        code[2 * jumps] = 0;
        rt_regex re = { code, none, 0, 0, 0 };
        static const rt_str empty = { 0, 0, "" };
        rt_value v = rt_match(cx, &re, rt_string(&empty));
        free(code);
        rt_say(cx, v);
    }
    rt_leave(cx, &frame);
}

int main(int argc, char **argv) {
    which = argc > 1 ? argv[1] : "under";
    return rt_run(body, "regex.pl");
}
