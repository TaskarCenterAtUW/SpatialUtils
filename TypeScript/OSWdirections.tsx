import mapboxgl from "mapbox-gl";

const getLength = (geometry, i, j) : number => {
    let totalLength = 0;
    for (let z = i; z < j; z++) {
      var x1 = geometry.coordinates[Math.min(Math.max(z, 0), geometry.coordinates.length-1)][0];
      var y1 = geometry.coordinates[Math.min(Math.max(z, 0), geometry.coordinates.length-1)][1];
      var x2 = geometry.coordinates[Math.min(Math.max(z+1, 0), geometry.coordinates.length-1)][0];
      var y2 = geometry.coordinates[Math.min(Math.max(z+1, 0), geometry.coordinates.length-1)][1];
  
      totalLength += (new mapboxgl.LngLat(x1, y1)).distanceTo(new mapboxgl.LngLat(x2, y2))
    }
    return totalLength;
  }
  
  // Converts from degrees to radians.
  const toRadians = (degrees) : number => {
    return degrees * Math.PI / 180;
  };
  
  // Converts from radians to degrees.
  const toDegrees = (radians) : number => {
    return radians * 180 / Math.PI;
  }
  
  const angleFromCoordinate = (long1: number, lat1: number, long2: number, lat2: number) : number => {
    long1 = toRadians(long1);
    lat1 = toRadians(lat1);
    long2 = toRadians(long2);
    lat2 = toRadians(lat2);
    const dLon = (long2 - long1);
  
    const y = Math.sin(dLon) * Math.cos(lat2);
    const x = Math.cos(lat1) * Math.sin(lat2) - Math.sin(lat1)
          * Math.cos(lat2) * Math.cos(dLon);
  
    let brng = Math.atan2(y, x);
  
    brng = toDegrees(brng);
  
    return brng;
  }
  
  const getDirection = (geometry1, geometry2) : string => {
    let instruction = ""
    if (geometry1 && geometry2) {
  
      let i = Math.max(0, geometry1.coordinates.length-2);
      while (i >= 0 && getLength(geometry1, i, geometry1.coordinates.length-1) < 6) {
        i = i - 1
      }
  
      let j = Math.min(1, geometry2.coordinates.length-1);
      while (j <= geometry2.coordinates.length-1 && getLength(geometry2, 0, j) < 6) {
        j = j + 1
      }
      let bearing1 = angleFromCoordinate(geometry1.coordinates[Math.max(0, i)][0],geometry1.coordinates[Math.max(0, i)][1],
                      geometry1.coordinates[geometry1.coordinates.length-1][0],geometry1.coordinates[geometry1.coordinates.length-1][1])
      
      let bearing2 = angleFromCoordinate(geometry2.coordinates[0][0],geometry2.coordinates[0][1],
                  geometry2.coordinates[Math.min(j, geometry2.coordinates.length-1)][0],geometry2.coordinates[Math.min(j, geometry2.coordinates.length-1)][1])
  
      let angle = ((((bearing1 - bearing2) % 360) + 540) % 360) - 180
    
      if (angle >= 67.5 && angle <= 112.5) {
        instruction = "Turn left"
      }
      else if (angle >= -112.5 && angle <= -67.5){
        instruction = "Turn right"
      }
      else if (angle >= -22.5 && angle <= 22.5){
        instruction = "Continue straight"
      }
      else if (angle >= 22.5 && angle <= 67.5){
        instruction = "Slight left"
      }
      else if (angle >= -67.5 && angle <= -22.5){
        instruction = "Slight right"
      }
      else if (angle >= 112.5){
        instruction = "Sharp left"
      }
      else if (angle <= -112.5){
        instruction = "Sharp right"
      }
  
      instruction += " and "
    }
    return instruction
  }
  