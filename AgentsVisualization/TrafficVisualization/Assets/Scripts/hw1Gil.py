#Natalia Valles Villegas A01562597

import math
import sys

def rueda(lados, radio, ancho):
   #inicializacion de listas 
    vertex=[]
    normales=[]
    faces=[]
   
    #calcular coordenadas para +z y -z
    z=ancho/2
     #crear vertices en el centro de cada z
    vertex.append([z,0.0,0.0])
    vertex.append([-z,0.0,0.0])
     #loop para calcular posición de los vértices
    for i in range(lados):
        angle=(i*(2*math.pi))/lados #angulos de separación entre vértices
        #Calcular coordenadas de vértices x,y
        x=radio*math.cos(angle) 
        y=radio*math.sin(angle)
       
        #guardar los vértices en la lista para +z y -z
        vertex.append([z,x,y])
        vertex.append([-z,x,y])
    
    #loop para calcular las normales
    for i in range(len(vertex)):
        # crea variable para vector actual
        vector = [vertex[i][1], vertex[i][2], vertex[i][0]]
        # calcula magnitud del vector
        magnitud = math.sqrt(vector[0]**2 + vector[1]**2 + vector[2]**2)
        #calcular normal
        normal=[vector[0]/magnitud, vector[1]/magnitud, vector[2]/magnitud]
        # Guarda la normal en la lista
        normales.append(normal)
        
    #loops para calcular las caras
    #calcular lado de +z
    for i in range(2, len(vertex), 2):
        #calcular vértices de la cara
        v1=0
        v2=i
        v3=(i+2)%len(vertex)
        #agregar caras a la lista
        faces.append([v1,v2,v3])
        
    #connectar último con primero
    faces.append([0,len(vertex)-2,2])
    
    #calcular lado de -z
    for i in range(3, len(vertex), 2):
        #calcular vértices de la cara
        v1=1
        v2=i
        v3=(i+2)%len(vertex)
        #agregar caras a la lista
        faces.append([v3,v2,v1])
    
    #conectar último con primero
    faces.append([1,3,len(vertex)-1])
  
    
   
    for i in range(2, len(vertex), 2):
    # Cada cara está formada por cuatro vértices, dos arriba y dos abajo
    # Aquí creamos las caras del centro a partir de los índices de los vértices
      v1 = i
      v2 = (i + 2) 
      v3 = (i + 3) 
      v4 = (i + 1)
    # Agregamos las caras a la lista de caras
      faces.append([v3, v2, v1])
      faces.append([v4, v3, v1])
    
    #connectar último con primero
    faces.append([len(vertex)-2,len(vertex)-1,3])
    faces.append([len(vertex)-2, len(vertex)-1, 3])
    faces.append([3,2,len(vertex)-2])
    faces.append([3,2,len(vertex)-2])
    
    #crear .obj
    with open("rueda.obj", 'w') as f:
        f.write("#OBJ file\n")
        f.write("#Vertices\n")
        for vert in vertex:
            f.write(f"v {vert[0]} {vert[1]} {vert[2]}\n")
        f.write("#Normals\n")
        for normal in normales:
            f.write(f"vn {normal[0]} {normal[1]} {normal[2]}\n")
        f.write("#Faces\n")
        for face in faces:
            f.write(f"f {face[0] + 1}//{face[0] + 1} {face[1] + 1}//{face[1] + 1} {face[2] + 1}//{face[2] + 1}\n")


if __name__ == "__main__":
    lados=8
    radio=1.0
    ancho=0.5
    #obtener argumentos de la linea de comandos
    if len(sys.argv)>1:
        lados=int(sys.argv[1])
        radio=float(sys.argv[2])
        anlcho=float(sys.argv[3])
        
    #llamar a la función
    rueda(lados, radio, ancho)
