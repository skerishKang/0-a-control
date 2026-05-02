# 📘 JavaScript 2단계 – Day 4

## 주제: 동적으로 HTML 요소 생성 및 조작하기

---

## 📗 교과서

### 🧠 학습 목표

* 자바스크립트로 새로운 HTML 요소를 생성하고, 페이지에 추가할 수 있다.
* `createElement`, `appendChild`, `remove()` 등의 메서드를 이해하고 사용할 수 있다.
* 동적으로 생성된 요소에 이벤트를 추가할 수 있다.

---

### 1. 요소 만들기 – `document.createElement()`

```javascript
const newItem = document.createElement("li");
newItem.textContent = "새 항목입니다";
```

* `"li"`는 생성할 태그 이름
* `.textContent`는 그 안에 표시할 텍스트

---

### 2. 요소 추가 – `appendChild()`

```javascript
const list = document.getElementById("todo-list");
list.appendChild(newItem);
```

* 기존 요소(`ul`, `div` 등)에 새로운 자식 요소를 붙임

---

### 3. 요소 삭제 – `.remove()`

```javascript
newItem.remove();
```

또는 부모에서 자식 제거:

```javascript
list.removeChild(newItem);
```

---

### 4. 실습 예제: 간단한 TODO 리스트

#### ✅ HTML 구조

```html
<input id="task-input" placeholder="할 일을 입력하세요" />
<button id="add-btn">추가</button>
<ul id="todo-list"></ul>
```

#### ✅ JavaScript 코드

```javascript
const input = document.getElementById("task-input");
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
```

---

### 5. 실습 과제

1. 할 일 항목을 하나씩 추가해보기
2. 항목을 클릭하면 삭제되도록 만들기
3. `Enter` 키로도 추가되게 해보기 (`keydown` 이벤트)

---

### 💡 팁

* 요소를 만들고 나면 `className`, `style`, `dataset`, `addEventListener` 등도 자유롭게 설정 가능
* 실제 많은 UI가 이런 방식으로 구성됨 (댓글, 알림, 리스트 등)

---

## 🎤 강의 대사 (강사용 스크립트)

> 오늘은 자바스크립트로 **HTML 요소를 직접 만들어서 화면에 추가하고**,
> 필요하면 삭제까지 해보는 걸 배워볼 거예요.
>
> HTML은 원래 정적인 문서지만, 자바스크립트를 쓰면 **동적인 콘텐츠**를 만들 수 있어요.
>
> 자, 시작해봅시다. 먼저 이런 코드가 있어요:

```javascript
const li = document.createElement("li");
li.textContent = "새 항목입니다";
```

> 이건 브라우저 안에서 `<li>새 항목입니다</li>`라는 \*\*요소를 "코드로 만든 것"\*\*이에요.
> 이걸 리스트에 넣으려면 `appendChild()`를 씁니다.

```javascript
list.appendChild(li);
```

> 자, 여기서 질문!
> "이렇게 만든 요소에도 이벤트를 붙일 수 있을까요?"
> 정답은 ✅ 예! 아래처럼요:

```javascript
li.addEventListener("click", () => {
  li.remove(); // 클릭하면 삭제
});
```

> 실제로 많이 쓰이는 방식입니다. 댓글 삭제, 알림 닫기, 목록 지우기 등 전부 이거예요.

---

> 이제 같이 미니 프로젝트처럼 만들어봅시다.
> 여러분만의 To-do 리스트를 만들어볼 거예요.

* 입력창에 텍스트 입력
* "추가" 버튼 누르면 리스트에 `<li>` 항목이 생김
* 그 항목을 클릭하면 삭제됨
* `Enter`로도 추가되게 해봅시다

---

필요하시면 `.html + .js` 실습 템플릿도 만들어드릴게요.
이 내용을 그대로 VSCode에서 바로 실행하거나 CodePen에 붙여서 확인할 수 있어요.
만들어드릴까요?
