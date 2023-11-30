using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Building : MonoBehaviour
{
    public void SetColor()
    {
        Color randomColor = new Color(Random.value, Random.value, Random.value);    
        Renderer renderer = GetComponentInChildren<Renderer>();
        renderer.material.color = randomColor;
    }
    }
