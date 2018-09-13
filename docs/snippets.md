# Snippets

```Python
motors = np.array([
    (0, 1, 2, 3),
    (4, 5, 6, 7),
    (8, 9, 10, 11),
    (12, 13, 14, 15),
])

ys, xs = np.indices(motors.shape)

m0 = 5
m1 = 9
coords0 = np.array((xs[motors == m0], ys[motors == m0]))
coords1 = np.array((xs[motors == m1], ys[motors == m1]))
movement = coords1 - coords0

movement
```
