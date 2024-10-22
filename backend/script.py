from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import heapq
from collections import defaultdict
import logging

app = Flask(__name__)
CORS(app)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load the data
def load_data():
    try:
        with open('global_ports_locations.geojson') as f:
            ports_data = json.load(f)
        logger.info(f"Loaded {len(ports_data['features'])} ports")
        
        with open('major_routes.json') as f:
            routes_data = json.load(f)
        logger.info(f"Loaded {len(routes_data['routes'])} routes")
        
        return ports_data, routes_data
    except FileNotFoundError as e:
        logger.error(f"Failed to load data files: {e}")
        raise

# Create a graph representation of the routes
def create_graph(routes_data):
    graph = defaultdict(list)
    route_details = {}
    
    for route in routes_data['routes']:
        from_port = route['from']
        to_port = route['to']
        distance = route['distance']
        route_path = [{'latitude': point['latitude'], 'Longtitude': point['Longtitude']} for point in route['route']]
        
        graph[from_port].append((to_port, distance))
        graph[to_port].append((from_port, distance))
        
        route_details[(from_port, to_port)] = route_path
        route_details[(to_port, from_port)] = route_path[::-1]
    
    logger.info(f"Created graph with nodes: {dict(graph)}")  # Added for debugging
    return graph, route_details

# Modified Dijkstra's algorithm with fuel constraint
def find_route(graph, start, end, max_fuel, ports_data, route_details):
    logger.info(f"Finding route from port {start} to {end} with max fuel {max_fuel}")
    
    if start not in graph:
        logger.warning(f"Start port {start} not found in graph")
        return None
    if end not in graph:
        logger.warning(f"End port {end} not found in graph")
        return None
    
    pq = [(0, start, [start], [])]
    visited = set()
    
    while pq:
        total_distance, current, path, coords = heapq.heappop(pq)
        logger.debug(f"Visiting port {current}, total distance so far: {total_distance}")
        
        if current == end:
            logger.info(f"Found route! Total distance: {total_distance}")
            # Get port details for the path
            port_details = []
            for port_id in path:
                port_feature = next(
                    (f for f in ports_data['features'] if f['properties']['id'] == port_id),
                    None
                )
                if port_feature:
                    port_details.append({
                        'id': port_id,
                        'name': port_feature['properties']['name'],
                        'coordinates': port_feature['geometry']['coordinates']
                    })
            
            return {
                'success': True,
                'total_distance': total_distance,
                'path': path,
                'ports': port_details,
                'route_coordinates': coords
            }
        
        if current in visited:
            continue
            
        visited.add(current)
        
        for next_port, segment_distance in graph[current]:
            if segment_distance <= max_fuel:
                logger.debug(f"Considering route {current} -> {next_port} (distance: {segment_distance})")
                new_distance = total_distance + segment_distance
                new_path = path + [next_port]
                
                route_key = (current, next_port)
                segment_coords = route_details.get(route_key, [])
                new_coords = coords + segment_coords
                
                heapq.heappush(pq, (new_distance, next_port, new_path, new_coords))
            else:
                logger.debug(f"Skipping route {current} -> {next_port} (distance {segment_distance} exceeds fuel capacity)")
    
    logger.warning("No valid route found")
    return None

@app.route('/api/route', methods=['POST'])
def get_route():
    data = request.get_json()
    logger.info(f"Received request with data: {data}")
    
    try:
        start_port = int(data.get('start'))
        end_port = int(data.get('end'))
        max_fuel = int(data.get('maxFuel'))
        print(start_port, end_port, max_fuel)
        # Load data and create graph
        ports_data, routes_data = load_data()
        graph, route_details = create_graph(routes_data)
        
        # Find route
        result = find_route(graph, start_port, end_port, max_fuel, ports_data, route_details)
        
        if result:
            return jsonify(result)
        else:
            return jsonify({
                'success': False,
                'message': 'No valid route found with given fuel constraint'
            })
    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)