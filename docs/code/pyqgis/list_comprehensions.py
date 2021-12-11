my_list = [1, 2, 3, 4, 5]

# Create a new list by adding 1 to each element
new_list = []
for x in my_list:
    new_list.append(x+1)

print(new_list)

# Use list comprehension syntax

new_list = [x+1 for x in my_list]
print(new_list)
