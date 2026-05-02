좋습니다! 이제 JavaScript 2단계 **Day 3: 입력값 다루기** 수업 내용을 정리해드릴게요.
아래는 마찬가지로 **교과서 + 강의 대사** 구성이며, 실습 위주로 설계했습니다.

---

# 📘 JavaScript 2단계 – Day 3

## 주제: 폼 입력값 다루기 (input, value, 출력 연결)

---

## 📗 교과서

### 🧠 학습 목표

* 사용자가 입력한 값을 자바스크립트로 받아올 수 있다.
* 입력값을 처리하여 화면에 출력하거나 반응할 수 있다.
* `input.value`의 사용법과 실습을 익힌다.

---

### 1. HTML 입력요소 (input, form)

HTML에서는 사용자의 입력을 받을 수 있는 다양한 요소를 제공함:

```html
<input type="text" id="name-input" />
<button id="submit-btn">제출</button>
<p id="result"></p>
```

---

### 2. 자바스크립트로 입력값 가져오기

`value` 속성을 이용하면 사용자가 입력한 값을 가져올 수 있음:

```javascript
const input = document.getElementById("name-input");
console.log(input.value);  // 사용자가 입력한 텍스트 출력
```

---

### 3. 입력값을 화면에 출력하기 (실습 예제)

```javascript
const input = document.getElementById("name-input");
const btn = document.getElementById("submit-btn");
const result = document.getElementById("result");

btn.addEventListener("click", () => {
  const name = input.value;
  result.textContent = `${name}님, 반가워요!`;
});
```

* `input.value`: 입력한 텍스트 값
* `textContent`: 해당 요소의 텍스트를 변경

---

### 4. 실습 과제

1. 이름 입력 후 버튼 누르면 “○○님, 환영합니다” 출력
2. 아무 것도 입력하지 않으면 “이름을 입력해주세요” 알림 띄우기
3. `Enter` 키로도 제출할 수 있도록 하기 (`keydown` + `Enter`)

---

### 💡 팁

* `.value`는 input, textarea 같은 **폼 요소에서만 사용 가능**
* 숫자 입력은 `.value`로 받아오면 문자열이므로 `Number()`로 형변환 필요
* 이벤트 안에서 `.value`를 읽어야 최신 값이 반영됨

---

## 🎤 강의 대사 (강사용 스크립트)

> 오늘은 사용자가 입력한 **값을 읽어오는 방법**을 배워볼게요.
>
> 여러분이 HTML에서 `<input>`을 만들면, 그 안에 사용자가 직접 텍스트를 입력할 수 있죠.
> 하지만 그걸 **자바스크립트에서 읽어오려면**, `value`라는 속성을 사용해야 해요.
>
> 예를 들어 이런 코드가 있다고 칠게요:

```html
<input id="name-input" />
<button id="submit-btn">제출</button>
<p id="result"></p>
```

```javascript
const input = document.getElementById("name-input");
console.log(input.value);
```

> 이 코드는 사용자가 입력한 값을 콘솔에 출력해줍니다.
> 실습해볼까요?
>
> 버튼을 눌렀을 때 아래 텍스트를 바꿔봅시다.
> 입력한 이름을 읽어서 “홍길동님, 반가워요!”처럼 보여주면 됩니다.

---

> 여기서 중요한 점 하나 더!
> 여러분이 `input.value`를 **이벤트 바깥에서** 미리 읽으면 안 돼요.
> 왜냐면 이벤트가 발생하기 전에는 사용자가 입력을 안 했을 수도 있으니까요.
> 항상 `click`이나 `keydown` 이벤트 **안에서** 읽어야 해요.

---

> 자, 이번에는 조건문도 넣어볼게요.
> 사용자가 아무 것도 안 썼다면 `alert("이름을 입력해주세요!")`처럼 경고를 띄우게 해봅시다.

---

> 마지막 미션!
> 버튼 클릭 말고 **엔터 키로도 제출이 되도록 만들어볼까요?**
> `input`에 `keydown` 이벤트를 추가해서, `e.key === "Enter"`일 때 실행해보세요.

---

원하시면 이 내용 기반으로 `.html`과 `.js` 실습 템플릿도 만들어드릴 수 있어요.
다음 단계인 \*\*Day 4 (동적으로 요소 추가)\*\*도 준비해드릴까요?
