document.addEventListener('DOMContentLoaded', function(){
    description = document.getElementById('Description')
    description.innerHTML = "Description"
    description.style.fontWeight="bold"
    description.style.fontFamily="-apple-system,BlinkMacSystemFont,Arial,sans-serif"

    source = document.getElementById('Source')
    source.innerHTML = "Source"
    source.style.fontWeight="bold"
    source.style.fontFamily="-apple-system,BlinkMacSystemFont,Arial,sans-serif"

    Treatment = document.getElementById('Treatment')
    Treatment.innerHTML = "Treatment"
    Treatment.style.fontWeight="bold"
    Treatment.style.fontFamily="-apple-system,BlinkMacSystemFont,Arial,sans-serif"

    Exposure = document.getElementById('Exposure')
    Exposure.innerHTML = "Exposure"
    Exposure.style.fontWeight="bold"
    Exposure.style.fontFamily="-apple-system,BlinkMacSystemFont,Arial,sans-serif"


    current = document.getElementById('form').dataset.step
    console.log(current)
    steps = 4


   let progressBar = document.querySelector('.progress-bar');
   progressBar.classList.remove('bg-success', 'bg-primary','bg-info', 'bg-warning', 'bg-danger'); // Remove potential Bootstrap background classes
    
    function setProgressBar(curStep){
       let percent = parseFloat(100 / steps) * curStep;
       console.log(percent)
       percent = percent.toFixed();
       document.querySelector(".progress-bar").style.width = percent + "%";
       console.log(document.querySelector(".progress-bar").style.width)
       
       document.querySelector(".progress-bar").style.backgroudColor = '#673AB7 !important;'
       console.log(document.querySelector(".progress-bar").style.backgroudColor)
   }
   setProgressBar(current)

 })