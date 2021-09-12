	.text
	.globl main
main: 	                                                           
	addi	sp,sp,-16
	sd	ra,8(sp)
## TODO Your assembly code there
	
## END TODO /end of user assembly code
	ld	ra,8(sp)
	addi	sp,sp,16
	jr	ra
	ret

# Data comes here
	.section	.data
mydata:
	.dword 7
