#ifndef __APPLE__
#error "ultrafastest currently requires Apple Silicon"
#endif

    .text
    .p2align 2
    .globl _start

_start:
    mov x0, #1
    adrp x1, payload@PAGE
    add x1, x1, payload@PAGEOFF
    adrp x2, payload_end@PAGE
    add x2, x2, payload_end@PAGEOFF
    sub x2, x2, x1
    mov x16, #4
    svc #0x80

    mov x0, #1
    mov x16, #1
    svc #0x80

    .section __TEXT,__const
payload:
    .incbin "src/payload.bin"
payload_end:
