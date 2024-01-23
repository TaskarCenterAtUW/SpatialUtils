const Steps = ({ onClose = null, routeResult = null }: Props) => {
    let stepsData = routeResult.routes[0].segments.features;
    let stepsDataCombined = [];
  
    let aggregatedLinks = [];
  
    stepsData.map((d, i) => {
      if (i === 0) {
        let featureCopy  = JSON.parse(JSON.stringify(d));
        stepsDataCombined.push(featureCopy);
      }
      else {
        let current = d;
        let last = stepsDataCombined[stepsDataCombined.length-1]
        // Merge crossings
        if (current.properties.highway === "footway"
          && current.properties.footway === "crossing"
          && current.properties.footway === last.properties.footway
          && current.properties.description === last.properties.description) {
            let lastCopy  = JSON.parse(JSON.stringify(last));
            // Check for aggregated links/link corners
            if (aggregatedLinks.length > 0) {
              aggregatedLinks = [];
            }
            // TODO: add the length of aggregated links
            lastCopy.properties.length += current.properties.length;
            stepsDataCombined[stepsDataCombined.length-1] = lastCopy;
        }
        // Skip links and link corners
        else if (current.properties.highway === "footway"
          && current.properties.footway === "sidewalk"
          && (current.properties.street_id === "[Link]" || current.properties.street_id === "[Link Corner]")) {
            // console.log(current)
            aggregatedLinks.push(i);
        }
        else {
          let featureCopy  = JSON.parse(JSON.stringify(d));
          // Check for aggregated links/link corners
          if (aggregatedLinks.length > 0) {
            aggregatedLinks = [];
            // TODO: add the length of aggregated links to featureCopy
          }
          stepsDataCombined.push(featureCopy);
        }
      }
    });
  };
  