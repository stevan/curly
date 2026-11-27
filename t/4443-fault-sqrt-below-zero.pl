# kind: fault
# perl dies: Can't take sqrt of -1e-300 (T481).
use v5.42;
say sqrt(0);
say sqrt(-1e-300);
