using System.Collections;
using System.Collections.Generic;
using UnityEngine;

// This class applies transformations to a 3D object in Unity.
public class ApplyTransforms : MonoBehaviour
{
    // The displacement vector for translation
    [SerializeField] Vector3 displacement; 
    // The angle for rotation
    [SerializeField] float angle; 
    // The axis for rotation
    [SerializeField] AXIS rotationAxis; 

    // The mesh of the 3D object
    Mesh mesh; 
    // The original vertices of the mesh
    Vector3[] baseVertices; 
    // The new vertices after transformation
    Vector3[] newVertices; 

    // This method is called at the start of the game.
    void Start(){
        // Get the mesh of the 3D object
        mesh = GetComponentInChildren<MeshFilter>().mesh; 
        // Get the original vertices of the mesh
        baseVertices = mesh.vertices; 

        newVertices = new Vector3[baseVertices.Length]; 
        for (int i = 0; i < baseVertices.Length; i++){ 
            newVertices[i] = baseVertices[i];
        }
    }

    // This method is called once per frame.
    void Update(){
        // Apply the transformations
        DoTransform(); 
    }

    // This method applies the transformations to the 3D object.
    void DoTransform(){
        // Create the translation matrix
        Matrix4x4 move = HW_Transforms.TranslationMat(displacement.x*Time.time,
                                                      displacement.y*Time.time,
                                                      displacement.z*Time.time);

        // Create the rotation matrix
        Matrix4x4 rotate = HW_Transforms.RotateMat(angle * Time.time,
                                                   rotationAxis);

        // Create the translation matrix to move the object back to the origin
        Matrix4x4 posOrigin = HW_Transforms.TranslationMat(-displacement.x, 
                                                           -displacement.y, 
                                                           -displacement.z);

        // Create the translation matrix to move the object back to its original position
        Matrix4x4 posObject = HW_Transforms.TranslationMat(displacement.x, 
                                                           displacement.y, 
                                                           displacement.z);

        // Combine the transformations
        Matrix4x4 composite = posObject*rotate*posOrigin;

        // Apply the transformations to each vertex of the mesh
        for (int i = 0; i<newVertices.Length; i++){
            Vector4 temp = new Vector4(baseVertices[i].x,baseVertices[i].y,baseVertices[i].z,1);
            newVertices[i] = composite * temp;
        }

        // Update the vertices of the mesh
        mesh.vertices = newVertices;
        // Recalculate the normals of the mesh for correct lighting
        mesh.RecalculateNormals();
    }
}