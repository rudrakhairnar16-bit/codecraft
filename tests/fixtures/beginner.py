"""A beginner-level Python file for testing concept extraction."""

name = input("What is your name? ")
print("Hello, " + name)

age = int(input("How old are you? "))

if age >= 18:
    print("You are an adult")
else:
    print("You are a minor")

numbers = [1, 2, 3, 4, 5]
total = 0
for num in numbers:
    total = total + num
print("Sum:", total)

count = 0
while count < 5:
    print(count)
    count = count + 1

try:
    result = 10 / 0
except:  # noqa: E722
    print("Something went wrong")

f = open("data.txt")
content = f.read()
f.close()
print(content)
