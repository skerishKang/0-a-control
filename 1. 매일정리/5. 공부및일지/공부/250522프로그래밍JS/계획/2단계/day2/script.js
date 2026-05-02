const title = document.getElementById('main-title');
title.innerHTML = '제목변경됨!';
title.style.color = 'blue';
title.style.fontSize = '20emx';


const btn = document.getElementById("change-btn");
const msg = document.getElementById("message");

btn.addEventListener("click", () => {
  msg.textContent = "버튼이 클릭됐어요!";
});