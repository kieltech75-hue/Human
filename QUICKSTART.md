# Human Language - Quick Start Guide

## Installation

1. Make sure you have Python 3.7 or higher installed
2. Navigate to the Human language directory
3. You're ready to go!

## Running Programs

### Run a .hm file
```bash
human program.hm
```

### Interactive REPL
```bash
human --repl
```

## Your First Program

Create a file named `hello.hm`:

```
print "Hello, World!"
```

Run it:
```bash
human hello.hm
```

## Example 1: Variables

Create `add.hm`:

```
set x to 10
set y to 20
set sum to x + y

print "Sum: " + sum
```

## Example 2: Conditionals

Create `age.hm`:

```
set age to 25

if age is greater than 18 then
    print "You are an adult"
else
    print "You are under 18"
end if
```

## Example 3: Loops

Create `count.hm`:

```
print "Counting from 1 to 5:"

loop from 1 to 5 do
    print "Number"
end loop
```

## Example 4: Functions

Create `greet.hm`:

```
define say_hello with name
    print "Hello, " + name + "!"
end define

say_hello "Alice"
say_hello "Bob"
```

## Common Patterns

### Check if a number is even
```
set num to 10

set remainder to num % 2
if remainder is equal to 0 then
    print "Even"
else
    print "Odd"
end if
```

### Simple calculator
```
set a to 15
set b to 7

print "Addition: " + (a + b)
print "Subtraction: " + (a - b)
print "Multiplication: " + (a * b)
print "Division: " + (a / b)
```

### Nested conditions
```
set temperature to 25

if temperature is greater than 30 then
    print "Too hot"
else
    if temperature is greater than 15 then
        print "Pleasant"
    else
        print "Too cold"
    end if
end if
```

## Tips

1. Use meaningful variable names: `set user_age to 25` instead of `set a to 25`
2. Use comments to explain your code: `-- This calculates the average`
3. Keep functions short and focused on one task
4. Test your programs frequently as you write them

## Troubleshooting

### "Unexpected token" error
- Check for typos in keywords
- Make sure all `if` statements have matching `end if`
- Make sure all `loop` statements have matching `end loop`

### Variables appear to be empty
- Make sure you used `set` to initialize the variable
- Check the variable name spelling

### String concatenation not working
- Use `+` to concatenate strings
- Make sure both sides are strings or can be converted to strings

## Next Steps

1. Read the full [SYNTAX.md](SYNTAX.md) guide for all features
2. Try the examples in the `examples/` directory
3. Start building your own programs!
4. Check the README for development notes

## Language Features Supported

-  Variables and assignments
-  Basic data types (numbers, strings, booleans)
-  Arithmetic operations
-  Comparison operators
-  Logical operators (and, or, not)
-  If/else conditionals
-  Loops (from/to)
-  Functions with parameters
-  Print output
-  Comments
-  User input (partially)
-  Arrays/lists
-  Classes and objects
-  Exception handling
-  Import/modules

## Getting Help

If you encounter issues:
1. Check the [SYNTAX.md](SYNTAX.md) file
2. Look at the examples in the `examples/` directory
3. Check error messages carefully - they often point to the problem

Happy coding with Human! 🎉
