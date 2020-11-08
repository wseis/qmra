document.addEventListener('DOMContentLoaded', function() {
    console.log("page loaded")
    el = document.querySelectorAll("[id*='id_treatment_']")
    label =document.querySelectorAll("[for*='id_treatment_']")

    el.forEach(element => {    
    sel = parseInt(element.value)
    fetch(`/api_treatments/${sel}`)
      .then(response => response.json())
      .then(treatments => {
        // Print emails
        element.setAttribute("data-toggle","tooltip") 
        element.title = treatments[0].description
})




    });
  
})

//[title~=flower]
//[id*='someId']