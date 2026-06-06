# String Methods, List Methods, and New Builtin Functions

## String Methods

All strings have these methods available:

### `.upper()`
Convert string to uppercase
```
set text to "hello"
print text.upper()  -- HELLO
```

### `.lower()`
Convert string to lowercase
```
set text to "HELLO"
print text.lower()  -- hello
```

### `.split(separator)`
Split string into list
```
set text to "apple,banana,cherry"
set fruits to text.split(",")
print fruits  -- ["apple", "banana", "cherry"]
```

### `.replace(old, new)`
Replace all occurrences of substring
```
set text to "hello world"
set result to text.replace("world", "Human")
print result  -- hello Human
```

### `.strip()`
Remove leading and trailing whitespace
```
set text to "  hello  "
print text.strip()  -- hello
```

### `.startswith(prefix)`
Check if string starts with prefix
```
set text to "Hello World"
print text.startswith("Hello")  -- true
```

### `.endswith(suffix)`
Check if string ends with suffix
```
set text to "Hello World"
print text.endswith("World")  -- true
```

### `.find(substring)`
Find index of substring (-1 if not found)
```
set text to "hello world"
print text.find("world")  -- 6
```

### `.count(substring)`
Count occurrences of substring
```
set text to "hello"
print text.count("l")  -- 2
```

### `.join(list)`
Join list of strings with separator
```
set words to ["a", "b", "c"]
print "-".join(words)  -- a-b-c
```

### `.contains(substring)`
Check if string contains substring
```
set text to "hello world"
print text.contains("world")  -- true
```

---

## List Methods

All lists have these methods available:

### `.append(item)`
Add item to end of list
```
set items to [1, 2, 3]
items.append(4)
print items  -- [1, 2, 3, 4]
```

### `.pop()`
Remove and return last item
```
set items to [1, 2, 3, 4]
set last to items.pop()
print last   -- 4
print items  -- [1, 2, 3]
```

### `.extend(other_list)`
Add all items from another list
```
set items to [1, 2, 3]
items.extend([4, 5])
print items  -- [1, 2, 3, 4, 5]
```

### `.index(item)`
Find index of item
```
set items to [10, 20, 30]
print items.index(20)  -- 1
```

### `.count(item)`
Count occurrences of item
```
set items to [1, 2, 2, 3, 2]
print items.count(2)  -- 3
```

### `.reverse()`
Reverse list in place
```
set items to [1, 2, 3]
items.reverse()
print items  -- [3, 2, 1]
```

### `.clear()`
Remove all items from list
```
set items to [1, 2, 3]
items.clear()
print items  -- []
```

### `.insert(index, item)`
Insert item at specific position
```
set items to [1, 2, 3]
items.insert(1, 99)
print items  -- [1, 99, 2, 3]
```

---

## Dictionary Methods

All dictionaries have these methods available:

### `.keys()`
Get list of all keys
```
set person to {name: "Alice", age: 30}
print person.keys()  -- ["name", "age"]
```

### `.values()`
Get list of all values
```
set person to {name: "Alice", age: 30}
print person.values()  -- ["Alice", 30]
```

### `.items()`
Get list of [key, value] pairs
```
set person to {name: "Alice", age: 30}
print person.items()  -- [["name", "Alice"], ["age", 30]]
```

### `.get(key, default)`
Get value with optional default
```
set person to {name: "Alice"}
print person.get("name")        -- Alice
print person.get("age", 0)      -- 0
```

### `.pop(key, default)`
Remove and return value
```
set person to {name: "Alice", age: 30}
set age to person.pop("age")
print age     -- 30
print person  -- {name: "Alice"}
```

### `.clear()`
Remove all items
```
set person to {name: "Alice", age: 30}
person.clear()
print person  -- {}
```

### `.update(other_dict)`
Merge another dictionary
```
set person to {name: "Alice"}
person.update({age: 30, city: "NYC"})
print person  -- {name: "Alice", age: 30, city: "NYC"}
```

---

## New Builtin Functions

### `sorted(list)`
Return sorted copy of list
```
set nums to [3, 1, 4, 1, 5, 9]
print sorted(nums)  -- [1, 1, 3, 4, 5, 9]
```

### `min(list)` or `min(a, b, c, ...)`
Return minimum value
```
set nums to [3, 1, 4, 1, 5]
print min(nums)     -- 1
print min(5, 2, 8)  -- 2
```

### `max(list)` or `max(a, b, c, ...)`
Return maximum value
```
set nums to [3, 1, 4, 1, 5]
print max(nums)     -- 5
print max(5, 2, 8)  -- 8
```

### `sum(list)`
Sum all items in list
```
set nums to [1, 2, 3, 4, 5]
print sum(nums)  -- 15
```

### `enumerate(list)`
Return list of [index, item] pairs
```
set fruits to ["apple", "banana", "cherry"]
set pairs to enumerate(fruits)
print pairs  -- [[0, "apple"], [1, "banana"], [2, "cherry"]]
```

### `zip(list1, list2, ...)`
Combine multiple lists element-wise
```
set nums to [1, 2, 3]
set letters to ["a", "b", "c"]
set pairs to zip(nums, letters)
print pairs  -- [[1, "a"], [2, "b"], [3, "c"]]
```

### `reversed(list)`
Return reversed copy of list
```
set nums to [1, 2, 3, 4, 5]
print reversed(nums)  -- [5, 4, 3, 2, 1]
```

### `all(list)`
Return true if all items are truthy
```
print all([true, true, true])    -- true
print all([true, false, true])   -- false
print all([1, 2, 3])             -- true
```

### `any(list)`
Return true if any item is truthy
```
print any([false, false, true])  -- true
print any([false, false, false]) -- false
print any([0, 1, 0])             -- true
```

---

## Usage Examples

### Example 1: Text Processing
```
set sentence to "Hello World Human Language"
set words to sentence.lower().split(" ")
set length to len(words)
print "Words:", words
print "Count:", length
print "First word:", words(0).upper()
```

### Example 2: List Manipulation
```
set data to [5, 2, 8, 1, 9]
set sorted_data to sorted(data)
set min_val to min(data)
set max_val to max(data)
set sum_val to sum(data)

print "Sorted:", sorted_data
print "Min:", min_val
print "Max:", max_val
print "Sum:", sum_val
```

### Example 3: Data Pairing
```
set names to ["Alice", "Bob", "Charlie"]
set ages to [25, 30, 35]
set pairs to zip(names, ages)

for pair in pairs do
    print pair(0), "is", pair(1), "years old"
end for
```

### Example 4: Enumeration
```
set items to ["apple", "banana", "cherry"]
set indexed to enumerate(items)

for pair in indexed do
    set idx to pair(0)
    set item to pair(1)
    print idx, ":", item
end for
```

### Example 5: Data Filtering and Transformation
```
set numbers to [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

-- Filter even numbers
set evens to [x from x in numbers if x % 2 is equal to 0]
print "Evens:", evens

-- Transform to squares
set squares to [x * x from x in numbers]
print "Squares:", squares

-- Get min, max, sum
print "Min:", min(evens)
print "Max:", max(squares)
print "Total:", sum(squares)
```

---

## Complete Feature List

✅ **String Methods**: upper, lower, split, replace, strip, startswith, endswith, find, count, join, contains

✅ **List Methods**: append, pop, extend, index, count, reverse, clear, insert

✅ **Dict Methods**: keys, values, items, get, pop, clear, update

✅ **Builtin Functions**: sorted, min, max, sum, enumerate, zip, reversed, all, any

---

## Test It Out

Run the complete test:
```bash
human examples/string_and_list_methods.hm
```

This demonstrates all string, list, and dict methods along with the new builtin functions!
