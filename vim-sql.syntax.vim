" Syntax highlighting for Database list buffer. NOT loaded from this file;
" stored in array in function vimsql.show_dblist_window().
syntax match DBName /^\* \zs.*\ze$/
syntax match SchemaName /- \[\zs[^\.\]]*\ze]/
syntax match TableName /\.\[\zs[^\]]*\ze\]$/
syntax match SqlType /(\zs.*\ze)/
syntax match ColumnName /> \zs\w*\ze/

highlight def link DBName Statement
highlight def link SchemaName Constant
highlight def link TableName Constant
highlight def link ColumnName Type
highlight def link SqlType Comment


