export const addPolygons = (map) => {
    fetch('/highlight-area.geojson')
      .then(response => response.json())
      .then(data => {
        console.log('Fetched GeoJSON:', data);

        map.addSource('highlighted-area', {
          type: 'geojson',
          data: data,
        });

        map.addLayer({
          id: 'highlighted-area-fill',
          type: 'fill',
          source: 'highlighted-area',
          layout: {},
          paint: {
            'fill-color': '#E77',
            'fill-opacity': 0.5,
          },
        });
      })
      .catch(error => console.error('Error fetching GeoJSON:', error));
  };