document.addEventListener('DOMContentLoaded', function() {
  const tooltipConfig = {
      fontColor: "black",
      bgColor: "#DCDCFB",
      borderRadius: "5px",
      padding: "20px"
  };

  setupTooltips('treatment', '/api_treatments/');
  setupTooltips('source', '/api_sources/');
  setupTooltips('exposure', '/api_exposures/');

  function setupTooltips(fieldName, apiUrl) {
      const elements = document.querySelectorAll(`[id*='id_${fieldName}_']`);
      elements.forEach(element => {
          const label = document.querySelector(`[for='${element.id}']`);
          const tooltip = document.createElement('span');
          tooltip.style.display = "none";
          applyStyles(tooltip, tooltipConfig);
          label.append(tooltip);

          let tooltipTimeout;  // Define a variable to hold the timeout

          label.addEventListener('mouseover', () => {
              // Set timeout to delay tooltip display
              tooltipTimeout = setTimeout(() => {
                  fetchAndDisplayTooltip(element, apiUrl, tooltip, fieldName);
              }, 150); // 700 milliseconds delay
          });

          label.addEventListener('mouseout', () => {
              // Clear the timeout if mouse leaves before the tooltip is displayed
              clearTimeout(tooltipTimeout);
              hideTooltip(tooltip);
          });
      });
  }

  function fetchAndDisplayTooltip(element, apiUrl, tooltip, fieldName) {
      if (!tooltip.innerHTML) { // Fetch only if tooltip is empty
          fetch(`${apiUrl}${element.value}`)
              .then(response => response.json())
              .then(data => {
                  tooltip.innerHTML = formatTooltipContent(data[0], fieldName);
                  tooltip.style.display = "block";  // Display the tooltip only after fetching
              });
      } else {
          tooltip.style.display = "block";  // Display the tooltip if already fetched
      }
  }

  function hideTooltip(tooltip) {
      tooltip.style.display = "none";
  }

  function applyStyles(tooltip, config) {
      tooltip.style.position = 'absolute';
      tooltip.style.top = '0';
      tooltip.style.left = "50px";  // Adjusted to place the tooltip to the right of the element
      tooltip.style.color = config.fontColor;
      tooltip.style.backgroundColor = config.bgColor;
      tooltip.style.borderRadius = config.borderRadius;
      tooltip.style.padding = config.padding;
      tooltip.style.zIndex = '1000';  // Ensure tooltip is above other elements
  }

  function toTitleCase(str) {
    return str.toLowerCase().split(' ').map(function(word) {
        return word.charAt(0).toUpperCase() + word.slice(1);
    }).join(' ');
}

  function formatTooltipContent(data, fieldName) {

      let titleCaseDataName = toTitleCase(data.name);
      // Customize content based on the field
      if (fieldName === 'exposure') {
          return `<strong>${titleCaseDataName}</strong><br>${data.description}<br>Events per year [N]: <strong>${data.events_per_year}</strong><br>Volume per event [L]: <strong>${data.volume_per_event}</strong>`;
      } else if (fieldName === 'treatment') { 
        return `<strong>${titleCaseDataName}</strong><br>${data.description}<br>
        <table class="table table-bordered mt-3">
        <thead class="custom-header">
            <tr>
                <th>Pathogen Group</th>
                <th>Minimum LRV</th>
                <th>Maximum LRV</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Viruses</td>
                <td>${data.virus_min}</td>
                <td>${data.virus_max}</td>
            </tr>
            <tr>
                <td>Bacteria</td>
                <td>${data.bacteria_min}</td>
                <td>${data.bacteria_max}</td>
            </tr>
            <tr>
                <td>Protozoa</td>
                <td>${data.protozoa_min}</td>
                <td>${data.protozoa_min}</td>
            </tr>
         
        </tbody>
    </table>`
        
        }
      else {
          return `<strong>${titleCaseDataName}</strong><br>${data.description}`;
      }
  }
});
