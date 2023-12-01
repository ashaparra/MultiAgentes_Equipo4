using System.Collections;
using System.Collections.Generic;
using UnityEngine;

// This class represents a traffic light in a game or simulation.
public class TrafficLight : MonoBehaviour {

    // This method sets the state of the traffic light.
    public void SetState(bool state){
        // If the state is true, the light color is set to green.
        if(state){
            this.GetComponentInChildren<Light>().color = Color.green;
        }else{
            // If the state is false, the light color is set to red.
            this.GetComponentInChildren<Light>().color = Color.red;
        }
    }

    // This method sets the direction of the traffic light by rotating it.
    public void SetDirection(string direction){
        Vector3 rotationAngle = Vector3.zero;

        switch(direction){
            case "Rigth":
                rotationAngle = new Vector3(0, 0, 0); 
                break;
            case "Left":
                rotationAngle = new Vector3(0, 180, 0); 
                break;
            case "Up":
                rotationAngle = new Vector3(0, -90, 0); 
                break;
            case "Down":
                rotationAngle = new Vector3(0, 90, 0); 
                break;
        }
        // Apply the rotation angle to the traffic light.
        this.transform.eulerAngles = rotationAngle; 
    }
}