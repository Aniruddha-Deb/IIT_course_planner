%%

\s+           /* skip whitespace */
[a-zA-Z0-9]+   return 'TERM';
"&&"             return 'AND';
"||"             return 'OR';
"("              return 'LBRACKET';
")"              return 'RBRACKET';
"["              return 'START';
"]"              return 'END';

%%
