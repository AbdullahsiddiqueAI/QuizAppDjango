let toggleBtn = document.getElementById('toggle-btn');
let body = document.body;
let darkMode = localStorage.getItem('dark-mode');

const enableDarkMode = () =>{
   toggleBtn.classList.replace('fa-sun', 'fa-moon');
   body.classList.add('dark');
   localStorage.setItem('dark-mode', 'enabled');
}

const disableDarkMode = () =>{
   toggleBtn.classList.replace('fa-moon', 'fa-sun');
   body.classList.remove('dark');
   localStorage.setItem('dark-mode', 'disabled');
}

if(darkMode === 'enabled'){
   enableDarkMode();
}

toggleBtn.onclick = (e) =>{
   darkMode = localStorage.getItem('dark-mode');
   if(darkMode === 'disabled'){
      enableDarkMode();
   }else{
      disableDarkMode();
   }
}

let profile = document.querySelector('.header .flex .profile');

document.querySelector('#user-btn').onclick = () =>{
   profile.classList.toggle('active');
   search.classList.remove('active');
}

let search = document.querySelector('.header .flex .search-form');

document.querySelector('#search-btn').onclick = () =>{
   search.classList.toggle('active');
   profile.classList.remove('active');
}

let sideBar = document.querySelector('.side-bar');

document.querySelector('#menu-btn').onclick = () =>{
   sideBar.classList.toggle('active');
   body.classList.toggle('active');
}

document.querySelector('#close-btn').onclick = () =>{
   sideBar.classList.remove('active');
   body.classList.remove('active');
}

window.onscroll = () =>{
   profile.classList.remove('active');
   search.classList.remove('active');

   if(window.innerWidth < 1200){
      sideBar.classList.remove('active');
      body.classList.remove('active');
   }
}





// Optional fade-out effect for messages
document.querySelectorAll('.close-btn').forEach(button => {
   button.onclick = function() {
       const message = this.parentElement;
       message.style.opacity = '0';
       setTimeout(() => message.style.display = 'none', 300); // Adjust the timeout duration as needed
   };
});

function submitQuiz(quizId,csrf_token) {
   const answers = {};
   
   document.querySelectorAll(".quiz-question").forEach(question => {
       const questionId = question.querySelector("input[type='radio']").name.replace("question", "");
       const selectedOption = question.querySelector("input[type='radio']:checked");
       answers[questionId] = selectedOption ? selectedOption.value : null;
   });

   fetch("/check_answers/", {
       method: "POST",
       headers: {
           "Content-Type": "application/json",
           "X-CSRFToken": `${ csrf_token }`
       },
       body: JSON.stringify({ quiz_id: quizId, answers: answers })
   })
   .then(response => response.json())
   .then(data => {
       const resultDiv = document.getElementById("result");
       resultDiv.style.display = "block";
       resultDiv.innerHTML = `Score: ${data.score}% - ${data.passed ? "Passed" : "Failed"}`;
       
       data.results.forEach(result => {
           resultDiv.innerHTML += `<p>${result.question} - ${result.is_correct ? "Correct" : "Incorrect"}</p>`;
       });
   })
   .catch(error => console.error("Error:", error));
}

