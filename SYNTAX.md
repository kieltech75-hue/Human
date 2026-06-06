# Human Language Syntax Guide

## Overview
Human is a plain English programming language designed to be as readable as possible while maintaining programming power.

## Basic Syntax

### Comments
```
-- This is a comment
-- Comments start with two dashes
```

### Variables
```
set x to 10
set name to "Alice"
set result to true
```

### Printing Output
```
print "Hello, World!"
print x
print "The value is " + x

-- Multiple arguments (concatenated with spaces)
print "Hello" "World"
```

### Getting User Input
```
ask "What is your name?"
```

## Data Types

- **Numbers**: `42`, `3.14`
- **Strings**: `"Hello"`, `'World'`
- **Booleans**: `true`, `false`

## Operators

### Arithmetic
- Addition: `+`
- Subtraction: `-`
- Multiplication: `*`
- Division: `/`
- Modulo (remainder): `%`

Examples:
```
set sum to 10 + 5
set product to 3 * 4
set remainder to 10 % 3
```

### Comparison
```
-- All comparisons use "is"
if x is equal to 5 then
    -- do something
end if

if x is greater than 10 then
    -- do something
end if

if x is less than 20 then
    -- do something
end if
```

### Logical Operators
```
if x is greater than 5 and y is less than 10 then
    -- do something
end if

if x is 5 or x is 10 then
    -- do something
end if

if not x is equal to 0 then
    -- do something
end if
```

## Control Flow

### If Statements
```
if condition then
    -- code here runs if condition is true
else
    -- code here runs if condition is false
end if
```

Nested if statements:
```
if age is greater than 18 then
    if license is true then
        print "Can drive"
    else
        print "Need a license"
    end if
else
    print "Too young to drive"
end if
```

### Loops
```
loop from 1 to 10 do
    print "Iteration"
end loop
```

The loop variable goes from the start value to the end value (inclusive).

### Functions
```
define greet with name
    print "Hello, " + name + "!"
end define

greet "Alice"
```

Functions with multiple parameters:
```
define add_numbers with a, b
    return a + b
end define

set result to add_numbers(10, 20)
```

## String Operations

String concatenation uses `+`:
```
set greeting to "Hello, " + "World!"
print greeting
```

## Example Programs

### Simple Calculator
```
print "Simple Calculator"

set num1 to 10
set num2 to 5

set sum to num1 + num2
set product to num1 * num2

print "Sum: " + sum
print "Product: " + product
```

### Grade Checker
```
set score to 85

if score is greater than 90 then
    print "Grade: A"
else
    if score is greater than 80 then
        print "Grade: B"
    else
        if score is greater than 70 then
            print "Grade: C"
        else
            print "Grade: F"
        end if
    end if
end if
```

### Factorial Using Loop
```
set n to 5
set factorial to 1

loop from 1 to n do
    factorial is factorial * i
end loop

print "Factorial of 5 is: " + factorial
```

## Keywords Reference

| Keyword | Purpose |
|---------|---------|
| `set` | Declare/assign a variable |
| `to` | Used with `set` |
| `if` | Start a conditional block |
| `then` | Used with `if` |
| `else` | Alternative block for `if` |
| `end` | End a block (if, loop, define) |
| `loop` | Start a loop |
| `from` | Used with `loop` |
| `do` | Used with `loop` |
| `define` | Define a function |
| `with` | Used with `define` for parameters |
| `return` | Return from a function |
| `print` | Output to console |
| `ask` | Get user input |
| `true` | Boolean true |
| `false` | Boolean false |
| `and` | Logical AND |
| `or` | Logical OR |
| `not` | Logical NOT |
| `is` | Comparison operator |
| `greater` | Used with `is` for > |
| `less` | Used with `is` for < |
| `equal` | Used with `is` for == |

## Tips for Writing Clean Code

1. **Use meaningful variable names**
   ```
   -- Good
   set user_age to 25
   
   -- Bad
   set a to 25
   ```

2. **Use comments to explain logic**
   ```
   -- Calculate the average of two numbers
   set average to (a + b) / 2
   ```

3. **Properly indent nested blocks**
   ```
   if condition then
       loop from 1 to 10 do
           if inner_condition then
               print "Done"
           end if
       end loop
   end if
   ```

