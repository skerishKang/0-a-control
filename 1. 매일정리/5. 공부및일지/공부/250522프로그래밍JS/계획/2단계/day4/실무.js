// 요소 가져오기
const input = document.getElementById("task-input");
const addBtn = document.getElementById("add-btn");
const list = document.getElementById("todo-list");

// 1. 할 일 항목 만들기
function createTaskItem(text) {
  const li = document.createElement("li");
  li.textContent = text;
  bindDeleteEvent(li);
  return li;
}

// 2. 삭제 이벤트 연결
function bindDeleteEvent(item) {
  item.addEventListener("click", () => {
    item.remove();
  });
}

// 3. 입력창 초기화
function clearInput() {
  input.value = "";
}

// 4. 버튼 클릭 시 실행될 전체 흐름
function handleAddTask() {
  const task = input.value.trim();
  if (!task) return;

  const newItem = createTaskItem(task);
  list.appendChild(newItem);
  clearInput();
}

// 5. 이벤트 연결
addBtn.addEventListener("click", handleAddTask);
