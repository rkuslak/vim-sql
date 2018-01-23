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

" Set import path to include plugin directory.
py3 << py3eof
import os
import sys
import vim

# Add Vim script path to module path so we can actually load:
VIM_SQL_SCRIPT_PATH = os.path.join(vim.eval("g:vim_sql_script_path"),
                                   'vim-sql')
print(VIM_SQL_SCRIPT_PATH)
if VIM_SQL_SCRIPT_PATH not in sys.path:
    sys.path += [VIM_SQL_SCRIPT_PATH]

# Update global Vim variable to point to entry script, as we can reasonably
# assume this will work cross-platform (and avoids any more VimScript than
# is absolutely need)
VIM_SQL_SCRIPT_PATH = os.path.join(VIM_SQL_SCRIPT_PATH, 'vim-sql.py')
cmd = 'let g:vim_sql_script_path="{}"'.format(VIM_SQL_SCRIPT_PATH)
vim.command(cmd)
py3eof


exec "py3file ". g:vim_sql_script_path

unlet g:vim_sql_script_path

" Add commands we can keybind, to make life easier:
command! -range VimSqlServers py3 vimsql.show_database_list() 
map <leader>wq :VimSqlServer<cr>
