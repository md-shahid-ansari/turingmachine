; Simple test program which loads a value in A, and then perform basic operations
; Initial P, A and X register values at memory locations 0, 1, and 2
.data 0, 0, 0

    loada 0
    a2p
    loada 152
    output
    write
    loada 15
    a2p
    loada 0
    output
    jumpz ; test jump also by modifying previous loada 0
    or ; try and, add here
    output
    halt