//Code that handles the color of the buildings
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Building : MonoBehaviour
{
    public void SetColor()
    {
        //Creates a random color and then sets it to the building
        Color randomColor = new Color(Random.value, Random.value, Random.value);    
        Renderer renderer = GetComponentInChildren<Renderer>();
        renderer.material.color = randomColor;
    }
    }
