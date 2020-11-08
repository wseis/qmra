document.addEventListener('DOMContentLoaded', function() {
    console.log("page loaded")
    el = document.querySelectorAll("[id*='id_treatment_']")
    label =document.querySelectorAll("[for*='id_treatment_']")

    el.forEach(element => {
       
    sel = parseInt(element.value)
    l = document.querySelector(`[for*=${element.id}`)
    const explain = document.createElement('span')
    

    fetch(`/api_treatments/${sel}`)
      .then(response => response.json())
      .then(treatments => {
        // Print emails
        
        element.title = treatments[0].description
        explain.innerHTML=treatments[0].description
        
      });
      
      l.append(explain)
      
      
      explain.style.display="None"
      l.addEventListener('mouseover', function(){
    
        explain.style.display="block"
        explain.style.color="#007c9f"
        explain.style.backgroundColor = "#eff1f4";
        explain.style.backgroundColor = "#eff1f4";
        explain.style.border = "thin solid #007c9f";
        explain.style.borderRadius = "5px";
      })
      l.addEventListener('mouseout', function(){
        explain.style.display="None"
      })


      
    //l.innerHTML = treatments[0].description


  })
    

})

//[title~=flower]
//[id*='someId']