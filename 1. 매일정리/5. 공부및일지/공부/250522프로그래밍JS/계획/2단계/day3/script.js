const title = document.getElementById('main-title');
title.innerHTML = '제목변경됨!';
title.style.color = 'blue';
title.style.fontSize = '20emx';


const btn = document.getElementById("change-btn");
const msg = document.getElementById("message");
const input = document.getElementById("name-input");
const result = document.getElementById("result");

btn.addEventListener("click", () => {
  msg.textContent = "버튼이 클릭됐어요!";
});

btn.addEventListener("click", () => {
  const name = input.value;
  result.textContent = `${name}님, 반가워요!`;
});