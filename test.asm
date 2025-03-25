; Hello World program
; Initial P, A and X register values at memory locations 0, 1, and 2
.data 0, 0, 0

; Initialize counter
    loada counter        ; Load address of counter
    a2p                  ; Move to pointer register
    loada string_data    ; Load address of the string data
    write                ; Store string address in counter location

; Main loop to print characters
start:
    loada counter    ; Load address of counter
    a2p              ; Move to pointer register
    read             ; Read the current string pointer
    a2p              ; Move the string pointer to pointer register
    read             ; Read the character at that location
    a2x              ; Move character to X register

    ; Check if character is null (end of string)
    loada end        ; Load end address
    a2p              ; Move to pointer register
    x2a              ; Move character back to A for comparison
    jumpz            ; If character is 0, jump to end

    ; Print the character
    x2a              ; Get character back to A
    output           ; Output the character

    ; Increment string pointer
    loada counter    ; Load address of counter
    a2p              ; Move to pointer register
    read             ; Read the current string pointer
    a2x              ; Move pointer to X
    loada 1          ; Load 1 to A
    add              ; Add 1 to pointer
    a2x              ; Move incremented pointer to X
    loada counter    ; Load counter address again
    a2p              ; Move to pointer register
    x2a              ; Move incremented pointer to A
    write            ; Update the counter with new pointer

    ; Jump back to start of loop
    loada start      ; Load the address of the start label
    a2p              ; Move to pointer register
    jump             ; Jump back to start of loop

end:
    halt             ; Stop execution

; Data section
counter:
    .data 0          ; Storage for string pointer
string_data:
    .data "Hello, World!", 0  ; Null-terminated string