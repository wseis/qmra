document.addEventListener('DOMContentLoaded', function(){
    description = document.getElementById('step_1')
    description.innerHTML = "Description"
    description.style.fontWeight="bold"
    description.style.fontFamily="-apple-system,BlinkMacSystemFont,Arial,sans-serif"

    source = document.getElementById('step_2')
    source.innerHTML = "Source"
    source.style.fontWeight="bold"
    source.style.fontFamily="-apple-system,BlinkMacSystemFont,Arial,sans-serif"

    Treatment = document.getElementById('step_3')
    Treatment.innerHTML = "Treatment"
    Treatment.style.fontWeight="bold"
    Treatment.style.fontFamily="-apple-system,BlinkMacSystemFont,Arial,sans-serif"

    Exposure = document.getElementById('step_4')
    Exposure.innerHTML = "Exposure"
    Exposure.style.fontWeight="bold"
    Exposure.style.fontFamily="-apple-system,BlinkMacSystemFont,Arial,sans-serif"


    current = description.id.split('_')[1]
    console.log(current)
    steps = 4


   let progressBar = document.querySelector('.progress-bar');
   progressBar.classList.remove('bg-success', 'bg-primary','bg-info', 'bg-warning', 'bg-danger'); // Remove potential Bootstrap background classes
    console.log(steps)
    function setProgressBar(curStep){
       let percent = parseFloat(100 / steps) * curStep;
       percent = percent.toFixed();
       document.querySelector(".progress-bar").style.width = percent + "%";
       
       document.querySelector(".progress-bar").style.backgroudColor = '#673AB7 !important;'
       console.log(document.querySelector(".progress-bar").style.backgroudColor)
   }
   setProgressBar(current)

 })