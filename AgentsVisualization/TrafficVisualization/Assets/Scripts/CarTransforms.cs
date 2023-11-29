using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CarTransforms : MonoBehaviour
{
    
    [Header ("Wheels")]
    [SerializeField] Vector3 wheelScale;
    [SerializeField] GameObject wheelPrefab;
    [SerializeField] List<Vector3> wheels;

    [Header ("Car")]
    [SerializeField] Vector3 carScale;

    [Header ("Movement interpolation")]
    [SerializeField] Vector3 startPosition= new Vector3(0,0,0);
    [SerializeField] Vector3 endPosition= new Vector3(0,0,0);
    Mesh mesh;
    Vector3[] baseVertices;
    Vector3[] newVertices;
    List<GameObject> wheelsList;
    List<Mesh> wheelsMeshes;
    List<Vector3[]> baseWheelsVertices;
    List<Vector3[]> newWheelsVertices;


    void Start()
    {
        //Obtener mesh del carro
        mesh = GetComponentInChildren<MeshFilter>().mesh;
        baseVertices = mesh.vertices;
        newVertices = new Vector3[baseVertices.Length];
        for (int i = 0; i < baseVertices.Length; i++){
            newVertices[i] = baseVertices[i];
        }
         //Crear llantas inicialmente en 0 0 0
        wheelsList = new List<GameObject>();
        for(int i =0; i<wheels.Count; i++){
            GameObject wheel = Instantiate(wheelPrefab, new Vector3(0,0,0), Quaternion.identity);
            wheelsList.Add(wheel);
        }
        //Obtener mesh de las llantas
        wheelsMeshes = new List<Mesh>();
        baseWheelsVertices= new List<Vector3[]>();
        newWheelsVertices= new List<Vector3[]>();
        for(int k = 0; k < wheelsList.Count; k++){
            wheelsMeshes.Add(wheelsList[k].GetComponentInChildren<MeshFilter>().mesh);
            var wheelVertices = wheelsMeshes[k].vertices;
            baseWheelsVertices.Add(wheelVertices);
            newWheelsVertices.Add(new Vector3[wheelVertices.Length]);
            for (int j = 0; j < wheelVertices.Length; j++){
                newWheelsVertices[k][j] = wheelVertices[j];
            }
        }
    }
    Vector3 NewTarget(Vector3 currentPosition, Vector3 targetPosition, float dt){
        if (endPosition != targetPosition){
            startPosition = currentPosition;
            endPosition = targetPosition;
            dt=Mathf.Clamp(dt,0,1);
            Vector3 target = Vector3.Lerp(startPosition, endPosition, dt);
            return target;
        }
        else{
            return targetPosition;
        }
    }
    public void SetMove(Vector3 currentPosition, Vector3 targetPosition, float dt){
        DoTransform(NewTarget(currentPosition, targetPosition, dt));
        
    }
    void DoTransform(Vector3 position)
    {
        //Rotaciones
        //Posicionar el carro volteando a 0 0 0 originalmente (frente)
        Matrix4x4 orientCar= HW_Transforms.RotateMat(90, AXIS.Y);
        //Calcular rotacion para el carro en base a donde se esta moviendo en x y y
        float rotateYRad = Mathf.Atan2(endPosition.x - startPosition.x, endPosition.z - startPosition.z);
        //Convertir de radianes a grados
        float rotateYDeg = rotateYRad * Mathf.Rad2Deg;
        //Crear matriz de rotacion en y
        Matrix4x4 rotateY = HW_Transforms.RotateMat(rotateYDeg, AXIS.Y);
        
        //Rotar el carro 180 y después rotarlo en la direccion que se esta moviendo
        Matrix4x4 rotate = rotateY * orientCar;

        //Mover carro
        //Calcular en que direccion se va a mover, con el input de unity
        Matrix4x4 move = HW_Transforms.TranslationMat(position.x, position.y, position.z);
        
        Matrix4x4 scaleMat = HW_Transforms.ScaleMat(carScale.x, carScale.y, carScale.z);
        //Crear matriz compuesta de rotacion y traslacion
        Matrix4x4 composite = move  * rotate * scaleMat;
        //Aplicar composite a cada vértice del carro
        for (int i = 0; i<newVertices.Length; i++){
            Vector4 temp = new Vector4(baseVertices[i].x,baseVertices[i].y,baseVertices[i].z,1);
            newVertices[i] = composite * temp;
        }
        //Actualizar mesh
        mesh.vertices = newVertices;
        mesh.RecalculateNormals();
        
        //Llamar a transformaciones para las llantas
        DoTransformWheels(composite);
        
    }
    void DoTransformWheels(Matrix4x4 composite)
    {
        //Aplicar cambios por cada llanta
        for (int wheel = 0; wheel<wheels.Count; wheel++){
            //escalar llantas
            Matrix4x4 scaleMat = HW_Transforms.ScaleMat(wheelScale.x, wheelScale.y, wheelScale.z);
            //mover llantas según los inputs de unity
            Matrix4x4 move = HW_Transforms.TranslationMat(wheels[wheel].x, wheels[wheel].y, wheels[wheel].z);
            //rotar llantas inicialmente 90 grados 
            Matrix4x4 rotate = HW_Transforms.RotateMat(90, AXIS.Y);
            //rotaciones en x para que la llanta gire
            Matrix4x4 rotateX= HW_Transforms.RotateMat((-40)*Time.time, AXIS.Z);
            //aplicar movimientos a llanta
            Matrix4x4 compositeW = composite * move *rotateX * rotate * scaleMat;
            
            //aplicar transformaciones a cada vértice de cada llanta
            for (int i = 0; i<newWheelsVertices[wheel].Length; i++){
            Vector4 temp = new Vector4(baseWheelsVertices[wheel][i].x,baseWheelsVertices[wheel][i].y,baseWheelsVertices[wheel][i].z,1);
            newWheelsVertices[wheel][i] = compositeW * temp;
            }
            //Actualizar mesh de la llanta
            wheelsMeshes[wheel].vertices = newWheelsVertices[wheel];
            wheelsMeshes[wheel].RecalculateNormals();
        }  
    }
}

