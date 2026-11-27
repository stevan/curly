# t/models/io.py 4708
# stdin: \0303\0251\n\0342\0230\0272 and \0342\0230\0272\n\0360\0237\0230\0200x\n\0357\0273\0277\nplain
use v5.42;
use utf8;
use open ':std', ':encoding(UTF-8)';
while (my $line = <STDIN>) {
    print length($line), " ", ord($line), " ", $line;
}
say "";
