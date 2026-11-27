# kind: fault
# perl seeds as srand(1), and gives 1 (T479).
use v5.42;
srand(-1);
