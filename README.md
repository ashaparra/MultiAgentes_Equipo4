# MultiAgentes Equipo4:
Arantza Parra Martinez A01782023

Natalia Valles Villegas A01562597

Link al video en youtube: https://youtu.be/58T0fQzELq4

Al carro se le inicializa un grid, conformado por todas las celdas visitables y se conectan
en base a su dirección.
Busca un path en base a este grid, utilizando dijkstra para que sea el menor posible, sigue 
las restricciones de avanzar conforme al estado de semáforos y dirección de calles.
Tiene paciencia, lo que hace que algunas veces espere en el tráfico y cuando se le acabe,
se mueve a una celda adyacente y recalcula el path.