// References (step 13a; D107, D112, D114). rt.c includes this file: it is
// a part of the runtime, apart for its subject.
//
// A reference is a value whose payload is a container's block: the very
// block an array's or a hash's variable holds, so `\@a` is that block
// with another tag, and `[ LIST ]` is the list the generated code built,
// which is a new array no one else holds. The collector walks from a
// container to what it holds (rt.c, `rt_collect`), and a container is
// frozen, changed and collected whatever reaches it.
//
// What an arrow reads through is made a container value again, ARRAY or
// HASH, which the element functions of rt.c and hash.c take as they take
// a variable's: so `$r->[0]` is `rt_elem` of `rt_deref` of `$r`.

#define UNDEF_REFERENCE "undef where a reference is wanted"
#define NOT_ARRAY "not a reference to an array"
#define NOT_HASH "not a reference to a hash"
#define NOT_SCALAR "not a reference to a scalar"
#define NOT_SUB "not a reference to a sub"

// `hash` is 0 for an array, 1 for a hash, and 2 for a scalar's cell (step
// 13c), throughout.
static rt_value container(rt_array *a, int hash) {
    rt_value v;
    v.tag = hash == 2 ? RT_TAG_CELL : hash ? RT_TAG_HASH : RT_TAG_ARRAY;
    v.as.a = a;
    return v;
}

static uint64_t reference_tag(int hash) {
    return hash == 2 ? RT_TAG_SREF : hash ? RT_TAG_HREF : RT_TAG_AREF;
}

// A new cell holding what the slot holds, which the slot holds after
// (step 13c). The allocation is made while the value is still in the slot.
void rt_cell_wrap(rt_ctx *cx, rt_value *slot) {
    if (!a_scalar(slot->tag)) rt_internal(cx, "a cell made of what is no value");
    rt_value c = rt_array_new(cx);
    append(cx, c.as.a, *slot);
    c.tag = RT_TAG_CELL;
    *slot = c;
}

rt_value rt_sref(rt_ctx *cx, rt_value cell) {
    if (cell.tag != RT_TAG_CELL || cell.as.a->dead) rt_internal(cx, "a reference to a scalar that has no cell");
    rt_value v;
    v.tag = RT_TAG_SREF;
    v.as.a = cell.as.a;
    return v;
}

rt_value rt_aref(rt_ctx *cx, rt_value array) {
    rt_value v;
    v.tag = RT_TAG_AREF;
    v.as.a = array_of(cx, array);
    return v;
}

rt_value rt_href(rt_ctx *cx, rt_value hash) {
    rt_value v;
    v.tag = RT_TAG_HREF;
    v.as.a = hash_of(cx, hash);
    return v;
}

// Reading through undef, or through anything that is not the reference
// wanted, is a fault (D107): perl makes the container on a read too, the
// variable included (T231), and dies of a string or the other kind of
// reference (T234).
rt_value rt_deref(rt_ctx *cx, rt_value v, int hash) {
    if (v.tag == RT_TAG_UNDEF) rt_fault(cx, UNDEF_REFERENCE);
    if (v.tag != reference_tag(hash)) {
        if (!a_scalar(v.tag)) rt_fault(cx, "not a value");
        rt_fault(cx, hash == 2 ? NOT_SCALAR : hash ? NOT_HASH : NOT_ARRAY);
    }
    if (v.as.a->dead) rt_internal(cx, "a reference to a container that was collected");
    return container(v.as.a, hash);
}

// A new container, empty: the one allocation of the two functions below,
// and the last thing either does before it stores what it made. A cell
// holds one undef from the start (step 13c), which is storage, and no
// collection.
static rt_value made_container(rt_ctx *cx, int hash) {
    if (hash != 2) return hash ? rt_hash_new(cx) : rt_array_new(cx);
    rt_value c = rt_array_new(cx);
    append(cx, c.as.a, rt_undef());
    c.tag = RT_TAG_CELL;
    return c;
}

static rt_value reference_to(rt_value c) {
    rt_value v;
    v.tag = c.tag == RT_TAG_CELL ? RT_TAG_SREF : c.tag == RT_TAG_HASH ? RT_TAG_HREF : RT_TAG_AREF;
    v.as.a = c.as.a;
    return v;
}

// A variable stored through (T248): undef is made a new container, as
// perl makes it, and the variable a reference to it. The variable is in a
// slot, and holds undef while the container is made.
rt_value rt_vivify(rt_ctx *cx, rt_value *slot, int hash) {
    if (slot->tag != RT_TAG_UNDEF) return rt_deref(cx, *slot, hash);
    rt_value c = made_container(cx, hash);
    *slot = reference_to(c);
    return c;
}

// One hop of a store: the element of `array` at `index`, made if it is not
// there or undef, and what it points at. Making it is a store to the array,
// so it faults while a foreach is over it (D114); an element that already
// holds the reference wanted is only read, as perl only reads it.
rt_value rt_elem_hop(rt_ctx *cx, rt_value array, rt_value index, int hash) {
    rt_value v = rt_elem(cx, array, index);
    if (v.tag != RT_TAG_UNDEF) return rt_deref(cx, v, hash);
    // (The element is made first, undef, so that what the allocation
    // below may collect is held by nothing that matters.)
    int64_t at = rt_elem_make(cx, array, index);
    rt_value c = made_container(cx, hash);
    rt_elem_put(cx, array, at, reference_to(c));
    return c;
}

// The same for a hash's element. The key, if it is no string, is made one
// as it is stored: an allocation, after which it is in the hash, and only
// then the container is made.
rt_value rt_helem_hop(rt_ctx *cx, rt_value h, rt_value key, int hash) {
    rt_value v = rt_helem(cx, h, key);
    if (v.tag != RT_TAG_UNDEF) return rt_deref(cx, v, hash);
    int64_t pair = rt_helem_make(cx, h, key);
    rt_value c = made_container(cx, hash);
    rt_helem_put(cx, h, pair, reference_to(c));
    return c;
}

static const rt_str STR_ARRAY = { 5, 5, "ARRAY", RT_STR_CONSTANT };
static const rt_str STR_HASH = { 4, 4, "HASH", RT_STR_CONSTANT };
static const rt_str STR_SCALAR = { 6, 6, "SCALAR", RT_STR_CONSTANT };
static const rt_str STR_REF = { 3, 3, "REF", RT_STR_CONSTANT };
static const rt_str STR_CODE = { 4, 4, "CODE", RT_STR_CONSTANT };

// A reference to a scalar is SCALAR, or REF when the scalar holds a
// reference now (T242).
rt_value rt_ref(rt_ctx *cx, rt_value v) {
    if (v.tag == RT_TAG_AREF) return rt_string(&STR_ARRAY);
    if (v.tag == RT_TAG_HREF) return rt_string(&STR_HASH);
    if (v.tag == RT_TAG_SREF) return rt_string(is_ref(RT_CELL(v)) ? &STR_REF : &STR_SCALAR);
    if (v.tag == RT_TAG_CODE) return rt_string(&STR_CODE);
    // An object's class's name (D176, step 17a).
    if (v.tag == RT_TAG_OBJ) return rt_class_name(cx, v);
    if (!a_scalar(v.tag)) rt_fault(cx, "not a value");
    return rt_string(&STR_FALSE);
}

// The containers to freeze are kept as container values, raw, in a list no
// program sees: it is in a slot, so they are alive while the loop runs.
void rt_frozen_add(rt_ctx *cx, rt_value frozen, rt_value c) {
    if (c.tag != RT_TAG_ARRAY && c.tag != RT_TAG_HASH) rt_internal(cx, "a frozen container is no container");
    append(cx, array_of(cx, frozen), c);
}

void rt_freeze_all(rt_ctx *cx, rt_value frozen) {
    rt_array *a = array_of(cx, frozen);
    for (uint64_t n = 0; n < a->count; n++) rt_freeze(cx, a->items[n]);
}

void rt_thaw_all(rt_ctx *cx, rt_value frozen) {
    rt_array *a = array_of(cx, frozen);
    for (uint64_t n = 0; n < a->count; n++) rt_thaw(cx, a->items[n]);
}

// ---- subs with no name, and calls through a reference (step 14)

// A sub's reference: a new block, its first item the function and then a
// row of undefs for what it captures, which the generated code stores at
// once, before anything allocates again. The one allocation is the
// block; the row is storage, and starts no collection.
rt_value rt_code_new(rt_ctx *cx, rt_code_fn fn, int64_t count) {
    rt_value c = rt_array_new(cx);
    rt_value f;
    f.tag = RT_TAG_FN;
    f.as.bits = (uint64_t)(uintptr_t)fn;
    append(cx, c.as.a, f);
    for (int64_t k = 0; k < count; k++) append(cx, c.as.a, rt_undef());
    c.tag = RT_TAG_CODE;
    return c;
}

// What a sub captures is the variable itself: a scalar's cell, or an
// array's or a hash's block (D161).
void rt_code_capture(rt_ctx *cx, rt_value code, int64_t at, rt_value v) {
    if (code.tag != RT_TAG_CODE || code.as.a->dead || at < 0 || (uint64_t)at + 1 >= code.as.a->count) rt_internal(cx, "a capture stored where a sub has none");
    if (v.tag != RT_TAG_CELL && v.tag != RT_TAG_ARRAY && v.tag != RT_TAG_HASH) rt_internal(cx, "a sub captured what is no variable");
    code.as.a->items[at + 1] = v;
}

// A call through a reference (D164): undef, and anything that is not a
// sub's reference, is a fault, as perl dies of each (T366).
rt_value rt_code(rt_ctx *cx, rt_value v) {
    if (v.tag == RT_TAG_UNDEF) rt_fault(cx, UNDEF_REFERENCE);
    if (v.tag != RT_TAG_CODE) {
        if (!a_scalar(v.tag)) rt_fault(cx, "not a value");
        rt_fault(cx, NOT_SUB);
    }
    if (v.as.a->dead || v.as.a->count == 0 || v.as.a->items[0].tag != RT_TAG_FN) rt_internal(cx, "a sub's reference that holds no sub");
    return v;
}

// Frozen for good (D162): the top bit of the count, which `rt_thaw` and a
// `die` never take, and which is set once however many closures ask.
#define FROZEN_FOREVER ((uint64_t)1 << 62)

void rt_freeze_forever(rt_ctx *cx, rt_value container) {
    rt_array *a = container_of(cx, container);
    a->frozen |= FROZEN_FOREVER;
}

void rt_freeze_all_forever(rt_ctx *cx, rt_value frozen) {
    rt_array *a = array_of(cx, frozen);
    for (uint64_t n = 0; n < a->count; n++) rt_freeze_forever(cx, a->items[n]);
}
