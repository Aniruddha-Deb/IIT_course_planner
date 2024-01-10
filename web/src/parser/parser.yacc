%{

function And(a, b) {
    this.left = a;
    this.right = b;
}

function Or(a, b) {
    this.left = a;
    this.right = b;
}

%}

%left AND OR
%start deps

%%
deps: START expr END {return $2;}
    ;

expr: expr AND expr {$$ = new And($1, $3);}
    | expr OR expr {$$ = new Or($1, $3);}
    | LBRACKET expr RBRACKET {$$ = $2;}
    | TERM {$$ = yytext;}
    ;
