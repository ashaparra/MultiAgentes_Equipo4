// TC2008B. Sistemas Multiagentes y Gráficas Computacionales
// C# client to interact with Python. Based on the code provided by Sergio Ruiz.
// Octavio Navarro. October 2023

using System;
using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Networking;

// Class to store the data of each agent
[Serializable]
public class AgentData
{
    /*
    The AgentData class is used to store the data of each agent.
    
    Attributes:
        id (string): The id of the agent.
        x (float): The x coordinate of the agent.
        y (float): The y coordinate of the agent.
        z (float): The z coordinate of the agent.
    */
    // The id of the agent
    public string id;
    // The coordinates of the agent
    public float x, y, z;

    public AgentData(string id, float x, float y, float z)
    {
        this.id = id;
        this.x = x;
        this.y = y;
        this.z = z;
    }

}

// Class to store the data of each traffic light
[Serializable]
public class TrafficLigthData
{
    /*
    The TrafficLigth class is used to store the data of each agent.
    
    Attributes:
        id (string): The id of the agent.
        x (float): The x coordinate of the agent.
        y (float): The y coordinate of the agent.
        z (float): The z coordinate of the agent.
        state (string): The state of the agent.
    */
    public string id;
    public float x, y, z;
    public bool state;
    public string direction;

    // Constructor for the TrafficLigthData class
    public TrafficLigthData(string id, float x, float y, float z, bool state, string direction)
    {
        this.id = id;
        this.x = x;
        this.y = y;
        this.z = z;
        this.state =state;
        this.direction = direction;
    }

}

[Serializable]

// Class to store the data of all the agents
public class AgentsData
{
    /*
    The AgentsData class is used to store the data of all the agents.

    Attributes:
        positions (list): A list of AgentData objects.
    */
    public List<AgentData> positions;

    // Constructor for the AgentsData class
    public AgentsData() => this.positions = new List<AgentData>();
}

// Class to store the data of all the traffic lights
[Serializable]
public class TrafficLightsData{
    /*
    The AgentsData class is used to store the data of all the agents.

    Attributes:
        positions (list): A list of AgentData objects.
    */
    public List<TrafficLigthData> positions;

    // Constructor for the TrafficLightsData class
    public TrafficLightsData() => this.positions = new List<TrafficLigthData>();
}

// Class to control the agents in the simulation
public class AgentController : MonoBehaviour
{
    /*
    The AgentController class is used to control the agents in the simulation.

    Attributes:
        serverUrl (string): The url of the server.
        getAgentsEndpoint (string): The endpoint to get the agents data.
        getObstaclesEndpoint (string): The endpoint to get the obstacles data.
        sendConfigEndpoint (string): The endpoint to send the configuration.
        updateEndpoint (string): The endpoint to update the simulation.
        agentsData (AgentsData): The data of the agents.
        obstacleData (AgentsData): The data of the obstacles.
        agents (Dictionary<string, GameObject>): A dictionary of the agents.
        prevPositions (Dictionary<string, Vector3>): A dictionary of the previous positions of the agents.
        currPositions (Dictionary<string, Vector3>): A dictionary of the current positions of the agents.
        updated (bool): A boolean to know if the simulation has been updated.
        started (bool): A boolean to know if the simulation has started.
        agentPrefab (GameObject): The prefab of the agents.
        obstaclePrefab (GameObject): The prefab of the obstacles.
        floor (GameObject): The floor of the simulation.
        NAgents (int): The number of agents.
        width (int): The width of the simulation.
        height (int): The height of the simulation.
        timeToUpdate (float): The time to update the simulation.
        timer (float): The timer to update the simulation.
        dt (float): The delta time.
    */
    // Server and endpoint
    string serverUrl = "http://localhost:8585";
    string getAgentsEndpoint = "/getAgents";
    string getObstaclesEndpoint = "/getObstacles";
    string getTrafficLightsEndpoint = "/getTrafficLights";
    string getRoadsEndpoint = "/getRoads";
    string getDestinationsEndpoint = "/getDestinations";
    string sendConfigEndpoint = "/init";
    string updateEndpoint = "/update";

    // Data of the agents, obstacles, roads, and destinations
    public AgentsData agentsData, obstacleData, roadsData, destinationsData;
    public TrafficLightsData trafficLightsData;

    // Simulation parameters
    public int NAgents = 10, width = 10, height = 10;
    Dictionary<string, GameObject> agents;
    Dictionary<string, Vector3> prevPositions, currPositions;
    Dictionary<string, GameObject> trafficLights;
    bool updated = false, started = false;}

    // Prefabs for the agents, obstacles, traffic lights, roads, and destinations
    public GameObject agentPrefab, obstaclePrefab, trafficLigthPrefab, roadPrefab, destinationPrefab;
    public float timeToUpdate = 0.5f;
    private float timer, dt;

    void Start()
{
    // Initialize the data
    agentsData = new AgentsData();
    obstacleData = new AgentsData();
    trafficLightsData = new TrafficLightsData();
    roadsData = new AgentsData();
    destinationsData = new AgentsData();

    prevPositions = new Dictionary<string, Vector3>();
    currPositions = new Dictionary<string, Vector3>();

    agents = new Dictionary<string, GameObject>();
    trafficLights = new Dictionary<string, GameObject>();
    
    timer = timeToUpdate;

    // Start a coroutine to send the configuration to the server.
    StartCoroutine(SendConfiguration());
}

private void Update() 
{
    // If the timer has reached zero
    if(timer < 0)
    {
        // Reset the timer and start the update process
        timer = timeToUpdate;
        updated = false;
        StartCoroutine(UpdateSimulation());
    }

    // If the simulation has been updated
    if (updated)
    {
        // Decrease the timer by the time since the last frame
        timer -= Time.deltaTime;
        dt = 1.0f - (timer / timeToUpdate);
        // Update the state of each traffic light
        foreach(var tl in trafficLightsData.positions)
        {
            if(trafficLights.ContainsKey(tl.id))
            {
                trafficLights[tl.id].GetComponent<TrafficLight>().SetState(tl.state);
            }
        }
    }
}

IEnumerator UpdateSimulation()
{
    // Send a GET request to the server to update the simulation
    UnityWebRequest www = UnityWebRequest.Get(serverUrl + updateEndpoint);
    yield return www.SendWebRequest();
 
    // If the request failed, log the error
    if (www.result != UnityWebRequest.Result.Success)
        Debug.Log(www.error);
    else 
    {
        // If the request succeeded, start coroutines to get the data of the agents and traffic lights
        StartCoroutine(GetAgentsData());
        StartCoroutine(GetTrafficLightsData());
    }
}

IEnumerator SendConfiguration()
{
    // Create a form with the number of agents, width, and height
    WWWForm form = new WWWForm();
    form.AddField("NAgents", NAgents.ToString());
    form.AddField("width", width.ToString());
    form.AddField("height", height.ToString());

    // Send a POST request to the server with the form
    UnityWebRequest www = UnityWebRequest.Post(serverUrl + sendConfigEndpoint, form);
    www.SetRequestHeader("Content-Type", "application/x-www-form-urlencoded");

    yield return www.SendWebRequest();

    // If the request failed, log the error
    if (www.result != UnityWebRequest.Result.Success)
    {
        Debug.Log(www.error);
    }
    else
    {
        // If the request succeeded, start coroutines to get the data of the agents, obstacles, traffic lights, roads, and destinations
        StartCoroutine(GetAgentsData());
        StartCoroutine(GetObstacleData());
        StartCoroutine(GetTrafficLightsData());
        StartCoroutine(GetRoadsData());
        StartCoroutine(GetDestinationsData());
    }
}