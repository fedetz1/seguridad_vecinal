function agregarPeligro(){
    // Obtén todos los botones con la clase "icono-alerta"
    const iconoAlertaButtons = document.querySelectorAll(".icono-alerta");

    // Agrega un evento de clic a cada botón
    iconoAlertaButtons.forEach((button, i) => {
    button.addEventListener("click", () => {
        const camContainer = button.closest(".cam"); // Encuentra el contenedor "cam"
        if(!button.classList.contains("efectopeligro")){
            camContainer.classList.add("efectopeligro"); // Agrega la clase para la animación
            iconoAlertaButtons[i].innerHTML=`<i class="fas fa-times"></i>`
            iconoAlertaButtons[i].style.color="black"
            button.addEventListener("click", () => {
                camContainer.classList.remove("efectopeligro");
                iconoAlertaButtons[i].innerHTML=`<i class="fas fa-exclamation-triangle"></i>`
                iconoAlertaButtons[i].style.color="red"
                agregarPeligro()
            })
        }
    });
    });

}

agregarPeligro()