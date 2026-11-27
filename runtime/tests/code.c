// Subs' references and closures (step 14; D161, D162, D164), driven from
// C as ref.c drives references: a reference made with what it captures and
// called through, as the generated code calls it; what the collector keeps
// of a closure and what it frees, a chain of a million and a cycle; the
// check of a call through a reference; the freeze for good; and every
// operator's fault for a sub's reference. The argument says which case.
#include <inttypes.h>
#include <stdio.h>
#include <string.h>
#include "rt.h"

static const char *which;
static const rt_str AB = { 2, 2, "ab", RT_STR_CONSTANT };

static int is(const char *name) {
    return strcmp(which, name) == 0;
}

static void report(rt_ctx *cx, const char *when) {
    printf("%s: %" PRIu64 " on the heap\n", when, cx->objects);
}

// A sub with no name as the compiler would write it: its captures where
// its reference holds them, a cell and an array, and the arguments it was
// handed.
static rt_value add_captured(rt_ctx *cx, int want, int64_t argc, rt_value **argv, rt_value *flat, rt_value *self) {
    (void)want;
    (void)flat;
    rt_value *cap = RT_CAPTURES(self);
    rt_value sum = rt_add(cx, RT_CELL(cap[0]), rt_count(cx, cap[1]));
    for (int64_t k = 0; k < argc; k++) sum = rt_add(cx, sum, *argv[k]);
    RT_CELL(cap[0]) = sum;
    return sum;
}

// One that holds only a cell, which may hold another sub's reference.
static rt_value next_link(rt_ctx *cx, int want, int64_t argc, rt_value **argv, rt_value *flat, rt_value *self) {
    (void)cx;
    (void)want;
    (void)argc;
    (void)argv;
    (void)flat;
    return RT_CELL(RT_CAPTURES(self)[0]);
}

static rt_value nothing(rt_ctx *cx, int want, int64_t argc, rt_value **argv, rt_value *flat, rt_value *self) {
    (void)cx;
    (void)want;
    (void)argc;
    (void)argv;
    (void)flat;
    (void)self;
    return rt_undef();
}

static void apply(rt_ctx *cx, const char *op, rt_value r) {
    rt_value one = rt_int(1);
    rt_value s = rt_string(&AB);
    if (strcmp(op, "add") == 0) rt_add(cx, r, one);
    if (strcmp(op, "neg") == 0) rt_neg(cx, r);
    if (strcmp(op, "inc") == 0) rt_inc(cx, r);
    if (strcmp(op, "lt") == 0) rt_num_lt(cx, r, one);
    if (strcmp(op, "eq-num-right") == 0) rt_num_eq(cx, one, r);
    if (strcmp(op, "concat") == 0) rt_concat(cx, r, s);
    if (strcmp(op, "length") == 0) rt_length(cx, r);
    if (strcmp(op, "say") == 0) rt_say(cx, r);
    if (strcmp(op, "key") == 0) rt_helem(cx, rt_hash_new(cx), r);
    if (strcmp(op, "join") == 0) {
        rt_value l = rt_array_new(cx);
        rt_list_add(cx, l, r);
        rt_join(cx, s, l);
    }
    if (strcmp(op, "sort") == 0) {
        rt_value l = rt_array_new(cx);
        rt_list_add(cx, l, s);
        rt_list_add(cx, l, r);
        rt_value into = rt_array_new(cx);
        rt_sort_strings(cx, l, into);
    }
}

static void body(rt_ctx *cx) {
    rt_value slots[6];
    rt_frame frame;
    rt_enter(cx, &frame, slots, 6);
    cx->line = 1;
    if (is("code")) {
        // A sub that captures a cell and an array, called twice through its
        // reference with the reference in a slot: it reads and stores the
        // variable itself. Kept while a slot holds the reference, and what
        // it captured with it; freed, all of it, when none does.
        slots[0] = rt_int(10);
        rt_cell_wrap(cx, &slots[0]);
        slots[1] = rt_array_new(cx);
        rt_list_add(cx, slots[1], rt_concat(cx, rt_string(&AB), rt_int(1)));
        slots[2] = rt_code_new(cx, add_captured, 2);
        rt_code_capture(cx, slots[2], 0, slots[0]);
        rt_code_capture(cx, slots[2], 1, slots[1]);
        slots[3] = rt_int(5);
        rt_value *argv[1] = { &slots[3] };
        slots[4] = rt_code(cx, slots[2]);
        rt_say(cx, RT_CODE_FN(slots[4])(cx, RT_SCALAR, 1, argv, NULL, &slots[4]));
        rt_say(cx, RT_CODE_FN(slots[4])(cx, RT_SCALAR, 1, argv, NULL, &slots[4]));
        rt_say(cx, RT_CELL(slots[0]));
        rt_say(cx, rt_ref(cx, slots[2]));
        rt_say(cx, rt_bool(rt_is_true(cx, slots[2])));
        rt_say(cx, rt_defined(cx, slots[2]));
        rt_say(cx, rt_num_eq(cx, slots[2], slots[4]));
        rt_say(cx, rt_num_ne(cx, slots[2], rt_code_new(cx, nothing, 0)));
        slots[0] = slots[1] = slots[3] = slots[4] = rt_undef();
        rt_collect(cx);
        report(cx, "the reference held");
        slots[2] = rt_undef();
        rt_collect(cx);
        report(cx, "none held");
    }
    if (is("code-deep")) {
        // A million subs, each holding a cell that holds the one made
        // before: the collector walks them with a stack of its own.
        slots[0] = rt_undef();
        for (int k = 0; k < 1000000; k++) {
            rt_cell_wrap(cx, &slots[0]);
            slots[1] = rt_code_new(cx, next_link, 1);
            rt_code_capture(cx, slots[1], 0, slots[0]);
            slots[0] = slots[1];
        }
        slots[1] = rt_undef();
        rt_collect(cx);
        report(cx, "a million kept");
        int64_t n = 0;
        slots[2] = slots[0];
        while (slots[2].tag == RT_TAG_CODE) {
            slots[3] = rt_code(cx, slots[2]);
            slots[2] = RT_CODE_FN(slots[3])(cx, RT_SCALAR, 0, NULL, NULL, &slots[3]);
            n += 1;
        }
        printf("%" PRId64 " deep\n", n);
        slots[0] = slots[3] = rt_undef();
        rt_collect(cx);
        report(cx, "dropped");
    }
    if (is("code-cycle")) {
        // A sub that captures the cell that holds it: kept while a slot
        // holds either, freed when none does.
        slots[0] = rt_undef();
        rt_cell_wrap(cx, &slots[0]);
        slots[1] = rt_code_new(cx, next_link, 1);
        rt_code_capture(cx, slots[1], 0, slots[0]);
        RT_CELL(slots[0]) = slots[1];
        slots[1] = rt_undef();
        rt_collect(cx);
        report(cx, "the cell held");
        slots[0] = rt_undef();
        rt_collect(cx);
        report(cx, "none held");
    }
    if (is("call-undef")) rt_code(cx, rt_undef());
    if (is("call-number")) rt_code(cx, rt_int(5));
    if (is("call-string")) rt_code(cx, rt_string(&AB));
    if (is("call-array-reference")) rt_code(cx, rt_aref(cx, rt_array_new(cx)));
    if (is("call-container")) rt_code(cx, rt_array_new(cx));
    if (is("deref-code")) rt_deref(cx, rt_code_new(cx, nothing, 0), 0);
    if (is("capture-not-a-variable")) {
        slots[0] = rt_code_new(cx, nothing, 1);
        rt_code_capture(cx, slots[0], 0, rt_int(1));
    }
    if (is("capture-past-the-end")) {
        slots[0] = rt_code_new(cx, nothing, 1);
        rt_code_capture(cx, slots[0], 1, rt_array_new(cx));
    }
    if (is("forever") || is("forever-hash")) {
        // Frozen by a loop and for good: the loop's freeze given back, the
        // one for good stays, and a second for good is the same one.
        slots[0] = is("forever") ? rt_array_new(cx) : rt_hash_new(cx);
        rt_freeze(cx, slots[0]);
        rt_freeze_forever(cx, slots[0]);
        rt_freeze_forever(cx, slots[0]);
        rt_thaw(cx, slots[0]);
        printf("thawed\n");
        if (is("forever")) rt_elem_store(cx, slots[0], rt_int(0), rt_int(1));
        else rt_helem_store(cx, slots[0], rt_string(&AB), rt_int(1));
    }
    if (is("forever-all")) {
        slots[0] = rt_array_new(cx);
        slots[1] = rt_hash_new(cx);
        slots[2] = rt_array_new(cx);
        rt_frozen_add(cx, slots[2], slots[0]);
        rt_frozen_add(cx, slots[2], slots[1]);
        rt_freeze_all_forever(cx, slots[2]);
        printf("frozen\n");
        rt_push(cx, slots[0], slots[2]);
    }
    if (strncmp(which, "op-", 3) == 0) {
        slots[0] = rt_code_new(cx, nothing, 0);
        printf("2\n");
        apply(cx, which + 3, slots[0]);
        printf("not faulted\n");
    }
    rt_leave(cx, &frame);
}

int main(int argc, char **argv) {
    which = argc > 1 ? argv[1] : "";
    return rt_run(body, "code.pl");
}
