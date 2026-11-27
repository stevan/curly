// Classes and objects (step 17a; D170 to D178, D182, D187). rt.c includes
// this file: it is a part of the runtime, apart for its subject.
//
// An object is a value, OBJ, whose payload is an instance: a block of the
// collector's as an array is, its first item its class and then one item a
// field, every field of the class's parents first. A scalar field holds a
// cell from construction (T432), an array's or a hash's its container, so
// the collector walks an instance as it walks an array, and a loop freezes
// a field as it freezes any array.
//
// A class is an object too, an instance of `Class` (D182): its items are
// its class, its name, its parent, how many fields an instance has, its
// constructor (an FN, which the collector skips and no program sees), the
// roles it does, and then its method table, one item a method's number,
// an FN or undef. `Object`, `Role` and `Class` are made here, by hand, as
// a program starts, and held in the context; no program can name them
// (D177), and they give a program's classes nothing to dispatch to
// (finding 16 of step 17's review). Every class a program declares is made
// by the generated code as the program starts, a parent before its
// children, with its parent's table copied and its own methods put over
// it. The runtime calls no generated code (D83): it finds the function,
// and the generated code calls it.

#define CLASS_OF 0
#define CLASS_NAME 1
#define CLASS_PARENT 2
#define CLASS_FIELDS 3
#define CLASS_MAKER 4
#define CLASS_DOES 5
#define CLASS_TABLE 6

#define UNDEF_OBJECT "undef where an object is wanted"
#define NOT_OBJECT "not an object"

static rt_value fn_value(rt_code_fn fn) {
    rt_value f;
    f.tag = RT_TAG_FN;
    f.as.bits = (uint64_t)(uintptr_t)fn;
    return f;
}

static rt_array *instance_of(rt_ctx *cx, rt_value v) {
    if (v.tag != RT_TAG_OBJ || v.as.a->dead || v.as.a->count == 0) rt_internal(cx, "an object that is no instance");
    return v.as.a;
}

// A class's block, every item undef but its class and name, which the
// caller fills before it allocates again. The one allocation is the block;
// the items are storage, and start no collection.
static rt_value class_block(rt_ctx *cx, rt_value of, const rt_str *name, int64_t methods) {
    rt_value c = rt_array_new(cx);
    append(cx, c.as.a, of);
    append(cx, c.as.a, rt_string(name));
    for (int64_t k = CLASS_PARENT; k < CLASS_TABLE + methods; k++) append(cx, c.as.a, rt_undef());
    c.as.a->items[CLASS_FIELDS] = rt_int(0);
    c.tag = RT_TAG_OBJ;
    return c;
}

static const rt_str STR_OBJECT_CLASS = { 6, 6, "Object", RT_STR_CONSTANT };
static const rt_str STR_ROLE_CLASS = { 4, 4, "Role", RT_STR_CONSTANT };
static const rt_str STR_CLASS_CLASS = { 5, 5, "Class", RT_STR_CONSTANT };

// The core (D182), bootstrapped: `Class` is an instance of itself, and
// `Object` and `Role` instances of it; `Role` and `Class` are subclasses of
// `Object`, and `Class` does `Role`. Each is in the context's own slots
// before the next is made.
void rt_core(rt_ctx *cx) {
    cx->core[RT_CORE_CLASS] = class_block(cx, rt_undef(), &STR_CLASS_CLASS, 0);
    cx->core[RT_CORE_CLASS].as.a->items[CLASS_OF] = cx->core[RT_CORE_CLASS];
    cx->core[RT_CORE_OBJECT] = class_block(cx, cx->core[RT_CORE_CLASS], &STR_OBJECT_CLASS, 0);
    cx->core[RT_CORE_ROLE] = class_block(cx, cx->core[RT_CORE_CLASS], &STR_ROLE_CLASS, 0);
    cx->core[RT_CORE_ROLE].as.a->items[CLASS_PARENT] = cx->core[RT_CORE_OBJECT];
    cx->core[RT_CORE_CLASS].as.a->items[CLASS_PARENT] = cx->core[RT_CORE_OBJECT];
    rt_value does = rt_array_new(cx);
    // (The list is in a slot of the context's before it is filled.)
    cx->core[RT_CORE_CLASS].as.a->items[CLASS_DOES] = does;
    append(cx, does.as.a, cx->core[RT_CORE_ROLE]);
}

rt_value rt_class_new(rt_ctx *cx, const rt_str *name, rt_value parent, int64_t fields, rt_code_fn make, int64_t methods) {
    if (parent.tag != RT_TAG_UNDEF) instance_of(cx, parent);
    rt_value c = class_block(cx, cx->core[RT_CORE_CLASS], name, methods);
    rt_array *a = c.as.a;
    a->items[CLASS_PARENT] = parent.tag == RT_TAG_UNDEF ? cx->core[RT_CORE_OBJECT] : parent;
    a->items[CLASS_FIELDS] = rt_int(fields);
    a->items[CLASS_MAKER] = fn_value(make);
    if (parent.tag != RT_TAG_UNDEF) {
        rt_array *p = parent.as.a;
        for (int64_t k = 0; k < methods && CLASS_TABLE + (uint64_t)k < p->count; k++) a->items[CLASS_TABLE + k] = p->items[CLASS_TABLE + k];
    }
    return c;
}

void rt_class_method(rt_ctx *cx, rt_value cls, int64_t id, rt_code_fn fn) {
    rt_array *a = instance_of(cx, cls);
    if (id < 0 || CLASS_TABLE + (uint64_t)id >= a->count) rt_internal(cx, "a method numbered past its class's table");
    a->items[CLASS_TABLE + id] = fn_value(fn);
}

// A new instance of `cls`, every field undef until the class's fields are
// made, in order (T400). One allocation, the block; the items are storage.
rt_value rt_object_new(rt_ctx *cx, rt_value cls) {
    rt_array *c = instance_of(cx, cls);
    int64_t fields = c->items[CLASS_FIELDS].as.i;
    rt_value o = rt_array_new(cx);
    append(cx, o.as.a, cls);
    for (int64_t k = 0; k < fields; k++) append(cx, o.as.a, rt_undef());
    o.tag = RT_TAG_OBJ;
    return o;
}

static rt_array *class_of(rt_ctx *cx, rt_value obj) {
    return instance_of(cx, instance_of(cx, obj)->items[CLASS_OF]);
}

// A method call (D172): the function the object's class has for method
// number `id`. undef, anything that is not an object, and an object whose
// class has no such method are faults, where perl dies (17-undef,
// 17-unblessed, 17-missing).
rt_code_fn rt_method(rt_ctx *cx, rt_value v, int64_t id, const char *name) {
    if (v.tag == RT_TAG_UNDEF) rt_fault(cx, UNDEF_OBJECT);
    if (v.tag != RT_TAG_OBJ) {
        if (!a_scalar(v.tag)) rt_fault(cx, "not a value");
        rt_fault(cx, NOT_OBJECT);
    }
    rt_array *c = class_of(cx, v);
    rt_value f = id >= 0 && CLASS_TABLE + (uint64_t)id < c->count ? c->items[CLASS_TABLE + id] : rt_undef();
    if (f.tag != RT_TAG_FN) {
        char what[600];
        const rt_str *cls = c->items[CLASS_NAME].as.s;
        snprintf(what, sizeof what, "an object of %.*s has no method %.300s", (int)(cls->len > 250 ? 250 : cls->len), cls->bytes, name);
        rt_fault(cx, what);
    }
    return (rt_code_fn)(uintptr_t)f.as.bits;
}

// `__CLASS__->new` (D173): the constructor of the object's own class.
rt_code_fn rt_class_maker(rt_ctx *cx, rt_value obj) {
    rt_value f = class_of(cx, obj)->items[CLASS_MAKER];
    if (f.tag != RT_TAG_FN) rt_internal(cx, "a class with no constructor");
    return (rt_code_fn)(uintptr_t)f.as.bits;
}

// `__CLASS__`, and what `ref` and `blessed` give of an object: its class's
// name, a constant of the generated code's.
rt_value rt_class_name(rt_ctx *cx, rt_value obj) {
    return class_of(cx, obj)->items[CLASS_NAME];
}

// `EXPR isa NAME`: an object of the class or of one below it; anything
// else is false, as perl has it (17-isa).
rt_value rt_isa(rt_ctx *cx, rt_value v, rt_value cls) {
    if (!a_scalar(v.tag)) rt_fault(cx, "not a value");
    if (v.tag != RT_TAG_OBJ) return rt_bool(0);
    rt_array *want = instance_of(cx, cls);
    for (rt_value c = instance_of(cx, v)->items[CLASS_OF]; c.tag == RT_TAG_OBJ; c = instance_of(cx, c)->items[CLASS_PARENT]) {
        if (c.as.a == want) return rt_bool(1);
    }
    return rt_bool(0);
}

static const rt_str STR_OBJECT = { 6, 6, "OBJECT", RT_STR_CONSTANT };

// `blessed`: an object's class's name, and undef for anything else.
rt_value rt_blessed(rt_ctx *cx, rt_value v) {
    if (!a_scalar(v.tag)) rt_fault(cx, "not a value");
    return v.tag == RT_TAG_OBJ ? rt_class_name(cx, v) : rt_undef();
}

// `reftype`: what a reference is, OBJECT for an object, and undef for
// what is no reference. A reference to a scalar that holds a reference is
// REF, as `ref` has it (R17-11-ref-ref-object).
rt_value rt_reftype(rt_ctx *cx, rt_value v) {
    if (!a_scalar(v.tag)) rt_fault(cx, "not a value");
    if (v.tag == RT_TAG_OBJ) return rt_string(&STR_OBJECT);
    if (rt_ref_tag(v.tag)) return rt_ref(cx, v);
    return rt_undef();
}

// The pairs a constructor was given (D178, D187), looked at before any of
// the construction runs: an odd count, then each name in turn (no
// parameter of the class or a parent, or one given twice), then the first
// required parameter not given. `places[k]` is then where parameter k's
// value is, or NULL. A name is made a string as `.` makes one, on the C
// stack, and compared by its bytes.
void rt_new_args(rt_ctx *cx, const char *cls, int64_t argc, rt_value **argv, rt_value *flat, int64_t count,
                 const rt_str *const *names, const unsigned char *required, rt_value **places) {
    char what[700];
    for (int64_t k = 0; k < count; k++) places[k] = NULL;
    if (argc % 2 != 0) {
        snprintf(what, sizeof what, "an odd number of arguments for %.300s->new: they are names and values by turns", cls);
        rt_fault(cx, what);
    }
    for (int64_t n = 0; n < argc; n += 2) {
        rt_value *key = flat != NULL ? &flat[n] : argv[n];
        scratch number;
        const rt_str *s = to_str(cx, *key, &number);
        int64_t found = -1;
        for (int64_t k = 0; k < count; k++) {
            if (names[k]->len == s->len && memcmp(names[k]->bytes, s->bytes, s->len) == 0) found = k;
        }
        int len = (int)(s->len > 200 ? 200 : s->len);
        if (found < 0) {
            snprintf(what, sizeof what, "%.300s->new was given %.*s, which is no parameter of %.300s", cls, len, s->bytes, cls);
            rt_fault(cx, what);
        }
        if (places[found] != NULL) {
            snprintf(what, sizeof what, "%.300s->new was given %.*s twice", cls, len, s->bytes);
            rt_fault(cx, what);
        }
        places[found] = flat != NULL ? &flat[n + 1] : argv[n + 1];
    }
    for (int64_t k = 0; k < count; k++) {
        if (required[k] && places[k] == NULL) {
            snprintf(what, sizeof what, "%.300s->new was not given %.*s, which it needs", cls, (int)names[k]->len, names[k]->bytes);
            rt_fault(cx, what);
        }
    }
}
