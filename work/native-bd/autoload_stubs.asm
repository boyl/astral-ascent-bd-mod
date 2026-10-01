EXTERN resolveVersion:PROC
.code
bdForward0 PROC
 push rcx
 push rdx
 push r8
 push r9
 sub rsp,104
 movdqu xmmword ptr [rsp+32],xmm0
 movdqu xmmword ptr [rsp+48],xmm1
 movdqu xmmword ptr [rsp+64],xmm2
 movdqu xmmword ptr [rsp+80],xmm3
 mov ecx,0
 call resolveVersion
 movdqu xmm0,xmmword ptr [rsp+32]
 movdqu xmm1,xmmword ptr [rsp+48]
 movdqu xmm2,xmmword ptr [rsp+64]
 movdqu xmm3,xmmword ptr [rsp+80]
 add rsp,104
 pop r9
 pop r8
 pop rdx
 pop rcx
 jmp rax
bdForward0 ENDP
bdForward1 PROC
 push rcx
 push rdx
 push r8
 push r9
 sub rsp,104
 movdqu xmmword ptr [rsp+32],xmm0
 movdqu xmmword ptr [rsp+48],xmm1
 movdqu xmmword ptr [rsp+64],xmm2
 movdqu xmmword ptr [rsp+80],xmm3
 mov ecx,1
 call resolveVersion
 movdqu xmm0,xmmword ptr [rsp+32]
 movdqu xmm1,xmmword ptr [rsp+48]
 movdqu xmm2,xmmword ptr [rsp+64]
 movdqu xmm3,xmmword ptr [rsp+80]
 add rsp,104
 pop r9
 pop r8
 pop rdx
 pop rcx
 jmp rax
bdForward1 ENDP
bdForward2 PROC
 push rcx
 push rdx
 push r8
 push r9
 sub rsp,104
 movdqu xmmword ptr [rsp+32],xmm0
 movdqu xmmword ptr [rsp+48],xmm1
 movdqu xmmword ptr [rsp+64],xmm2
 movdqu xmmword ptr [rsp+80],xmm3
 mov ecx,2
 call resolveVersion
 movdqu xmm0,xmmword ptr [rsp+32]
 movdqu xmm1,xmmword ptr [rsp+48]
 movdqu xmm2,xmmword ptr [rsp+64]
 movdqu xmm3,xmmword ptr [rsp+80]
 add rsp,104
 pop r9
 pop r8
 pop rdx
 pop rcx
 jmp rax
bdForward2 ENDP
bdForward3 PROC
 push rcx
 push rdx
 push r8
 push r9
 sub rsp,104
 movdqu xmmword ptr [rsp+32],xmm0
 movdqu xmmword ptr [rsp+48],xmm1
 movdqu xmmword ptr [rsp+64],xmm2
 movdqu xmmword ptr [rsp+80],xmm3
 mov ecx,3
 call resolveVersion
 movdqu xmm0,xmmword ptr [rsp+32]
 movdqu xmm1,xmmword ptr [rsp+48]
 movdqu xmm2,xmmword ptr [rsp+64]
 movdqu xmm3,xmmword ptr [rsp+80]
 add rsp,104
 pop r9
 pop r8
 pop rdx
 pop rcx
 jmp rax
bdForward3 ENDP
bdForward4 PROC
 push rcx
 push rdx
 push r8
 push r9
 sub rsp,104
 movdqu xmmword ptr [rsp+32],xmm0
 movdqu xmmword ptr [rsp+48],xmm1
 movdqu xmmword ptr [rsp+64],xmm2
 movdqu xmmword ptr [rsp+80],xmm3
 mov ecx,4
 call resolveVersion
 movdqu xmm0,xmmword ptr [rsp+32]
 movdqu xmm1,xmmword ptr [rsp+48]
 movdqu xmm2,xmmword ptr [rsp+64]
 movdqu xmm3,xmmword ptr [rsp+80]
 add rsp,104
 pop r9
 pop r8
 pop rdx
 pop rcx
 jmp rax
bdForward4 ENDP
bdForward5 PROC
 push rcx
 push rdx
 push r8
 push r9
 sub rsp,104
 movdqu xmmword ptr [rsp+32],xmm0
 movdqu xmmword ptr [rsp+48],xmm1
 movdqu xmmword ptr [rsp+64],xmm2
 movdqu xmmword ptr [rsp+80],xmm3
 mov ecx,5
 call resolveVersion
 movdqu xmm0,xmmword ptr [rsp+32]
 movdqu xmm1,xmmword ptr [rsp+48]
 movdqu xmm2,xmmword ptr [rsp+64]
 movdqu xmm3,xmmword ptr [rsp+80]
 add rsp,104
 pop r9
 pop r8
 pop rdx
 pop rcx
 jmp rax
bdForward5 ENDP
bdForward6 PROC
 push rcx
 push rdx
 push r8
 push r9
 sub rsp,104
 movdqu xmmword ptr [rsp+32],xmm0
 movdqu xmmword ptr [rsp+48],xmm1
 movdqu xmmword ptr [rsp+64],xmm2
 movdqu xmmword ptr [rsp+80],xmm3
 mov ecx,6
 call resolveVersion
 movdqu xmm0,xmmword ptr [rsp+32]
 movdqu xmm1,xmmword ptr [rsp+48]
 movdqu xmm2,xmmword ptr [rsp+64]
 movdqu xmm3,xmmword ptr [rsp+80]
 add rsp,104
 pop r9
 pop r8
 pop rdx
 pop rcx
 jmp rax
bdForward6 ENDP
bdForward7 PROC
 push rcx
 push rdx
 push r8
 push r9
 sub rsp,104
 movdqu xmmword ptr [rsp+32],xmm0
 movdqu xmmword ptr [rsp+48],xmm1
 movdqu xmmword ptr [rsp+64],xmm2
 movdqu xmmword ptr [rsp+80],xmm3
 mov ecx,7
 call resolveVersion
 movdqu xmm0,xmmword ptr [rsp+32]
 movdqu xmm1,xmmword ptr [rsp+48]
 movdqu xmm2,xmmword ptr [rsp+64]
 movdqu xmm3,xmmword ptr [rsp+80]
 add rsp,104
 pop r9
 pop r8
 pop rdx
 pop rcx
 jmp rax
bdForward7 ENDP
bdForward8 PROC
 push rcx
 push rdx
 push r8
 push r9
 sub rsp,104
 movdqu xmmword ptr [rsp+32],xmm0
 movdqu xmmword ptr [rsp+48],xmm1
 movdqu xmmword ptr [rsp+64],xmm2
 movdqu xmmword ptr [rsp+80],xmm3
 mov ecx,8
 call resolveVersion
 movdqu xmm0,xmmword ptr [rsp+32]
 movdqu xmm1,xmmword ptr [rsp+48]
 movdqu xmm2,xmmword ptr [rsp+64]
 movdqu xmm3,xmmword ptr [rsp+80]
 add rsp,104
 pop r9
 pop r8
 pop rdx
 pop rcx
 jmp rax
bdForward8 ENDP
bdForward9 PROC
 push rcx
 push rdx
 push r8
 push r9
 sub rsp,104
 movdqu xmmword ptr [rsp+32],xmm0
 movdqu xmmword ptr [rsp+48],xmm1
 movdqu xmmword ptr [rsp+64],xmm2
 movdqu xmmword ptr [rsp+80],xmm3
 mov ecx,9
 call resolveVersion
 movdqu xmm0,xmmword ptr [rsp+32]
 movdqu xmm1,xmmword ptr [rsp+48]
 movdqu xmm2,xmmword ptr [rsp+64]
 movdqu xmm3,xmmword ptr [rsp+80]
 add rsp,104
 pop r9
 pop r8
 pop rdx
 pop rcx
 jmp rax
bdForward9 ENDP
bdForward10 PROC
 push rcx
 push rdx
 push r8
 push r9
 sub rsp,104
 movdqu xmmword ptr [rsp+32],xmm0
 movdqu xmmword ptr [rsp+48],xmm1
 movdqu xmmword ptr [rsp+64],xmm2
 movdqu xmmword ptr [rsp+80],xmm3
 mov ecx,10
 call resolveVersion
 movdqu xmm0,xmmword ptr [rsp+32]
 movdqu xmm1,xmmword ptr [rsp+48]
 movdqu xmm2,xmmword ptr [rsp+64]
 movdqu xmm3,xmmword ptr [rsp+80]
 add rsp,104
 pop r9
 pop r8
 pop rdx
 pop rcx
 jmp rax
bdForward10 ENDP
bdForward11 PROC
 push rcx
 push rdx
 push r8
 push r9
 sub rsp,104
 movdqu xmmword ptr [rsp+32],xmm0
 movdqu xmmword ptr [rsp+48],xmm1
 movdqu xmmword ptr [rsp+64],xmm2
 movdqu xmmword ptr [rsp+80],xmm3
 mov ecx,11
 call resolveVersion
 movdqu xmm0,xmmword ptr [rsp+32]
 movdqu xmm1,xmmword ptr [rsp+48]
 movdqu xmm2,xmmword ptr [rsp+64]
 movdqu xmm3,xmmword ptr [rsp+80]
 add rsp,104
 pop r9
 pop r8
 pop rdx
 pop rcx
 jmp rax
bdForward11 ENDP
bdForward12 PROC
 push rcx
 push rdx
 push r8
 push r9
 sub rsp,104
 movdqu xmmword ptr [rsp+32],xmm0
 movdqu xmmword ptr [rsp+48],xmm1
 movdqu xmmword ptr [rsp+64],xmm2
 movdqu xmmword ptr [rsp+80],xmm3
 mov ecx,12
 call resolveVersion
 movdqu xmm0,xmmword ptr [rsp+32]
 movdqu xmm1,xmmword ptr [rsp+48]
 movdqu xmm2,xmmword ptr [rsp+64]
 movdqu xmm3,xmmword ptr [rsp+80]
 add rsp,104
 pop r9
 pop r8
 pop rdx
 pop rcx
 jmp rax
bdForward12 ENDP
bdForward13 PROC
 push rcx
 push rdx
 push r8
 push r9
 sub rsp,104
 movdqu xmmword ptr [rsp+32],xmm0
 movdqu xmmword ptr [rsp+48],xmm1
 movdqu xmmword ptr [rsp+64],xmm2
 movdqu xmmword ptr [rsp+80],xmm3
 mov ecx,13
 call resolveVersion
 movdqu xmm0,xmmword ptr [rsp+32]
 movdqu xmm1,xmmword ptr [rsp+48]
 movdqu xmm2,xmmword ptr [rsp+64]
 movdqu xmm3,xmmword ptr [rsp+80]
 add rsp,104
 pop r9
 pop r8
 pop rdx
 pop rcx
 jmp rax
bdForward13 ENDP
bdForward14 PROC
 push rcx
 push rdx
 push r8
 push r9
 sub rsp,104
 movdqu xmmword ptr [rsp+32],xmm0
 movdqu xmmword ptr [rsp+48],xmm1
 movdqu xmmword ptr [rsp+64],xmm2
 movdqu xmmword ptr [rsp+80],xmm3
 mov ecx,14
 call resolveVersion
 movdqu xmm0,xmmword ptr [rsp+32]
 movdqu xmm1,xmmword ptr [rsp+48]
 movdqu xmm2,xmmword ptr [rsp+64]
 movdqu xmm3,xmmword ptr [rsp+80]
 add rsp,104
 pop r9
 pop r8
 pop rdx
 pop rcx
 jmp rax
bdForward14 ENDP
bdForward15 PROC
 push rcx
 push rdx
 push r8
 push r9
 sub rsp,104
 movdqu xmmword ptr [rsp+32],xmm0
 movdqu xmmword ptr [rsp+48],xmm1
 movdqu xmmword ptr [rsp+64],xmm2
 movdqu xmmword ptr [rsp+80],xmm3
 mov ecx,15
 call resolveVersion
 movdqu xmm0,xmmword ptr [rsp+32]
 movdqu xmm1,xmmword ptr [rsp+48]
 movdqu xmm2,xmmword ptr [rsp+64]
 movdqu xmm3,xmmword ptr [rsp+80]
 add rsp,104
 pop r9
 pop r8
 pop rdx
 pop rcx
 jmp rax
bdForward15 ENDP
bdForward16 PROC
 push rcx
 push rdx
 push r8
 push r9
 sub rsp,104
 movdqu xmmword ptr [rsp+32],xmm0
 movdqu xmmword ptr [rsp+48],xmm1
 movdqu xmmword ptr [rsp+64],xmm2
 movdqu xmmword ptr [rsp+80],xmm3
 mov ecx,16
 call resolveVersion
 movdqu xmm0,xmmword ptr [rsp+32]
 movdqu xmm1,xmmword ptr [rsp+48]
 movdqu xmm2,xmmword ptr [rsp+64]
 movdqu xmm3,xmmword ptr [rsp+80]
 add rsp,104
 pop r9
 pop r8
 pop rdx
 pop rcx
 jmp rax
bdForward16 ENDP
END
