import json
import math
from queue import PriorityQueue
import folium

# Load GeoJSON data for port locations
with open('global_ports_locations.geojson') as f:
    ports_data = json.load(f)

# Load major routes data
with open('major_routes.json') as f:
    routes_data = json.load(f)

# Function to get port details (name and coordinates) based on port ID
def get_port_details(port_id):
    for feature in ports_data['features']:
        if feature['properties']['id'] == port_id:
            return feature['properties']['name'], feature['geometry']['coordinates'][1], feature['geometry']['coordinates'][0]  # name, latitude, longitude
    raise ValueError(f"Port with ID '{port_id}' not found in the dataset.")

# Create graph from major routes
def create_graph(routes_data):
    graph = {}
    for route in routes_data['routes']:
        start_port = route['from']
        end_port = route['to']
        distance = route['distance']

        # Get coordinates of start and end ports
        _, start_lat, start_lon = get_port_details(start_port)
        _, end_lat, end_lon = get_port_details(end_port)

        start_coords = (start_lat, start_lon)
        end_coords = (end_lat, end_lon)

        # Initialize graph with start and end ports
        if start_coords not in graph:
            graph[start_coords] = []
        if end_coords not in graph:
            graph[end_coords] = []

        # Add the distance between ports to the graph
        graph[start_coords].append((end_coords, distance, end_port))
        graph[end_coords].append((start_coords, distance, start_port))  # Bidirectional

    return graph

# Reconstruct the path from start to goal and track the distance
def reconstruct_path(came_from, current, start, distances):
    total_path = [current]
    total_distance = 0
    while current in came_from:
        previous = came_from[current]
        total_distance += distances[(previous, current)]  # Summing up the distance
        total_path.append(previous)
        current = previous
    total_path.reverse()
    return total_path, total_distance

# A* algorithm with fuel considerations
def a_star_with_fuel(graph, start, goal, max_fuel_capacity, ports):
    open_list = PriorityQueue()
    open_list.put((0, start, max_fuel_capacity))  # Include fuel in the priority queue
    
    came_from = {}
    g_score = {node: float('inf') for node in graph}
    g_score[start] = 0
    
    distances = {}  # To store the distances between nodes
    fuel_at_port = {node: 0 for node in graph}  # To track the remaining fuel at each port

    while not open_list.empty():
        _, current, current_fuel = open_list.get()

        if current == goal:
            return reconstruct_path(came_from, current, start, distances)  # Path found

        for neighbor, distance, port_id in graph[current]:
            if distance <= current_fuel:  # Only consider this neighbor if within fuel range
                tentative_g_score = g_score[current] + distance
                refueled_fuel = max_fuel_capacity  # Refuel at the neighbor port

                if tentative_g_score < g_score[neighbor]:
                    g_score[neighbor] = tentative_g_score
                    came_from[neighbor] = current
                    distances[(current, neighbor)] = distance  # Store the distance between current and neighbor
                    fuel_at_port[neighbor] = refueled_fuel
                    open_list.put((tentative_g_score, neighbor, refueled_fuel))

    return None, None  # Return None if no path is found

# Take input of starting and destination port IDs
start_port_id = int(input("Enter starting port ID: "))
destination_port_id = int(input("Enter destination port ID: "))
max_fuel_capacity = float(input("Enter maximum fuel capacity (in km): "))  # New input for fuel capacity

# Get the details for the starting and destination ports
start_name, start_lat, start_lon = get_port_details(start_port_id)
destination_name, destination_lat, destination_lon = get_port_details(destination_port_id)

# Create the graph from routes
graph = create_graph(routes_data)

# Call the A* algorithm with fuel constraints to get the path and total distance
path, total_distance = a_star_with_fuel(graph, (start_lat, start_lon), (destination_lat, destination_lon), max_fuel_capacity, ports_data)

# Check and display the path with port names and total distance
if path:
    print("Optimal path found:")
    print(f"Starting at: {start_name}")
    for coords in path[1:-1]:  # Print intermediate port names
        for feature in ports_data['features']:
            lat, lon = feature['geometry']['coordinates'][1], feature['geometry']['coordinates'][0]
            if (lat, lon) == coords:
                print(f"Via: {feature['properties']['name']}")
    print(f"Destination: {destination_name}")
    print(f"Total distance traveled: {total_distance} km")

    # Visualization using Folium
    map_route = folium.Map(location=[start_lat, start_lon], zoom_start=5)
    
    # Add the starting point marker
    folium.Marker([start_lat, start_lon], popup=f"Start: {start_name}", icon=folium.Icon(color="green")).add_to(map_route)
    
    # Add the destination point marker
    folium.Marker([destination_lat, destination_lon], popup=f"Destination: {destination_name}", icon=folium.Icon(color="red")).add_to(map_route)
    
    # Add the route to the map
    folium.PolyLine(path, color="blue", weight=2.5, opacity=1).add_to(map_route)
    
    # Save the map to an HTML file
    map_route.save("optimal_route_map_with_fuel.html")
else:
    print("No valid path found.")
