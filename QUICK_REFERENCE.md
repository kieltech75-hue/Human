# Human Language - Quick Reference Card

## Running Programs

```bash
python interpreter.py program.hm          # Run a program
python interpreter.py --repl              # Interactive mode
```

## Variables

```
set x to 10
set name to "Alice"
set flag to true
```

## Basic Output

```
print "Hello, World!"
print x
print "Value: " + x
print a + b + c
```

## Arithmetic

```
set sum to 10 + 5
set diff to 10 - 3
set prod to 4 * 5
set quot to 20 / 4
set remain to 10 % 3
```

## Comparisons

```
if x is equal to 5 then
if x is greater than 10 then
if x is less than 20 then
```

## Logical Operators

```
if x is greater than 5 and y is less than 10 then
if x is 5 or x is 10 then
if not x is equal to 0 then
```

## Conditionals

```
if condition then
    -- code here
end if

if condition then
    -- if block
else
    -- else block
end if

if cond1 then
    if cond2 then
        -- nested
    end if
end if
```

## Loops (Inclusive)

```
loop from 1 to 10 do
    print "Iteration"
end loop

loop from 1 to 5 do
    set square to i * i
    print square
end loop
```

## Functions

```
-- Define a function
define add with a, b
    return a + b
end define

-- Call a function
set result to add(10, 20)

define greet with name
    print "Hello, " + name + "!"
end define

greet "Alice"
```

## Comments

```
-- This is a comment
-- Comments start with two dashes

set x to 5  -- inline comment
```

## Common Patterns

### Sum of Numbers
```
set sum to 0
loop from 1 to 10 do
    set sum to sum + i
end loop
print sum
```

### Check Even/Odd
```
if n % 2 is equal to 0 then
    print "Even"
else
    print "Odd"
end if
```

### Grade Assignment
```
if score is greater than 90 then
    set grade to "A"
else
    if score is greater than 80 then
        set grade to "B"
    else
        set grade to "C"
    end if
end if
```

### Factorial
```
set n to 5
set fact to 1
loop from 1 to n do
    set fact to fact * i
end loop
print fact
```

### Counting with Step
```
set count to 0
loop from 1 to 10 do
    set count to count + 1
    print count
end loop
```

## String Operations

```
-- String concatenation
set greeting to "Hello" + " " + "World"

-- Number to string
set msg to "Answer: " + 42

-- Multiple parts
print "x=" + x + ", y=" + y
```

## Data Types

| Type | Example | Usage |
|------|---------|-------|
| Number | `42`, `3.14` | Arithmetic, comparisons |
| String | `"text"`, `'text'` | Output, concatenation |
| Boolean | `true`, `false` | Conditions |

## Keywords (33)

`set` `to` `if` `then` `else` `end` `loop` `from` `do` `define` `with` `return` `print` `ask` `class` `new` `this` `true` `false` `and` `or` `not` `is` `greater` `less` `equal` `than`

## Operators

| Type | Symbols |
|------|---------|
| Arithmetic | `+` `-` `*` `/` `%` |
| Comparison | `is greater than`, `is less than`, `is equal to` |
| Logical | `and` `or` `not` |
| String | `+` (concatenation) |

## Tips & Tricks

1. **Meaningful names**: Use `student_score` not `s`
2. **Clear logic**: Break complex conditions into parts
3. **Indent properly**: Makes code readable
4. **Test early**: Run your code frequently
5. **Comments help**: Explain why, not what

## Error Messages

| Error | Cause | Fix |
|-------|-------|-----|
| `Unexpected token` | Syntax error | Check keywords and spelling |
| `Expected THEN` | Missing `then` after condition | Add `then` after `if ...` |
| `Expected END` | Unmatched block start | Add matching `end` keyword |
| `Undefined variable` | Using undefined variable | Use `set` to create it first |
| `Runtime error` | Division by zero | Check for zero divisor |

## File Extension

Use `.hm` for all Human language files:
- `hello.hm`
- `program.hm`
- `calculate.hm`

## Example Programs

### Hello World
```
print "Hello, World!"
```

### Add Two Numbers
```
set a to 10
set b to 20
print a + b
```

### Simple Loop
```
loop from 1 to 5 do
    print "Iteration"
end loop
```

### If Statement
```
set age to 25
if age is greater than 18 then
    print "Adult"
end if
```

### Function
```
define multiply with x, y
    return x * y
end define

print multiply(4, 5)
```

## Resources

- **README.md** - Project overview
- **QUICKSTART.md** - Get started quickly
- **SYNTAX.md** - Complete syntax reference
- **DEVELOPMENT.md** - How to extend the language
- **examples/** - Working example programs

## Keyboard Shortcuts (REPL)

- `Ctrl+C` - Exit REPL
- `Up/Down` - Scroll through history (depends on terminal)

## Common Mistakes

```
-- ❌ Wrong (missing colon or operator)
if x > 5
    print "yes"

-- ✅ Right
if x is greater than 5 then
    print "yes"
end if

-- ❌ Wrong (not a keyword)
var x = 10

-- ✅ Right
set x to 10

-- ❌ Wrong (requires then)
if condition
    print "yes"
end if

-- ✅ Right
if condition then
    print "yes"
end if
```

## String Gotchas

```
-- ✅ Works (concatenation with +)
print "Answer: " + 42

-- ❌ Doesn't work (wrong operator)
print "Answer: " . 42

-- ✅ Works (multiple arguments)
print "x is" x

-- ✅ Works (explicit concatenation)
print "x is " + x
```

---

**Created for the Human Programming Language**
A plain English programming language with `.hm` file extension
