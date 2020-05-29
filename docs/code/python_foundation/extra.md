# Miscellaneous Concepts

## List Comprehension


```python
countries = ['USA', 'Canada', 'Mexico']
capitals = ['Washington D. C.', 'Ottawa', 'Mexico City']
for x in zip(countries, capitals):
    print(x)
```

    ('USA', 'Washington D. C.')
    ('Canada', 'Ottawa')
    ('Mexico', 'Mexico City')



```python
country_capitals_list = []
for x in zip(countries, capitals):
    country_capitals_list.append(x)
print(country_capitals_list)
```

    [('USA', 'Washington D. C.'), ('Canada', 'Ottawa'), ('Mexico', 'Mexico City')]



```python
country_capitals_list = [x for x in zip(countries, capitals)]
print(country_capitals_list)
```

    [('USA', 'Washington D. C.'), ('Canada', 'Ottawa'), ('Mexico', 'Mexico City')]

