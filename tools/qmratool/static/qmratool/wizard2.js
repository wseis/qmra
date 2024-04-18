document.addEventListener('DOMContentLoaded', function() {
  const tooltipConfig = {
      fontColor: "black",
      bgColor: "#DCDCFB",
      borderRadius: "5px",
      padding: "20px"
  };

  setupTooltips('2-treatment', '/api_treatments/');
  setupTooltips('1-source', '/api_sources/');
  setupTooltips('3-exposure', '/api_exposures/');

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
      } else {
          return `<strong>${titleCaseDataName}</strong><br>${data.description}`;
      }
  }
});
