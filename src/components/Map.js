import React, { useRef, useEffect } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

const Map = ({ routeData }) => {
  const mapContainerRef = useRef(null);
  const mapRef = useRef(null);

  useEffect(() => {
    mapboxgl.accessToken = process.env.REACT_APP_MAPBOX_TOKEN;

    // Initialize the map
    mapRef.current = new mapboxgl.Map({
      container: mapContainerRef.current,
      style: 'mapbox://styles/shubham-arutwar/clxublsj800up01pcfnb12wyb',
      center: [103.8198, 1.3521], // Default to Singapore coordinates
      zoom: 2,
    });

    // Cleanup on unmount
    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
      }
    };
  }, []); // Run only once on mount

  // Handle route data changes
  useEffect(() => {
    if (!mapRef.current || !routeData) return;

    const map = mapRef.current;

    // Wait for the map to be loaded
    if (!map.loaded()) {
      map.on('load', () => plotRoute(map, routeData));
    } else {
      plotRoute(map, routeData);
    }
  }, [routeData]); // Run when routeData changes

  const plotRoute = (map, routeData) => {
    const { ports, route_coordinates } = routeData;

    // Clear existing markers
    const existingMarkers = document.getElementsByClassName('mapboxgl-marker');
    while (existingMarkers[0]) {
      existingMarkers[0].remove();
    }

    // Remove existing route layer and source
    if (map.getSource('route')) {
      map.removeLayer('route');
      map.removeSource('route');
    }

    // Add markers for all ports
    ports.forEach((port, index) => {
      const color = index === 0 ? '#00ff00' : 
                   index === ports.length - 1 ? '#ff0000' : '#ffbb00';
      
      new mapboxgl.Marker({ color })
        .setLngLat(port.coordinates)
        .setPopup(
          new mapboxgl.Popup({ offset: 25 })
            .setHTML(`
              <h3 style="margin: 0 0 8px 0; font-weight: bold;">${port.name}</h3>
              <p style="margin: 0;">Port ID: ${port.id}</p>
            `)
        )
        .addTo(map);
    });

    // Format route coordinates for Mapbox
    const formattedCoordinates = route_coordinates.map(coord => [
      coord.Longtitude, // Note: keeping the original spelling from API
      coord.latitude
    ]);

    // Add the route line
    map.addSource('route', {
      type: 'geojson',
      data: {
        type: 'Feature',
        properties: {},
        geometry: {
          type: 'LineString',
          coordinates: formattedCoordinates
        }
      }
    });

    map.addLayer({
      id: 'route',
      type: 'line',
      source: 'route',
      layout: {
        'line-join': 'round',
        'line-cap': 'round'
      },
      paint: {
        'line-color': '#007cbf',
        'line-width': 3,
        'line-dasharray': [2, 1] // Create a dashed line effect
      }
    });

    // Fit map to show all markers and route
    const bounds = new mapboxgl.LngLatBounds();
    
    // Include all ports in bounds
    ports.forEach(port => {
      bounds.extend(port.coordinates);
    });
    
    // Include route coordinates in bounds
    formattedCoordinates.forEach(coord => {
      bounds.extend(coord);
    });

    map.fitBounds(bounds, {
      padding: 50,
      duration: 1000
    });
  };

  return (
    <div 
      ref={mapContainerRef} 
      className="map-container" 
      style={{ width: '100%', height: '500px' }} // Adjust height as needed
    />
  );
};

export default Map;