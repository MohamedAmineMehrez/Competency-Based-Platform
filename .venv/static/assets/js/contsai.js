const name= document.getElementById("username")

const error= document.getElementById("error")
        const form= document.getElementById("form")
        const error_name= document.getElementById("error_name")
  


        
        
        function check(){
        form.addEventListener('submit',(e) =>{
            
          let messages = []
          //nom
          if (name.value ===""){
            messages.push('Ce champ est vide')
            error_name.innerHTML = 'Ce champ est vide'
            
          }
            else if(name.value.length <=2 && name.value.length >=1 ){
              messages.push('Le nom doit contenir au moins 3 caracteres.')
              error_name.innerHTML = 'Le nom doit contenir au moins 3 caracteres.'
            }
            
            else if (isNaN(name.value)==false){
              messages.push('Ce nom est invalid')
              error_name.innerHTML = 'Ce nom est invalid'
            }
           

            
            if(messages.length >0){
              e.preventDefault()
              error.Element.innerText =messages.join(', ')
            }

          
        })
      }