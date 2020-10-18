document.addEventListener('DOMContentLoaded', function() {
    console.log("page loaded")
    ex =document.querySelector("#explain-text")
    ex.style.display="none"

    el = document.querySelector("#form-id")
    el.addEventListener('mouseover', function(){
        ex.style.display="block"
      })
      el.addEventListener('mouseout', function(){
        ex.style.display="none"
      })
})