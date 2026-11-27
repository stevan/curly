// Step 22: numbers and time (D200 to D207). rt.c includes this file, after
// format.c, so that it reads values with the readers every operator uses:
// `numeric` (D40), `to_str` (D24) and `whole_of`, a whole number by the
// rule `substr` has for a position (D41, T103).
#include <time.h>
#include <unistd.h>

// ---- int and abs (D201)

// perl's int: an integer when its cut fits one, and perl's test for that
// is `value > IV_MIN - 0.5` below zero, which as a double is -2^63 again,
// so -2^63 itself stays a float (T470). From 2^63 up to 2^64 perl's
// integer is unsigned, which the language does not have.
rt_value rt_num_int(rt_ctx *cx, rt_value a) {
    number x = numeric(cx, a);
    if (x.is_int) return rt_int(x.i);
    double d = x.n;
    if (d >= TWO_63 && d < 2 * TWO_63) rt_fault(cx, "int of a number from 2^63 to 2^64: perl gives an unsigned integer, which the language does not have");
    if (d > -TWO_63 && d < TWO_63) return rt_int((int64_t)trunc(d));
    return rt_num(d);
}

// perl's abs takes a Num for an integer only when it is integral, a whole
// number below 2^53 (T471), and never a string with a point (T487); -2^63 has no positive Int, and perl's answer
// is the unsigned 2^63.
rt_value rt_num_abs(rt_ctx *cx, rt_value a) {
    number x = numeric(cx, a);
    if (x.is_int) {
        if (x.i == INT64_MIN) rt_fault(cx, "abs of -2^63: perl gives the unsigned integer 2^63, which the language does not have");
        return rt_int(x.i < 0 ? -x.i : x.i);
    }
    // A string with a point and no exponent perl takes as a float here,
    // whole or not, whatever was done with it before (T487).
    int64_t w;
    if (!x.soft && integral(x, &w)) return rt_int(w < 0 ? -w : w);
    return rt_num(fabs(x.n));
}

// ---- the float functions (D202)

// An argument as a double. A string whose number is zero and which has a
// minus sign is a negative zero to perl until it has been used as an
// integer, and then a zero (T484): two answers wherever the sign can show.
static double float_arg(rt_ctx *cx, rt_value v, const char *name) {
    double d = as_double(numeric(cx, v));
    if (v.tag == RT_TAG_STR && negative_zero(cx, v, d)) {
        char what[160];
        snprintf(what, sizeof what, "a string that is a zero with a minus, to %s: perl reads it as -0 or 0 by what the string was used as", name);
        rt_fault(cx, what);
    }
    return d;
}

// What the C library gave, which is perl's too. perl exits with errno
// after an uncaught `die`, and the function may have set it (T472): noted
// for `rt_throw`, as a string's read and `**` note it (D151). The library
// says by errno, but a subnormal or a vanished answer is noted whatever it
// says, so that the language faults where perl's exit status may differ.
static rt_value libm(rt_ctx *cx, double r, int err, int vanished) {
    if (err != 0 || (r != 0.0 && fpclassify(r) == FP_SUBNORMAL) || (r == 0.0 && vanished)) cx->underflowed = 1;
    return num(cx, r);
}

rt_value rt_num_sqrt(rt_ctx *cx, rt_value a) {
    double d = float_arg(cx, a, "sqrt");
    // perl dies `Can't take sqrt of -1` (T481); -0 is not below zero.
    if (d < 0.0) rt_fault(cx, "sqrt of a number below zero");
    errno = 0;
    double r = sqrt(d);
    return libm(cx, r, errno, 0);
}

rt_value rt_num_log(rt_ctx *cx, rt_value a) {
    double d = float_arg(cx, a, "log");
    if (d <= 0.0) rt_fault(cx, "log of zero or a number below zero");
    errno = 0;
    double r = log(d);
    return libm(cx, r, errno, 0);
}

rt_value rt_num_exp(rt_ctx *cx, rt_value a) {
    double d = float_arg(cx, a, "exp");
    errno = 0;
    double r = exp(d);
    return libm(cx, r, errno, 1);
}

rt_value rt_num_sin(rt_ctx *cx, rt_value a) {
    double d = float_arg(cx, a, "sin");
    errno = 0;
    double r = sin(d);
    return libm(cx, r, errno, d != 0.0);
}

rt_value rt_num_cos(rt_ctx *cx, rt_value a) {
    double d = float_arg(cx, a, "cos");
    errno = 0;
    double r = cos(d);
    return libm(cx, r, errno, 0);
}

// A negative zero, either side, is pi or 0, -pi or -0, by its past (T79).
rt_value rt_atan2(rt_ctx *cx, rt_value y, rt_value x) {
    double p = float_arg(cx, y, "atan2");
    double q = float_arg(cx, x, "atan2");
    if ((p == 0.0 && signbit(p)) || (q == 0.0 && signbit(q))) {
        rt_fault(cx, "a negative zero to atan2: perl's answer turns on whether the zero was used as an integer");
    }
    errno = 0;
    double r = atan2(p, q);
    return libm(cx, r, errno, p != 0.0);
}

// ---- hex and oct (D203)

// Digits of a base, with one `_` before the first or between two, which
// is what perl takes in silence; none at all is 0. -1 for anything else,
// and for a number past 32 bits, which perl warns is not portable.
static int64_t based(const char *p, const char *end, int base) {
    uint64_t v = 0;
    int after_underscore = 0;
    if (p < end && *p == '_') {
        p++;
        after_underscore = 1;
        if (p == end) return -1;
    }
    for (; p < end; p++) {
        if (*p == '_') {
            if (after_underscore || p + 1 == end) return -1;
            after_underscore = 1;
            continue;
        }
        after_underscore = 0;
        int d = *p >= '0' && *p <= '9' ? *p - '0' : *p >= 'a' && *p <= 'f' ? *p - 'a' + 10 : *p >= 'A' && *p <= 'F' ? *p - 'A' + 10 : 99;
        if (d >= base) return -1;
        v = v * (uint64_t)base + (uint64_t)d;
        if (v > 0xFFFFFFFFu) return -2;
    }
    return (int64_t)v;
}

static rt_value based_result(rt_ctx *cx, int64_t v, const char *name) {
    char what[160];
    if (v == -2) {
        snprintf(what, sizeof what, "%s of a number past 32 bits: perl warns that it is not portable", name);
        rt_fault(cx, what);
    }
    if (v < 0) {
        snprintf(what, sizeof what, "%s of a string that is not all digits of its base: perl warns, or stops there in silence", name);
        rt_fault(cx, what);
    }
    return rt_int(v);
}

rt_value rt_hex(rt_ctx *cx, rt_value a) {
    scratch none;
    const rt_str *s = to_str(cx, a, &none);
    const char *p = s->bytes;
    const char *end = p + s->len;
    if (end - p >= 2 && p[0] == '0' && (p[1] == 'x' || p[1] == 'X')) p += 2;
    else if (p < end && (*p == 'x' || *p == 'X')) p += 1;
    return based_result(cx, based(p, end, 16), "hex");
}

rt_value rt_oct(rt_ctx *cx, rt_value a) {
    scratch none;
    const rt_str *s = to_str(cx, a, &none);
    const char *p = s->bytes;
    const char *end = p + s->len;
    while (p < end && blank(*p)) p++;
    int base = 8;
    const char *q = p < end && *p == '0' ? p + 1 : p;
    char c = q < end ? *q : 0;
    if (c == 'x' || c == 'X') base = 16;
    else if (c == 'b' || c == 'B') base = 2;
    else if (c == 'o' || c == 'O') base = 8;
    if (c == 'x' || c == 'X' || c == 'b' || c == 'B' || c == 'o' || c == 'O') p = q + 1;
    return based_result(cx, based(p, end, base), "oct");
}

// ---- the bit operators (D204)

// Each operand a whole number by `substr`'s rule, as its 64 bits; the
// answer perl's unsigned integer, which from 2^63 the language does not
// have (T474).
static uint64_t bits_of(rt_ctx *cx, rt_value v) {
    return (uint64_t)whole_of(cx, v);
}

static rt_value unsigned_answer(rt_ctx *cx, uint64_t u) {
    if (u > (uint64_t)INT64_MAX) rt_fault(cx, "a bitwise answer of 2^63 or more: perl's is an unsigned integer, which the language does not have");
    return rt_int((int64_t)u);
}

rt_value rt_bit_and(rt_ctx *cx, rt_value a, rt_value b) {
    uint64_t x = bits_of(cx, a);
    uint64_t y = bits_of(cx, b);
    return unsigned_answer(cx, x & y);
}

rt_value rt_bit_or(rt_ctx *cx, rt_value a, rt_value b) {
    uint64_t x = bits_of(cx, a);
    uint64_t y = bits_of(cx, b);
    return unsigned_answer(cx, x | y);
}

rt_value rt_bit_xor(rt_ctx *cx, rt_value a, rt_value b) {
    uint64_t x = bits_of(cx, a);
    uint64_t y = bits_of(cx, b);
    return unsigned_answer(cx, x ^ y);
}

// `|=` and `^=` take an undef on the left for 0, in silence, as perl does;
// `&=` and the shifts do not (T477).
rt_value rt_bit_or_to(rt_ctx *cx, rt_value a, rt_value b) {
    return rt_bit_or(cx, a.tag == RT_TAG_UNDEF ? rt_int(0) : a, b);
}

rt_value rt_bit_xor_to(rt_ctx *cx, rt_value a, rt_value b) {
    return rt_bit_xor(cx, a.tag == RT_TAG_UNDEF ? rt_int(0) : a, b);
}

rt_value rt_bit_not(rt_ctx *cx, rt_value a) {
    return unsigned_answer(cx, ~bits_of(cx, a));
}

// A negative count shifts the other way, and 64 or more either way is 0,
// as perl 5.42 has it (T476); C leaves both undefined.
static uint64_t shifted(uint64_t u, int64_t count, int left) {
    if (count < 0) {
        left = !left;
        if (count == INT64_MIN) return 0;
        count = -count;
    }
    if (count >= 64) return 0;
    return left ? u << count : u >> count;
}

rt_value rt_shl(rt_ctx *cx, rt_value a, rt_value b) {
    uint64_t x = bits_of(cx, a);
    int64_t n = whole_of(cx, b);
    return unsigned_answer(cx, shifted(x, n, 1));
}

rt_value rt_shr(rt_ctx *cx, rt_value a, rt_value b) {
    uint64_t x = bits_of(cx, a);
    int64_t n = whole_of(cx, b);
    return unsigned_answer(cx, shifted(x, n, 0));
}

// ---- rand and srand (D205)

// perl's own generator, Perl_drand48_r of util.c, which is FreeBSD's
// drand48: so a seeded program prints what perl prints on every machine
// (T480). The seed is 32 bits.
static void seed_with(rt_ctx *cx, uint32_t seed) {
    cx->rand_state = UINT64_C(0x330E) + ((uint64_t)seed << 16);
    cx->rand_seeded = 1;
}

// A seed of the runtime's own choosing (D14): perl's comes from the
// system, and so does this.
static uint32_t any_seed(void) {
    uint64_t t = (uint64_t)time(NULL);
    uint64_t p = (uint64_t)getpid();
    struct timespec now;
    clock_gettime(CLOCK_MONOTONIC, &now);
    uint64_t mixed = t * UINT64_C(0x9E3779B97F4A7C15) ^ p * UINT64_C(0xBF58476D1CE4E5B9) ^ (uint64_t)now.tv_nsec;
    return (uint32_t)(mixed ^ (mixed >> 32));
}

static double drand(rt_ctx *cx) {
    if (!cx->rand_seeded) seed_with(cx, any_seed());
    cx->rand_state = (cx->rand_state * UINT64_C(0x5DEECE66D) + UINT64_C(0xB)) & UINT64_C(0xFFFFFFFFFFFF);
    return ldexp((double)cx->rand_state, -48);
}

rt_value rt_rand(rt_ctx *cx, rt_value n) {
    double v = as_double(numeric(cx, n));
    if (v == 0.0) v = 1.0;
    return num(cx, v * drand(cx));
}

rt_value rt_rand0(rt_ctx *cx) {
    return num(cx, drand(cx));
}

static const rt_str ZERO_BUT_TRUE = { 10, 10, "0 but true", RT_STR_CONSTANT };

static rt_value seeded(rt_ctx *cx, int64_t n) {
    seed_with(cx, (uint32_t)(uint64_t)n);
    return n == 0 ? rt_string(&ZERO_BUT_TRUE) : rt_int(n);
}

// perl reads srand's argument as a string of digits (T479): `srand(-1)`
// is `srand(1)`, `srand(1e-5)` overflows. So what is taken is what is
// digits as a string: an Int of 0 or more, a whole Num below 10^15, a
// string of digits alone.
rt_value rt_srand(rt_ctx *cx, rt_value v) {
    const char *why = "srand of a negative number, a fraction, a boolean or a string that is not digits alone: perl reads its argument as a string of digits";
    if (v.tag == RT_TAG_INT) {
        if (v.as.i < 0) rt_fault(cx, why);
        return seeded(cx, v.as.i);
    }
    if (v.tag == RT_TAG_NUM) {
        double d = v.as.n;
        if (!(d >= 0.0 && d < 1e15 && d == trunc(d))) rt_fault(cx, why);
        return seeded(cx, (int64_t)d);
    }
    if (v.tag == RT_TAG_STR) {
        const rt_str *s = alive(cx, v.as.s);
        if (s->len == 0) rt_fault(cx, why);
        uint64_t m = 0;
        for (uint64_t k = 0; k < s->len; k++) {
            char c = s->bytes[k];
            if (!digit(c)) rt_fault(cx, why);
            int o = __builtin_mul_overflow(m, (uint64_t)10, &m);
            o |= __builtin_add_overflow(m, (uint64_t)(c - '0'), &m);
            if (o || m > (uint64_t)INT64_MAX) rt_fault(cx, "integer overflow");
        }
        return seeded(cx, (int64_t)m);
    }
    if (v.tag == RT_TAG_BOOL) rt_fault(cx, why);
    (void)numeric(cx, v);
    rt_fault(cx, why);
}

rt_value rt_srand0(rt_ctx *cx) {
    return seeded(cx, any_seed());
}

// ---- time (D206)

// The seconds since the epoch; under the virtual clock, CURLY_TIME,
// always the same.
rt_value rt_time(rt_ctx *cx) {
    if (cx->clock != 0) return rt_int((int64_t)cx->clock);
    return rt_int((int64_t)time(NULL));
}
