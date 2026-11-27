# quotemeta past ASCII, by perl's own table: some characters are quoted, most are not (D256).
use v5.42;
use utf8;
use open ":std", ":encoding(UTF-8)";
say quotemeta("é-ß");
say length quotemeta(chr(0xAD)), length quotemeta(chr(0x2028)), length quotemeta(chr(0x263A)), length quotemeta(chr(0x10FFFD));
say "\Qa b\E";
