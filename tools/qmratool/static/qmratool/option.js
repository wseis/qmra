document.addEventListener('DOMContentLoaded', function() {
    console.log("page loaded")

    fontcolor = "white"
    bgcolor = "#8081F1"
    border = "#8081F1"

    el = document.querySelectorAll("[id*='id_treatment_']")
//    label =document.querySelectorAll("[for*='id_treatment_']")
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
        explain.style.color=fontcolor;
        //explain.style.backgroundColor = "#eff1f4";
        explain.style.backgroundColor = bgcolor;
        //explain.style.border = "thin solid #0003e2";
        explain.style.borderRadius = "5px";
        explain.style.padding = "20px";
      })
      l.addEventListener('mouseout', function(){
        explain.style.display="None"
      })
    })

      
    //l.innerHTML = treatments[0].description
    source = document.querySelectorAll("[id*='id_source_']")
//    label =document.querySelectorAll("[for*='id_treatment_']")
    source.forEach(element => {
    sel = parseInt(element.value)
    l = document.querySelector(`[for*=${element.id}`)
    const explain = document.createElement('span')
    fetch(`/api_sources/${sel}`)
      .then(response => response.json())
      .then(sources => {
        // Print emails
        
        element.title = sources[0].description
        explain.innerHTML=sources[0].description
        
      });
      
      l.append(explain)
      explain.style.display="None"
      l.addEventListener('mouseover', function(){
    
        explain.style.display="block"
        explain.style.color=fontcolor;
        //explain.style.backgroundColor = "#eff1f4";
        explain.style.backgroundColor = bgcolor;
        //explain.style.border = "thin solid #0003e2";
        explain.style.borderRadius = "5px";
        explain.style.padding = "20px";
      })
      l.addEventListener('mouseout', function(){
        explain.style.display="None"
      })
    })

 //l.innerHTML = treatments[0].description
 exposure = document.querySelectorAll("[id*='id_exposure_']")
 //    label =document.querySelectorAll("[for*='id_treatment_']")
 console.log(exposure)
    exposure.forEach(element => {
     sel = parseInt(element.value)
     l = document.querySelector(`[for*=${element.id}`)
     const explain = document.createElement('span')
     fetch(`/api_exposures/${sel}`)
       .then(response => response.json())
       .then(exposure => {
         // Print emails
         
         element.title = exposure[0].description
         text= [exposure[0].description, '<br>' ,
         'Events per year [N]):', "<strong>",exposure[0].events_per_year,"</strong>", '<br>' ,
         'Volume per exposure event [L]:', "<strong>", exposure[0].volume_per_event],"</strong>";
         
         explain.innerHTML= text.join(' ') 
       });
       
       l.append(explain)
       explain.style.display="None"
       l.addEventListener('mouseover', function(){
     
         explain.style.display="block"
         explain.style.color=fontcolor
         explain.style.backgroundColor = bgcolor;
         //explain.style.border = "thin solid #0003e2";
         explain.style.borderRadius = "5px";
         explain.style.padding = "20px";
       })
       l.addEventListener('mouseout', function(){
         explain.style.display="None"
       })
     })




 
    

})

//[title~=flower]
//[id*='someId']