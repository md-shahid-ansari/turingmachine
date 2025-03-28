; Simple test program
; Initial P, A and X register values at memory locations 0, 1, and 2
.data 0, 0, 120

    ; test write (output w)
    loada test1
    a2p
    loada 119
    write
    loada test1
    a2p
    read
    output
    halt

test1:
    .data 114
