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
    [SerializeField] Vector3 lastPosition= new Vector3(0,0,0);
    Mesh mesh;
    Vector3[] baseVertices;
    Vector3[] newVertices;
    List<GameObject> wheelsList;
    List<Mesh> wheelsMeshes;
    List<Vector3[]> baseWheelsVertices;
    List<Vector3[]> newWheelsVertices;
    List<Color> colors;
    float timer = 0.0f;
    float timeToUpdate = 1.0f;
    float dt = 0.0f;
    private float lastRotationYDeg;

    // Lista de colores posibles para el carro
    List<Color> possibleColors= new List<Color>(){
        Color.red,
        Color.green,
        Color.blue,
        Color.yellow,
        Color.magenta,
        Color.cyan,
        Color.white,
        Color.black,
        Color.gray,
        new Color(1.0f, 0.5f, 0.0f) // Orange: R=1, G=0.5, B=0
    };

    public List<GameObject> GetWheelObjects() // returns the list of wheel objects
    {
        return wheelsList;
    }

    void Start()
    {
        
        //Obtener mesh del carro
        mesh = GetComponentInChildren<MeshFilter>().mesh;
        baseVertices = mesh.vertices;
        newVertices = new Vector3[baseVertices.Length];
        for (int i = 0; i < baseVertices.Length; i++){
            newVertices[i] = baseVertices[i];
        }
        //Colores
        if (possibleColors.Count > 0)
        {
            Color randomColor = possibleColors[Random.Range(0, possibleColors.Count)];
            ApplyColor(randomColor);
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
        
            dt=Mathf.Clamp(dt,0,1);
            Vector3 target = Vector3.Lerp(startPosition, endPosition, dt);
            return target;
    }
    void ApplyColor(Color color)
    {
        Renderer renderer = GetComponentInChildren<Renderer>();
        renderer.material.color = color;
    }
    void Update()
    {
        //Llamar a transformaciones para el carro
        timer -= Time.deltaTime;
        dt = 1.0f - (timer / timeToUpdate);
        DoTransform(NewTarget(startPosition, endPosition, dt));
    }
    public void SetMove(Vector3 targetPosition){
        // DoTransform(NewTarget(currentPosition, targetPosition, dt));
        timer = timeToUpdate;
        startPosition = endPosition;
        endPosition = targetPosition;
        
    }
    public void SetTime(float time){
        timeToUpdate = time;
    }

    void DoTransform(Vector3 position)
    {
        //Rotaciones
        //Posicionar el carro volteando a 0 0 0 originalmente (frente)
        Matrix4x4 orientCar= HW_Transforms.RotateMat(180, AXIS.Y);
        //Calcular rotacion para el carro en base a donde se esta moviendo en x y y
        float rotateYDeg;
        if (startPosition != endPosition)
        {
                float rotateYRad = Mathf.Atan2(endPosition.z - startPosition.z, endPosition.x - startPosition.x);
                rotateYDeg = rotateYRad * Mathf.Rad2Deg;
                lastRotationYDeg = rotateYDeg; // Update the last known rotation
        }
        else
            {
                rotateYDeg = lastRotationYDeg; // Use the last known rotation
            }
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
        mesh.RecalculateBounds();
        
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
            wheelsMeshes[wheel].RecalculateBounds();
        }  
    }
}

