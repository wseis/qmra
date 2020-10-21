document.addEventListener('DOMContentLoaded', function() {
    console.log("hello")
    
    document.querySelector('#source_info').style.display= "none"
    document.querySelector('#treatment_info').style.display="none"
    document.querySelector('#exposure_info').style.display="none"
    document.querySelector("#to_source_water").onclick=()=>{
        document.querySelector('#basic_info').style.display= "none"
        document.querySelector('#source_info').style.display= "block"
        document.querySelector('#treatment_info').style.display="none"
        document.querySelector('#exposure_info').style.display="none"
            
    }
})