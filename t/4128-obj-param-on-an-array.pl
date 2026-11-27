# kind: refused
# perl dies (17-param-array): Only scalar fields can take a :param attribute.
use v5.42;
use experimental 'class';
class P { field @a :param; }
