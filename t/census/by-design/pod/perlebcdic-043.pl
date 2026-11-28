use v5.42;
printf("%c",utf8::unicode_to_native(65));  # prints A on all
                                           # platforms
print utf8::native_to_unicode(ord("A"));   # Likewise, prints 65
