// Classes and objects (step 17a; D172, D176, D182, D187), driven from C as
// the generated code drives them: the core made, a class and a subclass
// made as a program starts, their tables, dispatch and its faults; an
// instance made and its fields filled; what the collector keeps of an
// instance and of the class blocks, a chain of a million and a cycle; the
// constructor's look at its pairs; and every operator's fault for an
// object. The argument says which case.
#include <inttypes.h>
#include <stdio.h>
#include <string.h>
#include "rt.h"

static const char *which;
static const rt_str AB = { 2, 2, "ab", RT_STR_CONSTANT };
static const rt_str NAME_P = { 1, 1, "P", RT_STR_CONSTANT };
static const rt_str NAME_Q = { 1, 1, "Q", RT_STR_CONSTANT };
static const rt_str KEY_X = { 1, 1, "x", RT_STR_CONSTANT };
static const rt_str KEY_Y = { 1, 1, "y", RT_STR_CONSTANT };

static int is(const char *name) {
    return strcmp(which, name) == 0;
}

static void report(rt_ctx *cx, const char *when) {
    printf("%s: %" PRIu64 " on the heap\n", when, cx->objects);
}

// Methods as the compiler writes them: `self` is where the invocant is.
static rt_value p_m(rt_ctx *cx, int want, int64_t argc, rt_value **argv, rt_value *flat, rt_value *self) {
    (void)want; (void)argc; (void)argv; (void)flat;
    return rt_concat(cx, rt_string(&AB), RT_CELL(RT_FIELD(*self, 0)));
}

static rt_value q_m(rt_ctx *cx, int want, int64_t argc, rt_value **argv, rt_value *flat, rt_value *self) {
    (void)cx; (void)want; (void)argc; (void)argv; (void)flat; (void)self;
    return rt_int(2);
}

static rt_value p_n(rt_ctx *cx, int want, int64_t argc, rt_value **argv, rt_value *flat, rt_value *self) {
    (void)cx; (void)want; (void)argc; (void)argv; (void)flat; (void)self;
    return rt_int(3);
}

static rt_value maker(rt_ctx *cx, int want, int64_t argc, rt_value **argv, rt_value *flat, rt_value *self) {
    (void)cx; (void)want; (void)argc; (void)argv; (void)flat; (void)self;
    return rt_int(99);
}

static void apply(rt_ctx *cx, const char *op, rt_value o) {
    rt_value one = rt_int(1);
    if (strcmp(op, "add") == 0) rt_add(cx, o, one);
    if (strcmp(op, "neg") == 0) rt_neg(cx, o);
    if (strcmp(op, "lt") == 0) rt_num_lt(cx, o, one);
    if (strcmp(op, "eq-num-right") == 0) rt_num_eq(cx, one, o);
    if (strcmp(op, "concat") == 0) rt_concat(cx, rt_string(&AB), o);
    if (strcmp(op, "length") == 0) rt_length(cx, o);
    if (strcmp(op, "say") == 0) rt_say(cx, o);
    if (strcmp(op, "key") == 0) rt_helem(cx, rt_hash_new(cx), o);
    if (strcmp(op, "eq-str") == 0) rt_str_eq(cx, o, rt_string(&AB));
}

static void body(rt_ctx *cx) {
    rt_value slots[8];
    rt_frame frame;
    rt_enter(cx, &frame, slots, 8);
    cx->line = 1;
    rt_core(cx);
    // P has a field and methods 0 and 1; Q, below it, its own method 0.
    slots[0] = rt_class_new(cx, &NAME_P, rt_undef(), 1, maker, 3);
    rt_class_method(cx, slots[0], 0, p_m);
    rt_class_method(cx, slots[0], 1, p_n);
    slots[1] = rt_class_new(cx, &NAME_Q, slots[0], 2, maker, 3);
    rt_class_method(cx, slots[1], 0, q_m);
    if (is("dispatch")) {
        // An instance of each, its scalar field a cell: each method is the
        // class's own, or its parent's; isa follows the parents; ref,
        // blessed and reftype; truth and identity. Kept while a slot holds
        // it and freed when none does, the class blocks kept by their slots
        // and the core by the context.
        slots[2] = rt_object_new(cx, slots[0]);
        RT_FIELD(slots[2], 0) = rt_int(7);
        rt_cell_wrap(cx, &RT_FIELD(slots[2], 0));
        slots[3] = rt_object_new(cx, slots[1]);
        RT_FIELD(slots[3], 0) = rt_int(8);
        rt_cell_wrap(cx, &RT_FIELD(slots[3], 0));
        RT_FIELD(slots[3], 1) = rt_array_new(cx);
        rt_say(cx, rt_method(cx, slots[2], 0, "m")(cx, RT_SCALAR, 0, NULL, NULL, &slots[2]));
        rt_say(cx, rt_method(cx, slots[3], 0, "m")(cx, RT_SCALAR, 0, NULL, NULL, &slots[3]));
        rt_say(cx, rt_method(cx, slots[3], 1, "n")(cx, RT_SCALAR, 0, NULL, NULL, &slots[3]));
        rt_say(cx, rt_isa(cx, slots[3], slots[0]));
        rt_say(cx, rt_isa(cx, slots[2], slots[1]));
        rt_say(cx, rt_isa(cx, rt_string(&AB), slots[0]));
        rt_say(cx, rt_ref(cx, slots[3]));
        rt_say(cx, rt_blessed(cx, slots[2]));
        rt_say(cx, rt_reftype(cx, slots[2]));
        rt_say(cx, rt_bool(rt_is_true(cx, slots[2])));
        rt_say(cx, rt_num_eq(cx, slots[2], slots[2]));
        rt_say(cx, rt_num_ne(cx, slots[2], slots[3]));
        rt_say(cx, rt_class_name(cx, slots[3]));
        rt_say(cx, rt_class_maker(cx, slots[3])(cx, RT_SCALAR, 0, NULL, NULL, NULL));
        slots[4] = rt_sref(cx, RT_FIELD(slots[2], 0));
        rt_say(cx, rt_ref(cx, slots[4]));
        slots[5] = rt_sref(cx, RT_FIELD(slots[2], 0));
        rt_say(cx, rt_num_eq(cx, slots[4], slots[5]));
        slots[4] = slots[5] = rt_undef();
        rt_collect(cx);
        report(cx, "two instances held");
        slots[2] = slots[3] = rt_undef();
        rt_collect(cx);
        report(cx, "none held");
    }
    if (is("deep")) {
        // A million instances, each holding the one made before in its
        // field: the collector walks them with a stack of its own.
        slots[2] = rt_undef();
        for (int k = 0; k < 1000000; k++) {
            slots[3] = rt_object_new(cx, slots[0]);
            RT_FIELD(slots[3], 0) = slots[2];
            slots[2] = slots[3];
        }
        slots[3] = rt_undef();
        rt_collect(cx);
        report(cx, "a million kept");
        int64_t n = 0;
        for (slots[3] = slots[2]; slots[3].tag == RT_TAG_OBJ; slots[3] = RT_FIELD(slots[3], 0)) n += 1;
        printf("%" PRId64 " deep\n", n);
        slots[2] = slots[3] = rt_undef();
        rt_collect(cx);
        report(cx, "dropped");
    }
    if (is("cycle")) {
        // Two instances that hold each other, freed once nothing else does.
        slots[2] = rt_object_new(cx, slots[0]);
        slots[3] = rt_object_new(cx, slots[0]);
        RT_FIELD(slots[2], 0) = slots[3];
        RT_FIELD(slots[3], 0) = slots[2];
        slots[3] = rt_undef();
        rt_collect(cx);
        report(cx, "one held");
        slots[2] = rt_undef();
        rt_collect(cx);
        report(cx, "none held");
    }
    if (is("core")) {
        // The core alone: Class an instance of itself, Object and Role of
        // Class, both of them below Object; kept with no slot of a frame.
        rt_say(cx, rt_class_name(cx, cx->core[RT_CORE_CLASS]));
        rt_say(cx, rt_class_name(cx, cx->core[RT_CORE_OBJECT]));
        rt_say(cx, rt_isa(cx, cx->core[RT_CORE_CLASS], cx->core[RT_CORE_CLASS]));
        rt_say(cx, rt_isa(cx, cx->core[RT_CORE_ROLE], cx->core[RT_CORE_OBJECT]));
        rt_say(cx, rt_isa(cx, cx->core[RT_CORE_OBJECT], cx->core[RT_CORE_ROLE]));
        rt_say(cx, rt_ref(cx, slots[0]));
        slots[0] = slots[1] = rt_undef();
        rt_collect(cx);
        report(cx, "the core alone");
    }
    // The constructor's look at its pairs, before anything is made.
    if (strncmp(which, "new-", 4) == 0) {
        const rt_str *names[2] = { &KEY_X, &KEY_Y };
        const unsigned char required[2] = { 1, 0 };
        rt_value *places[2];
        slots[2] = rt_string(&KEY_X);
        slots[3] = rt_int(1);
        slots[4] = rt_string(&KEY_Y);
        slots[5] = rt_int(2);
        rt_value *ok[4] = { &slots[2], &slots[3], &slots[4], &slots[5] };
        if (is("new-ok")) {
            rt_new_args(cx, "P", 4, ok, NULL, 2, names, required, places);
            rt_say(cx, rt_add(cx, *places[0], *places[1]));
            rt_new_args(cx, "P", 2, ok, NULL, 2, names, required, places);
            rt_say(cx, rt_bool(places[1] == NULL));
        }
        rt_value *odd[3] = { &slots[2], &slots[3], &slots[4] };
        if (is("new-odd")) rt_new_args(cx, "P", 3, odd, NULL, 2, names, required, places);
        rt_value *twice[4] = { &slots[2], &slots[3], &slots[2], &slots[5] };
        if (is("new-twice")) rt_new_args(cx, "P", 4, twice, NULL, 2, names, required, places);
        rt_value *missing[2] = { &slots[4], &slots[5] };
        if (is("new-missing")) rt_new_args(cx, "P", 2, missing, NULL, 2, names, required, places);
        slots[6] = rt_string(&AB);
        rt_value *unknown[2] = { &slots[6], &slots[5] };
        if (is("new-unknown")) rt_new_args(cx, "P", 2, unknown, NULL, 2, names, required, places);
        slots[6] = rt_undef();
        if (is("new-undef")) rt_new_args(cx, "P", 2, unknown, NULL, 2, names, required, places);
    }
    // Dispatch's faults.
    if (is("call-undef")) rt_method(cx, rt_undef(), 0, "m");
    if (is("call-string")) rt_method(cx, rt_string(&AB), 0, "m");
    if (is("call-reference")) rt_method(cx, rt_aref(cx, rt_array_new(cx)), 0, "m");
    if (is("call-missing")) rt_method(cx, rt_object_new(cx, slots[1]), 2, "z");
    if (is("call-container")) rt_method(cx, rt_array_new(cx), 0, "m");
    if (is("deref")) rt_deref(cx, rt_object_new(cx, slots[0]), 0);
    if (strncmp(which, "op-", 3) == 0) {
        slots[2] = rt_object_new(cx, slots[0]);
        rt_say(cx, rt_int(2));
        apply(cx, which + 3, slots[2]);
        rt_say(cx, rt_int(3));
    }
    rt_leave(cx, &frame);
}

int main(int argc, char **argv) {
    which = argc > 1 ? argv[1] : "";
    return rt_run(body, "obj.pl");
}
