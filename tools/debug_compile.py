from human_language.lexer import Lexer
from human_language.parser import Parser
from human_language.compiler import Compiler

fname = 'examples/import_test.hm'
with open(fname, 'r', encoding='utf-8') as f:
    s = f.read()

print('---SOURCE---')
print(s)

print('---TOKENS---')
print([(t.type.name, t.value) for t in Lexer(s).tokenize()])

print('---AST---')
ast = Parser(Lexer(s).tokenize()).parse()
print(ast)

print('---BYTECODE---')
bc = Compiler().compile(ast)
print('instrs:')
for i,(op,arg) in enumerate(bc.instructions):
    print(i, op, arg)
print('consts:', bc.constants)
print('functions:', list(bc.functions.keys()))
