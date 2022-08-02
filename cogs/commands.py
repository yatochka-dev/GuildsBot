class Some:

	some_attr = None

s = Some()

x = s.some_attr

print(s.some_attr)
print("x", x)
s.some_attr = "test"
print(s.some_attr)
print("x", x)
