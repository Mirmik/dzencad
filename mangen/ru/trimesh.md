:ru
# Триангуляция и меш

__EXPERIMENTAL__

Функции для работы с полигональным представлением.
:en
# Triangulation and mesh

__EXPERIMENTAL__

Functions for working with polygonal representation. 
::

---
:ru
## Триангуляция
Построение полигональной сетки в формате (_nodes_, _triangles_), где _pnts_ - массив точек, а _triangles_ - массив 3-кортежей, индексов точек.
Параметр _deflection_ отвечает за разрешение разбиения. 
:en
## Triangulation
Creation of a polygonal mesh in the format (_nodes_, _triangles_), where _pnts_ is an array of points, and _triangles_ is an array of 3-tuples, indices of points.
The _deflection_ parameter is responsible for resolving the splitting. 
::

Сигнатура:
```python
nodes, triangles = triangulate(shp, deflection)
```

Пример:
```python
m=sphere(10)
nodes, triangles = triangulate(m, 0.1)

print("count_of_nodes:", len(nodes))
print("count_of_triangles:", len(triangles))

print("first_five_nodes:", nodes[:5])
print("first_five_triangles:", triangles[:5])

#count_of_nodes: 699
#count_of_triangles: 1362
#first_five_nodes: [point3(0.000000,-0.000000,10.000000), point3(0.000000,-0.000000,10.000000), point3(0.000000,-0.000000,-10.000000), point3(1.950903,-0.000000,-9.807853), point3(3.826834,-0.000000,-9.238795)]
#first_five_triangles: [[237, 227, 200], [486, 482, 470], [237, 200, 211], [487, 472, 477], [238, 201, 212]]
```

-----------------------------
:ru
## Полигедрон
Объёмное тело, состоящее из плоских граней, заданное точками вершин _pnts_ и массивом кортежей индексов точек, задающих грани.
:en
## Polyhedrone
A solid consisting of flat faces, specified by vertex points _pnts_ and an array of tuples of indices of points defining the faces. 
::

Сигнатура:
```python
polyhedron(pnts, faces, shell=False)
```

Пример:
```python
m=sphere(10)
nodes, triangles = triangulate(m, 0.1)
disp(polyhedron(nodes, triangles))
```
![](../images/generic/polyhedron0.png)

----------------------------------------------
:ru
## Выпуклая оболочка
Построение выпуклой оболочки множества точек.
Используется процедура scipy.spatial.ConvexHull

_convex_hull_ вычисляет массив индексов точек полигонов выпуклой оболочки.
_convex_hull_shape_ строит выпуклую оболочку, используя процедуру _polyhedron_.

Опции:
_incremental_ и _qhull_options_ являются опциями scipy.spatial.ConvexHull (см. документацию scipy).
_shell_ - создать оболочку вместо тела.
:en
## Convex hull
Construction of the convex hull of a set of points.
The scipy.spatial.ConvexHull procedure is used

_convex_hull_ computes an array of convex hull polygon point indices.
_convex_hull_shape_ builds a convex hull using the _polyhedron_ procedure.

Options:
_incremental_ and _qhull_options_ are scipy.spatial.ConvexHull options (see scipy documentation).
_shell_ - create a shell instead of a body.
::

Сигнатура:
```python
convex_hull(pnts, incremental=False, qhull_options=None)
convex_hull_shape(pnts, shell=False, incremental=False, qhull_options=None)
```

Пример:
```python
pnts = points([
	( 0,  0,  0),
	(10,  0,  0),
	(10, 10,  0),
	( 0, 10,  0),
	( 5,  5, 10),
])

print(convex_hull(pnts))
disp(convex_hull_shape(pnts))
```

![](../images/generic/convex_hull0.png)
