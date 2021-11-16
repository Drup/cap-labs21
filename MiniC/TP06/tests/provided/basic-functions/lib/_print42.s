	.text
	.globl print_42
print_42:
	addi sp, sp, -16
        sd ra, 0(sp)
        sd fp, 8(sp)
        addi fp, sp, 16

	li a0, 42
	call print_int
	call newline
	
	ld ra, 0(sp)
	addi sp, sp, 16
	ret
