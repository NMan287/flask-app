document.getElementById("filetype").onclick = () => {
    document.getElementById("fileInput").click(); // acts as custom file input
}
const submit_btn = document.getElementById("submitBtn");

var input = document.getElementById("wordProb")
input.addEventListener("keypress", function(event){
    if (event.key == "Enter"){ // detects when enter key is pressed
        event.preventDefault();
        if (input.value.trim().length == 0){
            console.log("Error")  
        }
        else{
        submit_btn.click(); // clicks a button and directs to answer page
    }}
})

document.getElementById("fileInput").onchange = function(){ 
    console.log("Received")
    const file = this.files[0]; // allows image to be previewed
    const preview_img = document.getElementById("imgPreview");
    preview_img.src = URL.createObjectURL(file);
    preview_img.style.display = "block";
    submit_btn.style.display = "block" 
} 


submit_btn.onclick = function(){
    const text_prompt = document.getElementById("wordProb").value.trim(); // represents worded problem
    const image_prompt = document.getElementById("fileInput").files[0]; // represents the image inputtedd
    if (text_prompt.length > 0){
        localStorage.setItem("TextInput", text_prompt); // so it can be accessed in other js files
        sessionStorage.setItem("question", text_prompt);
    }

    if(image_prompt){
        const reader = new FileReader(); // allows image to be read and stored
        reader.onload = function(e){
            localStorage.setItem("imageInput", e.target.result);
            sessionStorage.setItem("image", e.target.result);
            window.location.href = "/answer"; // takes user to answer page
        }
        reader.readAsDataURL(image_prompt); // so it can be accessed in other js files
        return;
    }

    window.location.href = "/answer"; // if no image inputted takes user to answer page
}