; Hello World program
; Initial P, A and X register values at memory locations 0, 1, and 2
.data 0, 0, 0

    loada start
    a2p
    loada 0
    jumpz

end:
    halt

start:
    loada 42
    output
    loada end
    a2p
    loada 0
    jumpz