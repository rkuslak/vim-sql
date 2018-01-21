"    Vim-SQL
"    Copyright 2018 Ron Kuslak, All Rights Reserved
"    Further license information including in the LICENSE file at the root of
"    this plugin.
"
"    Attempts to provide SQL Server browsing, symbol completion, and arbirary
"    query execution to Vim and NeoVIM via a plesant interface for limited
"    values of "plesant."
"
"    Some effort has been made to keep it a general and plugable as possible,
"    as eventual addition of other engines (such as Postgre or MariaDB) is a
"    long-term goal, after a first-class MS SQL experience is created.

" Root path to this file:
let g:vim_sql_script_path = expand('<sfile>:p:h')

function! s:VimSqlInit()
    " Do 1-time initialization functions in Vim to sanitize enviroment
    if !exists("g:VimSqlInitialized")
        py3 << py_eof
import sys
import vim

VIM_SQL_SCRIPT_PATH = vim.eval("g:vim_sql_script_path")
if not VIM_SQL_SCRIPT_PATH in sys.path:
    sys.path += [VIM_SQL_SCRIPT_PATH]

# TODO: Is this needed? Shouldn't need the consuming code to know of the DBs or
#   models?
py_eof
        py3file Z:\vim-sql\test.py
        " let g:VimSqlInitialized = 1
    endif
endfunction

call s:VimSqlInit()

function! s:VimSqlGetBuffer(buffertype)
    let calling_buff = bufnr("%")
    let calling_buff_name = bufname(calling_buff)
    
endfunction

function! VimSqlShowServers()
    " Display the server list for the currently active buffer via a vsplit
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

