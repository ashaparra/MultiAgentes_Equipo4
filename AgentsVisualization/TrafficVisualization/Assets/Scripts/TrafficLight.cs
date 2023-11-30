using System.Collections;
using System.Collections.Generic;
using UnityEngine;
public class TrafficLight : MonoBehaviour {

    // [SerializeField] bool state;Vo
    public void SetState(bool state){
        if(state){
            this.GetComponentInChildren<Light>().color = Color.green;
        }else{
            this.GetComponentInChildren<Light>().color = Color.red;
        }
    }
    public void SetDirection(string direction){
        Vector3 rotationAngle = Vector3.zero;

        switch(direction){
            case "Rigth":
                rotationAngle = new Vector3(0, 0, 0); // Adjust these values as needed
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
            // Add more cases if there are more directions
        }
        this.transform.eulerAngles = rotationAngle;
    }
}
    
