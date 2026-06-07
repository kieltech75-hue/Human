# Human Language - Development Guide

## Architecture Overview

The Human language interpreter is built with a classic multi-stage compiler architecture:

```
Source Code (.hm file)
        ↓
    LEXER (lexer.py)
        ↓
    Tokens
        ↓
    PARSER (parser.py)
        ↓
    Abstract Syntax Tree (ast_nodes.py)
        ↓
    COMPILER (compiler.py)
        ↓
    Bytecode + Constants
        ↓
    VM (vm.py)
        ↓
    Execution / Output
```

## File Structure

### Core Components

- **`lexer.py`** - Tokenizes source code
  - `TokenType`: Enum of all token types
  - `Token`: Individual token with type, value, line, column
  - `Lexer`: Main lexer class

- **`ast_nodes.py`** - AST node definitions
  - Base `ASTNode` class
  - Node types for all language constructs
  - Immutable dataclasses for each node type

- **`parser.py`** - Parses tokens into AST
  - `Parser`: Recursive descent parser
  - Operator precedence handling
  - Error reporting with line/column info

- **`compiler.py`** - Compiles AST to bytecode
  - `Opcode`: Enum of all bytecode operations
  - `Bytecode`: Container for instructions and constants
  - `Compiler`: Walks AST and emits bytecode

- **`vm.py`** - Virtual machine for executing bytecode
  - `VM`: Stack-based VM implementation
  - Instruction execution
  - Variable storage

- **`interpreter.py`** - Main entry point
  - File loading and execution
  - REPL mode
  - Error handling and reporting

## Adding New Features

### 1. Add a New Keyword

**Step 1: Update the lexer**
```python
# In lexer.py, TokenType enum:
MYFEATURE = auto()

# In lexer.py, get_keyword_type():
'myfeature': TokenType.MYFEATURE,
```

**Step 2: Update the parser**
```python
# In parser.py, add a parse method:
def parse_myfeature(self):
    self.expect(TokenType.MYFEATURE)
    # ... parsing logic
    return MyFeatureNode(...)

# In parser.py, parse_statement():
elif token.type == TokenType.MYFEATURE:
    return self.parse_myfeature()
```

**Step 3: Update AST nodes**
```python
# In ast_nodes.py:
@dataclass
class MyFeatureNode(ASTNode):
    # ... fields
    pass
```

**Step 4: Update the compiler**
```python
# In compiler.py, compile_statement():
elif isinstance(node, MyFeatureNode):
    self.compile_myfeature(node)

def compile_myfeature(self, node: MyFeatureNode):
    # ... emit bytecode
    pass
```

**Step 5: Update the VM (if needed)**
```python
# In compiler.py, Opcode enum (if needed):
MYFEATURE_OP = auto()

# In vm.py:
elif opcode == Opcode.MYFEATURE_OP:
    # ... execution logic
    pass
```

### 2. Add a New Operator

Example: Adding a power operator `**`

**Step 1: Lexer**
```python
# TokenType:
POWER = auto()

# Tokenize method (in tokenize loop):
elif char == '*' and self.peek(1) == '*':
    self.advance()
    self.advance()
    self.tokens.append(Token(TokenType.POWER, '**', line, column))
```

**Step 2: Parser**
```python
# Add parse_power method with right precedence
def parse_power(self) -> ASTNode:
    left = self.parse_unary()
    while self.current_token().type == TokenType.POWER:
        op = '**'
        self.advance()
        right = self.parse_power()  # Right associative
        left = BinaryOp(left, op, right)
    return left

# Update parse_multiplicative to call parse_power instead of parse_unary
```

**Step 3: Compiler**
```python
# In compile_expression, BinaryOp case:
elif node.operator == '**':
    self.bytecode.emit(Opcode.POW)
```

**Step 4: VM**
```python
# In Opcode enum:
POW = auto()

# In VM execute method:
elif opcode == Opcode.POW:
    b = self.stack.pop()
    a = self.stack.pop()
    self.stack.append(a ** b)
```

## Testing

To test changes:

```bash
# Create a test file: test_feature.hm
# Run the interpreter
human test_feature.hm

# Or use REPL
human --repl
```

## Common Issues and Solutions

### Issue: Parser hangs or infinite loop
- Check that all loops have exit conditions
- Verify that all blocks (`if`, `loop`, `define`) have matching `end` keywords

### Issue: Variable is undefined
- Check that variable is assigned before use with `set`
- Remember variable names are case-sensitive

### Issue: Type errors in VM
- Ensure operators are used with compatible types
- Check string concatenation uses `+` operator

### Issue: Bytecode doesn't execute
- Check that `compiler.compile()` returns bytecode
- Verify `HALT` opcode is emitted at end
- Check that `VM.execute()` is called

## Performance Considerations

1. **Bytecode Compilation**: AST is compiled to bytecode once, then executed multiple times
2. **Variable Storage**: Variables are stored in a dictionary in the VM
3. **Loop Optimization**: Loops use labels and jumps rather than function calls
4. **String Operations**: String concatenation creates new strings (consider caching in future)

## Future Enhancements

### Language Features
- [ ] Arrays and lists
- [ ] Dictionaries/maps
- [ ] Classes and objects (partially in AST)
- [ ] Exception handling (try/catch)
- [ ] Import/module system
- [ ] Lambda functions
- [ ] List comprehensions
- [ ] Generators
- [ ] Context managers

### Implementation
- [ ] Function call stack (for recursion)
- [ ] Better error messages with stack traces
- [ ] Optimization passes (dead code elimination, constant folding)
- [ ] Just-in-time compilation
- [ ] Interactive debugger
- [ ] Type checking system

### Tooling
- [ ] VS Code extension with syntax highlighting
- [ ] Linter for style checking
- [ ] Code formatter
- [ ] Documentation generator
- [ ] Package manager
- [ ] Standard library

## Code Style

- Follow PEP 8 for Python
- Use type hints for function parameters and returns
- Write docstrings for public classes and methods
- Keep functions focused and concise
- Use meaningful variable names

## Contributing

1. Test your changes with existing examples
2. Create new test files for new features
3. Update documentation (README, SYNTAX, QUICKSTART)
4. Follow the architecture outlined above
5. Maintain backward compatibility when possible

## Debugging Tips

### Enable debug output
Add print statements in:
- `Lexer.tokenize()` to see tokens
- `Parser.parse_*()` to see AST nodes
- `Compiler.compile_*()` to see bytecode
- `VM.execute()` to see stack state

### Inspect bytecode
```python
# In interpreter.py, after compiling:
print(f"Instructions: {bytecode.instructions}")
print(f"Constants: {bytecode.constants}")
```

### Step through execution
Add debug output in `vm.py`:
```python
print(f"PC: {self.pc}, Opcode: {opcode}, Stack: {self.stack}")
```

## References

- **Lexer**: Token-based scanning
- **Parser**: Recursive descent with operator precedence
- **AST**: Tree representation of program structure
- **Compiler**: Bytecode emission
- **VM**: Stack-based execution model

## Questions or Issues?

See README.md and SYNTAX.md for more information about the language.
