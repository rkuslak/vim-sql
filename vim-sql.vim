"
"
"

let s:debug = 1
let s:script_path = expand('<sfile>:p:h')
let g:plugin_path = expand('<sfile>:p:h')

function! s:VimSqlInit()
    " Do 1-time initialization functions in Vim to sanitize enviroment
    if(!exists("g:VimSqlInitialized") || s:debug != 1)
        " Add module directory to python module paths:
        python3 << endpython
import sys
import vim

sys.path.append(vim.eval("g:plugin_path"))
endpython
        exec "py3 import os"
        exec "py3file ". s:script_path. "\\__init__.py"
        " let g:VimSqlInitialized = 1
    endif
endfunction

function! VimSqlShowServers()
    call s:VimSqlInit()
    let current_buff = bufnr("%")
    " let buffer_name = 'Servers: '
    let buffer_name = bufname(current_buff)
    let server_buffer = getbufvar(current_buff, "vimsqlserverlist")
    let server_buffer_name = "Database: ". buffer_name
    echo current_buff
    echo buffer_name
    echo server_buffer_name
    exec ":b ". current_buff
endfunction

command! VimSqlServers exec VimSqlShowServers()
