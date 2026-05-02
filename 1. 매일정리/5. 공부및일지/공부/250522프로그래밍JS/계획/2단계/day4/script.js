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

const taskInput = document.getElementById("task-input");
const addBtn = document.getElementById("add-btn");
const list = document.getElementById("todo-list");

addBtn.addEventListener("click", () => {
  const task = input.value.trim();
  
  if (task === "") return;

  const li = document.createElement("li");
  li.textContent = task;

  // 클릭하면 삭제되게 만들기
  li.addEventListener("click", () => {
    li.remove();
  });

  list.appendChild(li);
  input.value = ""; // 입력창 초기화
});
