# kind: refused
# perl dies (T409-reopen): Cannot reopen existing class "P".
use v5.42;
use experimental 'class';
class P { }
class P { }
