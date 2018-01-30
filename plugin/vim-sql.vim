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

if !has("python3") == 1
    echo "Python 3 support is required. You can test this in Vim by calling ':has(\"Python3\")'"
endif

" Root path to this file:
let g:vim_sql_script_path = expand('<sfile>:p:h')

if has("win32")
    let g:vim_sql_script_path = g:vim_sql_script_path. "\\vim-sql\\"
else
    let g:vim_sql_script_path = g:vim_sql_script_path. "/vim-sql/"
endif

" Set import path to include plugin directory.
py3 << py3eof
# import os
import sys
import vim

# # Add Vim script path to module path so we can actually load:
VIM_SQL_SCRIPT_PATH = vim.eval("g:vim_sql_script_path")

if VIM_SQL_SCRIPT_PATH not in sys.path:
    sys.path += [VIM_SQL_SCRIPT_PATH]

# vim.command("let g:vim_sql_script_path="+VIM_SQL_SCRIPT_PATH)
py3eof

" let g:vim_sql_script_path = g:vim_sql_script_path. "\\vim-sql\\"

if has("win32")
    exec "py3file ". g:vim_sql_script_path. "\\vim-sql.py"
else
    exec "py3file ". g:vim_sql_script_path. "/vim-sql.py"
endif

" Add commands we can keybind, to make life easier:
command! -range VimSqlServers py3 vimsql.show_database_list() 
command! -range VimSqlExecuteBuffer py3 vimsql.execute_buffer() 
map <leader>wq :VimSqlServer<cr>
map <leader>ww :VimSqlExecuteBuffer<cr>

so ~/.config/nvim/secrets.vim
