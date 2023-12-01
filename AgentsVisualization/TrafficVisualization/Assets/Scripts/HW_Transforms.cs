/*
Functions to work with transformation matrices in 3D

Gilberto Echeverria
2022-11-03
*/

using System.Collections;
using System.Collections.Generic;
using UnityEngine;

// Enumeration to define the axis
public enum AXIS {X, Y, Z}; // X, Y, and Z represent the three axes in 3D space.

public class HW_Transforms : MonoBehaviour
{
    // This function creates a translation matrix for a given translation along the x, y, and z axes.
    public static Matrix4x4 TranslationMat(float tx, float ty, float tz)
    {
        Matrix4x4 matrix = Matrix4x4.identity; 
        matrix[0, 3] = tx; 
        matrix[1, 3] = ty; 
        matrix[2, 3] = tz; 
        return matrix; 
    }

    // This function creates a scaling matrix for a given scale along the x, y, and z axes.
    public static Matrix4x4 ScaleMat(float sx, float sy, float sz)
    {
        Matrix4x4 matrix = Matrix4x4.identity; 
        matrix[0, 0] = sx; 
        matrix[1, 1] = sy; 
        matrix[2, 2] = sz; 
        return matrix; 
    }

    // This function creates a rotation matrix for a given angle and axis of rotation.
    public static Matrix4x4 RotateMat(float angle, AXIS axis)
    {
        // Convert the angle from degrees to radians
        float rads = angle * Mathf.Deg2Rad; 
        // Calculate the sine of the angle
        float sinTheta=Mathf.Sin(rads); 
        // Calculate the cosine of the angle
        float cosTheta = Mathf.Cos(rads); 

        Matrix4x4 matrix = Matrix4x4.identity; 
        // If the axis of rotation is the x-axis
        if (axis == AXIS.X) { 
            matrix[1, 1] = cosTheta;
            matrix[2, 1] = -sinTheta;
            matrix[1, 2] = sinTheta;
            matrix[2, 2] = cosTheta;
            // If the axis of rotation is the y-axis
        } else if (axis == AXIS.Y) { 
            matrix[0, 0] = cosTheta;
            matrix[0, 2] = -sinTheta;
            matrix[2, 0] = sinTheta;
            matrix[2, 2] = cosTheta;
             // If the axis of rotation is the z-axis
        } else if (axis == AXIS.Z) {
            matrix[0, 0] = cosTheta;
            matrix[0, 1] = sinTheta;
            matrix[1, 0] = -sinTheta;
            matrix[1, 1] = cosTheta;
        }
        return matrix; 
    }
}