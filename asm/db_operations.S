.global check_rowcount
.global choose_field

# func 1
check_rowcount:
    cmpq $0, %rcx
    jg positive

    movq $0, %rax
    ret

positive:
    movq $1, %rax
    ret

# func 2
choose_field:
    cmpq $0, %rcx
    je use_country

    movq $1, %rax   # id
    ret

use_country:
    movq $0, %rax   # country
    ret