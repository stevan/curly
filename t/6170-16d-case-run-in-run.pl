# kind: refused
# perl ends the \U at the \L: 'ABcdef'.
use v5.42;
say "\Uab\Lcd\Eef";
