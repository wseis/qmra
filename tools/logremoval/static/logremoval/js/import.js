document.addEventListener('DOMContentLoaded', function() {
    
    function getFilename(fullPath) {
        return fullPath.replace(/^.*[\\\/]/, '');
      }
    
    inputlabel = document.querySelector('.custom-file-label')
    inputform = document.querySelector('#file_id')
    
    inputform.addEventListener('change', function(){
        inputlabel.innerHTML = getFilename(inputform.value)

    })

})
