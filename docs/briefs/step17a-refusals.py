#!/usr/bin/env python3
# Writes step 17a's refusal tests from a table written by hand: the program,
# the text the message points at (its column is counted here, from the
# program's own text), and the message. Nothing here asks the compiler.
# What perl does with each is in its comment, from perl 5.42 run plain
# (`python3 docs/briefs/step17a-refusals.py --perl` prints each again).
# Every program has `use experimental 'class';` after `use v5.42;` but
# the one marked `bare`.
#
#     python3 docs/briefs/step17a-refusals.py 4100
import subprocess
import sys
T = []
def r(name, why, body, at, message, nth=1, bare=False):
    T.append((name, why, body, at, message, nth, bare))

LATER = "a later part of {} can change {}, which an earlier part names: perl reads it after the change; take the value into a my first"
PIECE = "a later piece of a concatenation calls {}, which can change {}, which an earlier piece reads: perl joins the pieces as one operation and reads each late; make the call a statement of its own"
RESERVED = "{}: perl gives the name a meaning of its own, and the method is not what a call of it reaches (D178, T409, T416, T423)"
BLOCK = "{} in a class's block: it holds field, method, my method and ADJUST, and perl runs anything else where the block stands (D171, T408)"
BARE = "{0}(...) in a class: perl looks it up in the class's package, P::{0}, and dies there (D178, T422); write main::{0}(...)"
HELPER = 'sub helper($n) {\n    return "h$n";\n}\n'
UNIVERSAL = "->{}: the methods UNIVERSAL gives every object are not in the language (T416)"

# ---- the class statement (D171, D174, D177, D178)
r('class-without-the-pragma', "perl does not compile it: Bareword found where operator expected (Do you need to predeclare \"class\"?)", 'class P { }', 'class', "class needs use experimental 'class'; at the top, with the pragmas: perl 5.42 does not compile it without", bare=True)
r('pragma-late', "perl runs it (R17-17-pragma-late): the pragma may stand after a statement.", 'say "a";\nuse experimental \'class\';', 'use experimental', "'use experimental' goes at the top, after 'use v5.42;' and before anything else", nth=2)
r('pragma-other-feature', "perl runs it, and says nothing.", 'use experimental \'signatures\';', 'use experimental', "'use experimental' is written: use experimental 'class';", bare=True)
r('class-in-a-block', "perl runs it: a class may be declared in a block.", '{\n    class P { }\n}', 'class P', 'a class stands at the top level of the file: not in a block, a loop or a sub')
r('class-statement-form', "perl runs it (17-stmt-form): the class runs to the end of the file or the next package.", 'class P;', ';', 'class P; with no block: a class that runs to the end of the file is not in the language yet (D174); class P { ... }', nth=3)
r('class-version', "perl runs it (17-version): P->VERSION is 1.5.", 'class P 1.5 { }', '1.5', 'class P and a version: not in the language yet (D174)')
r('isa-version', "perl dies: A does not define $A::VERSION--version check failed.", 'class A { }\nclass B :isa(A 1.5) { }', '1.5', 'a version in :isa(...) is not in the language yet (D174)')
r('class-lower-case-part', "perl runs it: the class is Foo::bar.", 'class Foo::bar { }', 'Foo::bar', "class Foo::bar: every part of a class's name begins with a capital letter (D178): perl takes other names for its own words, its packages or a version (T426)")
r('class-held-package', "perl dies (R17-05-class-carp): Cannot create class Carp as it already has a non-empty @ISA.", 'class Carp { }', 'Carp', 'class Carp: perl holds the package Carp by the end of the preamble, and a class of it is that package or one inside it (D178, T426)')
r('class-inside-a-held-package', "perl runs it: IO::Thing is a package of its own beside IO's.", 'class IO::Thing { }', 'IO::Thing', 'class IO::Thing: perl holds the package IO by the end of the preamble, and a class of it is that package or one inside it (D178, T426)')
r('class-perl-word-part', "perl runs it: the class is P::STDIN.", 'class P::STDIN { }', 'P::STDIN', "class P::STDIN: STDIN is perl's own name (D178, T426)")
r('class-object', "perl runs it (T415): Object is a name like any other to perl.", 'class Object { }', 'Object', 'class Object: Object, Role and Class are the runtime\'s own, held back until the metaobject protocol shows them (D177, T415)')
r('class-class', "perl runs it (T415).", 'class Class { }', 'Class', 'class Class: Object, Role and Class are the runtime\'s own, held back until the metaobject protocol shows them (D177, T415)')
r('class-twice', "perl dies (T409-reopen): Cannot reopen existing class \"P\".", 'class P { }\nclass P { }', 'P', 'class P again: perl dies, "Cannot reopen existing class" (T409)', nth=2)
r('class-and-sub', "perl compiles it; a call P->new calls the sub, and dies (T407): Can't locate object method \"new\" via package \"sub\".", 'sub P() {\n    return "sub";\n}\nclass P { }', 'P {', 'class P and a sub of the same name: perl calls the sub, and takes what it gives for the class (T407)')
r('parent-below', "perl dies (T410): Can't locate A.pm in @INC.", 'class B :isa(A) { }\nclass A { }', 'A)', ':isa(A): the parent is a class declared above this one; to perl any other is a module to load (T410)')
r('parent-object', "perl dies: Can't locate Object.pm in @INC.", 'class B :isa(Object) { }', 'Object', ':isa(Object): Object, Role and Class are held back (D177)')
r('isa-twice', "perl dies: Class already has a superclass, cannot add another.", 'class A { }\nclass B :isa(A) :isa(A) { }', 'isa', ':isa twice: a class has one parent', nth=2)
r('statement-in-the-block', "perl runs it where the block stands (T408-statements): before, in class body, after.", 'class P { say "x"; }', 'say', BLOCK.format("'say'"))
r('my-in-the-block', "perl runs it where the block stands (T408): a method that reads it before then sees undef.", 'class P { my $c = 10; }', 'my', "a my in a class's block, which perl runs where the block stands, so that it is undef until then (D171, T408); a field says it")
r('sub-in-the-block', "perl runs it (T411-sub): a sub called as a method, with the class's name or an object first.", 'class P { sub make() { 1 } }', 'sub', "a sub in a class, which perl calls as a method with the class's name or an object first (D171, T411); a method says it")
r('pragma-in-the-block', "perl runs it.", 'class P { use utf8; }', 'use', "a pragma in a class's block (D171): the pragmas go at the top of the file", nth=2)
r('class-in-a-class', "perl runs it: Q is a class of its own.", 'class P { class Q { } }', 'class Q', 'a class in a class (D171)')
r('field-outside', "perl does not compile it: field is only valid inside a class.", 'field $x;', 'field', "field outside a class's block: it is a declaration of a class, class NAME { field ... }")
r('method-outside', "perl does not compile it: method is only valid inside a class.", 'method m { 1 }', 'method', "method outside a class's block: it is a declaration of a class, class NAME { method ... }")
r('adjust-outside', "perl does not compile it.", 'ADJUST { 1 }', 'ADJUST', "ADJUST outside a class's block: it is a declaration of a class, class NAME { ADJUST ... }")

# ---- fields (T401, T430, T434, T436)
r('field-self', "perl runs it (R17-09-field-self): the method's $self is the field.", 'class P { field $self = 1; }', '$self', 'field $self: perl hides the object behind it, in silence (D178, T430); choose another name')
r('field-twice', "perl warns: \"field\" variable $x masks earlier declaration in same scope.", 'class P { field $x; field $x; }', '$x', 'field $x again in one class: perl warns that it masks the first', nth=2)
r('param-on-an-array', "perl dies (17-param-array): Only scalar fields can take a :param attribute.", 'class P { field @a :param; }', 'param', ':param on @a: perl takes it on a scalar field alone')
r('writer-on-an-array', "perl dies (17-writer-array): Cannot apply a :writer attribute to a non-scalar field.", 'class P { field @a :writer; }', 'writer', ':writer on @a: perl takes it on a scalar field alone')
r('param-twice', "perl dies: Field already has a parameter name, cannot add another.", 'class P { field $x :param :param; }', 'param', ':param twice on one field (T434)', nth=2)
r('reader-twice', "perl runs it (R17-13-attr-repeated): two readers.", 'class P { field $x :reader :reader(q); }', 'reader', ':reader twice on one field: perl makes two readers (T434)', nth=2)
r('attribute-blank-after-colon', "perl runs it (T434): ': param' is ':param'.", 'class P { field $x : param; }', ':', "an attribute is written hard against its colon, :param; perl takes ': param' too, and the language does not")
r('attribute-blank-before-bracket', "perl does not compile it (R17-13-attr-blank): Invalid separator character '(' in attribute list.", 'class P { field $x :param (y); }', '(y)', 'a blank between :param and its bracket: perl does not compile it (T434)')
r('attribute-blank-inside', "perl runs it (T434): the blank is trimmed, and the name is y.", 'class P { field $x :param( y); }', 'y)', ':param(...) takes a name hard against its brackets, :param(name); perl trims the blanks, and the language does not (T434)')
r('attribute-empty', "perl runs it (T434): :param() is the field's own name.", 'class P { field $x :param(); }', '()', ':param() with nothing in its brackets: write :param for the field\'s own name (T434)')
r('attribute-unknown', "perl dies: Unrecognized field attribute weak.", 'class P { field $x :weak; }', 'weak', ':weak is not an attribute the language has here: :param, :reader, :writer')
r('defined-or-without-param', "perl runs it: the default is taken, as with =.", 'class P { field $x //= 3; }', '//=', "'//=' on a field with no :param: a default with //= is for a parameter that may be given undef or false")
r('field-comma', "perl does not compile it: syntax error, near \"1,\".", 'class P { field @a = 1, 2; }', ',', "a comma after a field's default: perl takes the field and its default for the first item of a list; put the list in brackets")
r('field-modifier', "perl does not compile it: syntax error.", 'class P { field $x = 1 if 1; }', 'if', 'if after a field: a field is declared whatever happens; a modifier is not in the language there')
r('param-collides-with-a-parent', "perl dies (17-param-collide): Cannot assign :param(x) to field $z because that name is already in use.", 'class A { field $x :param; }\nclass B :isa(A) { field $z :param(x); }', 'x)', ':param(x) where the name is a parameter of this class or a parent already: perl dies, "that name is already in use"')
r('field-default-self', "perl does not compile it (T401): Global symbol \"$self\" requires explicit package name.", 'class P { field $x = 2; field $y = $self; }', '$self', "$self in a field's default: perl does not compile it (T401); a field's default sees the fields above it, and an ADJUST block sees $self")
r('field-read-above', "perl does not compile it (R17-09-field-after-method): Global symbol \"$x\" requires explicit package name.", 'class P { method m { $x } field $x = 1; }', '$x', '$x is not declared: my $x')
r('field-die-over-two-lines', "perl names the field's first line (T436): no y at FILE line 5.", 'class P {\n    field $y :param\n        = die "no y";\n}', 'die', 'a die in a statement, a test or a header over more than one line: perl names a line of its own choosing there, and the message would carry it; put it on one line, or end the message in a newline')

# ---- methods' names (T409, T416, T419, T423, T424, T425)
r('method-without-a-block', "perl runs it (T419), and the call dies: Undefined subroutine &P::m.", 'class P { method m; }', ';', "method m; with no block: perl takes it, and dies when it is called (T419); a role's required method is step 17b's", nth=3)
r('method-new', "perl warns (T409-new): Subroutine new redefined; and new is lost.", 'class P { method new { 1 } }', 'new', RESERVED.format('method new'))
r('method-isa', "perl runs it (T416-own): the class's own isa wins over UNIVERSAL's.", 'class P { method isa($c) { 1 } }', 'isa', RESERVED.format('method isa'))
r('method-destroy', "perl runs it (T416-destroy) as the object goes.", 'class P { method DESTROY { 1 } }', 'DESTROY', RESERVED.format('method DESTROY'))
r('method-end', "perl takes it for an END block (R17-02-method-end).", 'class P { method END { 1 } }', 'END', RESERVED.format('method END'))
r('method-floor', "perl warns (R17-02-method-floor-ceil): Prototype mismatch, Subroutine floor redefined; the method is never installed.", 'class P { method floor { 1 } }', 'floor', RESERVED.format('method floor'))
r('reader-trim', "perl runs it: a reader is installed over an import.", 'class P { field $trim :reader = 1; }', 'reader', RESERVED.format('the reader trim'))
r('writer-stdout', "perl runs it: set_x is a method.", 'class P { field $x :writer(STDOUT); }', 'STDOUT', RESERVED.format('the writer STDOUT'))
r('method-underscores', "perl runs it.", 'class P { method __x { 1 } }', '__x', "method __x: a name perl reads as one of its own words or a version")
r('my-method-perl-word', "perl takes it for every join below it (R17-03-my-method-join).", 'class P { my method join { 1 } }', 'join', "my method join: a my method of a word of perl's takes every use of the word below it (D178, T424)")
r('method-twice', "perl warns (T409): Method m redefined, and takes the last.", 'class P { method m { 1 } method m { 2 } }', 'm {', 'method m again in class P: perl warns that it is redefined, and takes the last (T409)', nth=2)
r('method-and-reader', "perl warns (T409-reader): Method x redefined.", 'class P { field $x :reader = 1; method x { 2 } }', 'x {', 'method x again in class P: perl warns that it is redefined, and takes the last (T409)')
r('my-method-and-method', "perl warns (R17-03-my-and-public-same): Method b redefined, and the call dies.", 'class P { my method b { 1 } method b { 2 } }', 'b {', 'method b again in class P: perl warns that it is redefined, and takes the last (T409)', nth=2)
r('method-named-as-a-class', "perl calls the method for the class's name below it (R17-04-method-hides-class).", 'class Q { }\nclass P { method Q { 1 } }', 'Q {', 'method Q where a class is called Q: perl takes the class\'s name for a call of the method (D178, T425)', nth=2)
r('method-hides-an-inner-class', "perl calls the method for A::B (R17-04-method-hides-class-everywhere).", 'class A { method B { 1 } }\nclass A::B { }', 'B {', 'method B where a class is called A::B: perl takes the class\'s name for a call of the method (D178, T425)')

# ---- names in a class (T430, T432, T413)
r('self-parameter', "perl runs it (R17-09-self-param): $self is the argument.", 'class P { method m($self) { 1 } }', '$self', '$self declared again in a class: perl hides the object behind it, in silence (D178, T430); choose another name')
r('my-self', "perl runs it (R17-09-my-self).", 'class P { method m { my $self = 3; return $self } }', 'my $self', '$self declared again in a class: perl hides the object behind it, in silence (D178, T430); choose another name')
r('parameter-shadows-a-field', "perl runs it (R17-09-param-shadows-field): the parameter, in silence.", 'class P { field $x = 1; method m($x) { $x } }', '$x)', '$x declared in a class with a field $x: perl hides the field behind it, in silence (D178, T430); choose another name')
r('my-shadows-a-field', "perl runs it: the my, in silence.", 'class P { field @a; method m { my @a = (1); return scalar(@a) } }', 'my @a', '@a declared in a class with a field @a: perl hides the field behind it, in silence (D178, T430); choose another name')
r('loop-variable-shadows-a-field', "perl runs it.", 'class P { field $x = 1; method m { for my $x (1, 2) { say $x } return } }', 'my $x', '$x declared in a class with a field $x: perl hides the field behind it, in silence (D178, T430); choose another name')
r('self-assigned', "perl runs it (T413): $self is a variable.", 'class P { method m { $self = 1; return } }', '=', '$self is read-only (D175, T413): perl lets a method assign it, and the object is lost to the rest of the method')
r('reference-to-self', "perl runs it (R17-11-sref-self): a store through the reference replaces the object.", 'class P { method m { my $r = \\$self; return $r } }', '\\$self', '\\$self: to perl it is the variable that holds the object, and a store through it replaces the object (D178, T432); the object itself, $self, is a reference already')
r('bare-call-in-a-method', "perl dies (R17-01-sub-from-method): Undefined subroutine &P::helper.", HELPER + 'class P { method m { helper(1) } }', 'helper(1)', BARE.format('helper'))
r('bare-call-in-a-default', "perl dies (R17-01-sub-from-field): Undefined subroutine &P::helper.", HELPER + 'class P { field $id = helper(2); }', 'helper(2)', BARE.format('helper'))
r('bare-call-in-an-adjust', "perl dies: Undefined subroutine &P::helper.", HELPER + 'class P { ADJUST { helper(3) } }', 'helper(3)', BARE.format('helper'))
r('bare-call-in-a-closure', "perl dies: Undefined subroutine &P::helper, when the closure runs.", HELPER + 'class P { method m { return sub { helper(4) } } }', 'helper(4)', BARE.format('helper'))
r('sub-reference-in-a-class', "perl takes \\&P::helper, which is no sub.", HELPER + 'class P { method m { return \\&helper } }', '\\&helper', '\\&helper in a class: perl takes the class\'s package\'s sub, \\&P::helper (D178, T422); write \\&main::helper')
r('method-called-as-a-function', "perl runs it as a function (T411-function), and dies for another class's object.", 'class P { method m { 1 } }\nmy $x = P::m(P->new);', 'P::m', 'P::m(...): a sub of another package, or a method called as a function, which is not in the language (T411); call a method as $obj->m(...)')

# ---- calls (T405, T411, T416, T417, T424, T431; D172, D173)
r('new-on-an-object', "perl runs it (T411-new-on-object): an object of P.", 'class P { }\nmy $p = P->new;\nmy $q = $p->new;', 'new;', '->new: new is called on a class\'s name (D173): NAME->new(...), or __CLASS__->new(...) in a method', nth=2)
r('super-new', "perl runs it (R17-10-super-new): an object of the parent.", 'class A { }\nclass B :isa(A) { method c { $self->SUPER::new } }', 'SUPER::new', '->SUPER::new: new is called on a class\'s name (D173): NAME->new(...), or __CLASS__->new(...) in a method')
r('universal-isa', "perl runs it (T416): 1.", 'class P { }\nmy $x = P->new->isa("P");', 'isa', UNIVERSAL.format('isa') + ': the operator says it, $o isa NAME')
r('universal-can', "perl runs it (T416): a code reference.", 'class P { }\nmy $x = P->new->can("new");', 'can', UNIVERSAL.format('can'))
r('universal-does', "perl runs it (T416): 1.", 'class P { }\nmy $x = P->new->DOES("P");', 'DOES', UNIVERSAL.format('DOES'))
r('next-method', "perl dies (T417): Can't locate object method \"method\" via package \"next\".", 'class A { method m { 1 } }\nclass B :isa(A) { method m { $self->next::method() } }', 'next::method', "->next::method: perl's next::method is not in the language (T417); $self->SUPER::m(...) says it")
r('qualified-method', "perl runs it (R17-10-qualified-method) with no dispatch.", 'class A { method m { 1 } }\nmy $x = A->new->A::m;', 'A::m', '->A::m: a method named with its class is called with no dispatch, and is not in the language (T431); $self->SUPER::m(...) calls the parent\'s')
r('super-on-another-object', "perl dies (R17-10-super-other-invocant): Can't locate object method \"m\" via package \"C\".", 'class A { method m { 1 } }\nclass C { method go($o) { $o->SUPER::m } }', 'SUPER::m', '->SUPER::m on what is not $self: perl takes the parent of the class it is written in whatever the object, and the language calls it on $self alone (D178, T431)')
r('super-with-no-parent', "perl dies when the call is made: Can't locate object method \"m\" via package \"P::SUPER\".", 'class P { method m { $self->SUPER::m } }', 'SUPER::m', '->SUPER::m: class P has no parent, and perl dies when the call is made')
r('super-not-in-the-parent', "perl dies when the call is made.", 'class A { }\nclass B :isa(A) { method m { $self->SUPER::m } }', 'SUPER::m', '->SUPER::m: no parent of B has a method called m, and perl dies when the call is made')
r('lexical-on-another-object', "perl runs it (R17-03-arrow-amp-other) on another object of the class, and dies of another class's.", 'class P { my method b { 1 } method a($o) { $o->&b() } }', 'b()', '->&b: a my method is called on $self alone (D178, T424): perl calls it on any object, of any class, with no dispatch')
r('lexical-of-a-public-method', "perl runs it (R17-03-arrow-amp-public) with no dispatch: P.b where dispatch gives Q.b.", 'class P { method a { $self->&b() } method b { 1 } }', 'b()', '->&b: class P has no my method called b; perl calls the sub of that name in the class\'s package, with no dispatch (D178, T424)')
r('lexical-above-its-method', "perl dies (R17-03-lexical-before-declared): Undefined subroutine &P::b.", 'class P { method a { $self->&b() } my method b { 1 } }', 'b()', '->&b above its my method: perl does not see it there, and dies (D178, T424); declare the my method first')
r('lexical-outside-a-class', "perl dies (17-amp-outside): Undefined subroutine &main::m.", 'class P { method m { 1 } }\nmy $self = P->new;\nmy $x = $self->&m;', 'm;', '->&m: a my method is called on $self alone (D178, T424): perl calls it on any object, of any class, with no dispatch')
r('method-blank-before-its-bracket', "perl runs it (17-call-forms): the brackets are the arguments.", 'class P { method m($x) { $x } }\nmy $x = P->new->m (1);', '(1)', "a blank between the method's name m and its bracket: perl takes it, and reads on; write it hard against the name, ->m(...)")
r('method-no-class-has', "perl dies when the call is made (17-missing): Can't locate object method \"nope\" via package \"P\".", 'class P { }\nP->new->nope;', 'nope', '->nope: no class of the program has a method called nope, and perl dies when the call is made')
r('method-by-a-variable', "perl calls the method the variable names.", 'class P { method m { 1 } }\nmy $m = "m";\nmy $x = P->new->$m;', '->$m', "'->' and a variable: a method chosen by what a variable holds is not in the language yet")
r('class-method', "perl dies (T411-class): Cannot invoke method \"m\" on a non-instance.", 'class P { method m { 1 } }\nP->m;', 'm;', 'P->m: a method called on a class\'s name, which perl calls with the name for its object and which dies "Cannot invoke method on a non-instance" for a method of a class (T411); P->new(...) makes an object')
r('new-of-no-class', "perl dies: Can't locate object method \"new\" via package \"Q\" (perhaps you forgot to load \"Q\"?).", 'class P { }\nmy $q = Q->new;', 'Q->new', 'Q->new: the program has no class called Q')
r('new-of-object', "perl dies: Can't locate object method \"new\" via package \"Object\".", 'my $o = Object->new;', 'Object', 'Object->new: Object, Role and Class are held back (D177)')
r('new-indirect', "perl does not compile it (17-indirect): syntax error.", 'class P { }\nmy $p = new P;', 'new', "'new' is not in the language; a call of a sub of the program's has brackets: new(...)")
r('curclass-outside', "perl does not compile it: Cannot use __CLASS__ outside of a method or field initializer expression.", 'my $c = __CLASS__;', '__CLASS__', '__CLASS__ outside a method, an ADJUST block or a field\'s default: perl does not compile it there')
r('curclass-in-a-closure', "perl does not compile it: Cannot use __CLASS__ outside of a method or field initializer expression.", 'class P { method m { return sub { __CLASS__ } } }', '__CLASS__', '__CLASS__ outside a method, an ADJUST block or a field\'s default: perl does not compile it there')
r('curclass-method', "perl dies: Cannot invoke method \"m\" on a non-instance.", 'class P { method m { 1 } method n { __CLASS__->m } }', 'm }', '__CLASS__->m: a method called on a class\'s name, which perl calls with the name for its object and which dies "Cannot invoke method on a non-instance" for a method of a class (T411); __CLASS__->new(...) makes an object')
r('isa-no-class', "perl runs it (17-isa): false for any other name.", 'class P { }\nmy $x = P->new isa Nope;', 'isa', 'isa Nope: the program has no class called Nope; perl gives false for any other name (17-isa)')
r('isa-object', "perl runs it (T415): 0.", 'class P { }\nmy $x = P->new isa Object;', 'isa', 'isa Object: Object, Role and Class are held back until the metaobject protocol shows them (D177, T415)')
r('isa-a-variable', "perl runs it: the class is named by what the variable holds.", 'class P { }\nmy $c = "P";\nmy $x = P->new isa $c;', '$c;', "after isa comes a class's name, found '$c': a class named by what a value holds is not in the language")
r('isa-after-not', "perl warns: Possible precedence problem between ! and derived class test.", 'class P { }\nmy $p = P->new;\nmy $x = !$p isa P;', '!', "'!' before 'isa': perl warns of a precedence problem; write !(... isa ...)")
r('blessed-before-a-dot', "perl takes all of it for blessed's argument, and warns of an undef.", 'class P { }\nmy $p = P->new;\nsay blessed $p . "x";', 'blessed', "blessed before '.': perl takes all of it for blessed's argument, which is then no reference; write blessed(...) . ...")

# ---- the walks (D57, D69, D76, D77, T230's rule; D172, D178)
r('new-default-changes-an-argument', "perl prints 9 (R17-06-new-element-late): the argument is read at its field's turn.", 'my @a = (1, 2);\nclass P { field $z = ($a[0] = 9); field $x :param :reader; }\nsay P->new(x => $a[0])->x;', 'P->new', LATER.format('the arguments of P->new', '@a'))
r('new-default-shifts-an-argument', "perl prints 1 2 3 (R17-06-new-element-shifted): the element shifted out is still the old scalar.", 'my @a = (1, 2, 3);\nclass P { field $z = shift(@a); field $x :param :reader; }\nsay P->new(x => $a[0])->x, " @a";', 'P->new', LATER.format('the arguments of P->new', '@a'))
r('new-adjust-in-a-row-of-dots', "perl prints ab-c (R17-07-new-adjust-concat).", 'my $log = "a";\nclass P { ADJUST { $log .= "b" } method v { "c" } }\nsay $log . "-" . P->new->v;', 'P->new', PIECE.format('P->new', '$log'))
r('new-default-in-a-row-of-dots', "perl prints ab-c (R17-07-new-field-concat).", 'my $log = "a";\nclass P { field $f = ($log .= "b"); method v { "c" } }\nsay $log . "-" . P->new->v;', 'P->new', PIECE.format('P->new', '$log'))
r('curclass-new-of-a-class-below', "perl prints abb-c (R17-07-class-new-subclass): Q's ADJUST runs for __CLASS__->new written in P.", 'my $log = "a";\nclass P { method clone { __CLASS__->new } method v { "c" } }\nclass Q :isa(P) { ADJUST { $log .= "b" } }\nmy $q = Q->new;\nsay $log . "-" . $q->clone->v;', 'clone->', PIECE.format('the method clone', '$log'))
r('new-adjust-in-a-list', "perl prints 9c (R17-07-new-adjust-list).", 'my @a = (1);\nclass P { ADJUST { $a[0] = 9 } method v { "c" } }\nsay $a[0], P->new->v;', 'v;', LATER.format("say's list", '@a'))
r('writer-in-a-row-of-dots', "perl prints b-Pb (R17-07-writer-concat).", 'class P { field $x :writer = "a"; method go { $x . "-" . ref($self->set_x("b")) . $x } }', 'set_x("b', PIECE.format('the method set_x', '$x'))
r('method-in-a-row-of-dots', "perl reads $n late: the method's store shows.", 'my $n = 1;\nclass P { method bump { $n = 5; return "!" } }\nsay $n . P->new->bump;', 'bump;', PIECE.format('the method bump', '$n'))
r('invocant-element-changed', "perl prints 2:x (R17-08-invocant-element): the element is read at the call.", 'class P { field $n :param; method m($x) { "$n:$x" } }\nmy @a = (P->new(n => 1));\nsay $a[0]->m(($a[0] = P->new(n => 2)) ? "x" : "y");', '?', LATER.format('the call of the method m', '@a'))
r('invocant-hash-element-changed', "perl prints 2:x (R17-08-invocant-helem).", 'class P { field $n :param; method m($x) { "$n:$x" } }\nmy %h = (k => P->new(n => 1));\nsay $h{k}->m(($h{k} = P->new(n => 2)) ? "x" : "y");', '?', LATER.format('the call of the method m', '%h'))
r('invocant-chain-changed', "perl prints 2:x (R17-08-invocant-chain).", 'class P { field $n :param; method m($x) { "$n:$x" } }\nmy $r = [P->new(n => 1)];\nsay $r->[0]->m(($r->[0] = P->new(n => 2)) ? "x" : "y");', '?', LATER.format('the call of the method m', 'what references reach'))
r('loop-over-a-field-a-method-changes', "perl's loop walks the field itself, and sees the store.", 'class P { field $x = 1; method set { $x = 5; return } method go { for my $v ($x, 2) { $self->set } return } }', 'set }', "this can change $x, which the list of the loop it is in names: perl's loop walks the variable itself; take the value into a my before the loop")
r('key-changed-by-a-method', "perl joins the pieces as it stores, after the key is worked out (T230).", 'my $v = "a";\nclass P { method k { $v = "b"; return "k" } }\nmy %h;\n$h{P->new->k} = $v . "!";', 'k}', 'the key changes $v, which the concatenation on the right reads: perl joins its pieces as it stores, after the key is worked out; take the string into a my first')

# ---- five more, which the breakages of the step showed no test reached
# (briefs/step17a-mutations.py): they are written from 4214.
r('isa-after-isa', "perl does not compile it: syntax error.", 'class A { }\nclass B { }\nmy $x = A->new isa A isa B;', 'isa B', "'isa' after 'isa': perl does not compile it")
r('field-of-the-parent', "perl does not compile it (T56): Global symbol \"$x\" requires explicit package name.", 'class A { field $x = 1; }\nclass B :isa(A) { method m { $x } }', '$x }', '$x is not declared: my $x')
r('method-of-a-second-class-in-a-row-of-dots', "perl reads $n late: the store of B's method shows.", 'my $n = 1;\nclass A { method bump { "a" } }\nclass B { method bump { $n = 5; return "!" } }\nsay $n . B->new->bump;', 'bump;', PIECE.format('the method bump', '$n'))
r('argument-before-a-method-that-gives-a-list', "perl hands the sub $x itself, and reads it after the method stored 5: 5.", 'my $x = 1;\nsub first(@l) {\n    return $l[0];\n}\nclass A { method parts { $x = 5; return (1, 2) } }\nsay first($x, A->new->parts);', 'parts);', LATER.format('the arguments of first', '$x'))
r('field-list-where-one-value', "perl gives the last value, and warns (17-field-list-scalar): Useless use of a constant in void context.", 'class P { field $x = (4, 5, 6); }', '(4', 'a list where one value is wanted: perl gives its last value, and warns of the others')

# ---- three more, found finishing the step: `isa` is of the comparisons' row
# to perl, and what binds tighter takes its class's name for a bareword. The
# compiler read each from the left, and printed where perl does not compile.
r('operator-after-isa', "perl does not compile it: Bareword \"A\" not allowed while \"strict subs\" in use.", 'class A { }\nmy $o = A->new;\nsay $o isa A - 1;', '- 1', "'-' after isa and its class: perl does not compile it; write (... isa A) - ...")
r('comparison-after-isa', "perl does not compile it: syntax error, near \"A <\".", 'class A { }\nmy $o = A->new;\nmy $x = $o isa A < 2;', '< 2', "'<' after isa and its class: perl does not compile it; write (... isa A) < ...")
r('comparison-before-isa', "perl does not compile it: syntax error, near \"$o isa\".", 'class A { }\nmy $o = A->new;\nmy $x = 2 ge $o isa A;', 'isa A;', "'ge' before an isa: perl does not compile it; write ... ge (... isa A)")

def write(first, table=None):
    n = first
    for name, why, body, at, message, nth, bare in (T if table is None else table):
        program = f'# kind: refused\n# {why}\nuse v5.42;\n' + ('' if bare else "use experimental 'class';\n") + f'{body}\n'
        path = f't/{n}-obj-{name}'
        open(path + '.pl', 'w', encoding='utf-8').write(program)
        k = program.index('use v5.42;')
        for _ in range(nth):
            k = program.index(at, k + 1)
        line = program.count('\n', 0, k) + 1
        col = len(program[program.rfind('\n', 0, k) + 1:k]) + 1
        open(path + '.expected', 'w', encoding='utf-8').write(f'{path}.pl:{line}:{col}: {message}\nexit: 1\n')
        n += 1

if __name__ == '__main__':
    if sys.argv[1] == '--perl':
        import os
        for name, why, body, at, message, nth, bare in T:
            src = 'use v5.42;\n' + ('' if bare else "use experimental 'class';\n") + body
            r_ = subprocess.run([os.environ.get('CURLY_PERL', 'perl'), '-e', src], capture_output=True, text=True, timeout=10)
            print(f'{name}: exit {r_.returncode}; {r_.stdout!r}; {r_.stderr.strip()[:200]!r}')
    else:
        write(int(sys.argv[1]))
