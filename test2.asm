; Simple test program which loads a value in A, and then moves it to X
; Initial P, A and X register values at memory locations 0, 1, and 2
.data 0, 0, 0

    loada 42
    output
    a2x
    not
    a2p
    lshift
    output
    rshift
    output
    x2a
    halt
    
