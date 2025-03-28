; Simple test program
; Initial P, A and X register values at memory locations 0, 1, and 2
.data 0, 0, 120

    ; test loada (outputs l)
    loada 108
    output

    ; test x2a (X value from initial initialization, outputs x)
    x2a
    output

    ; test a2x (outputs a)
    loada 97
    a2x
    loada 0
    x2a
    output

    ; test lshift (outputs <)
    loada 30
    lshift
    output

    ; test rshift (outputs >)
    loada 124
    rshift
    output

    ; test not (outputs n)
    loada 145
    not
    output

    ; test a2p and read (outputs r)
    loada test1
    a2p
    read
    output

    ; test add (outputs d)
    loada 42
    a2x
    loada 58
    add
    output

    ; test or (outputs e)
    loada 65
    a2x
    loada 100
    or
    output

    ; test and (outputs f)
    loada 102
    a2x
    loada 110
    and
    output

    ; test write (output w)
    loada test1
    a2p
    loada 119
    write
    loada test1
    a2p
    read
    output

    ; jump and jumpz (output j),
    loada test2
    a2p
    loada 0
    jumpz
    loada 106
    output
test2:

    ; test halt, no output
    halt

test1:
    .data 114
