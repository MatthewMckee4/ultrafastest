#ifndef __APPLE__
#error "ultrafastest currently requires Apple Silicon"
#endif

    .text
    .p2align 2
    .globl _start

_start:
    mov x0, #1
    adr x1, payload
    mov x2, #PAYLOAD_SIZE
    mov x16, #4
    svc #0x80

    mov x0, #1
    mov x16, #1
    svc #0x80

payload:
    .incbin "src/payload.bin"
