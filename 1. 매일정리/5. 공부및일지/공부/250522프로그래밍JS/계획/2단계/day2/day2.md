# 📘 JavaScript 2단계 – Day 2

## 주제: 사용자 이벤트 다루기 (click, mouseover 등)

---

## 📗 교과서

### 🧠 학습 목표

* 브라우저에서 발생하는 이벤트의 개념을 이해한다.
* `addEventListener()`를 사용하여 다양한 이벤트를 처리할 수 있다.
* 버튼 클릭, 마우스 오버, 키보드 입력 등의 이벤트를 실습해본다.

---

### 1. 이벤트(Event)란?

**이벤트**는 사용자가 웹페이지와 상호작용할 때 발생하는 신호입니다. 예를 들면:

* 버튼을 클릭함
* 마우스를 올림
* 키보드를 입력함
* 화면을 스크롤함

이러한 이벤트가 발생하면 **자바스크립트로 그에 맞는 반응(함수)을 실행**할 수 있습니다.

---

### 2. 이벤트 연결 방법

#### ✅ 1) HTML 속성 방식 (비추)

```html
<button onclick="sayHello()">인사하기</button>

<script>
  function sayHello() {
    alert("안녕하세요!");
  }
</script>
```

> 단점: HTML과 JS가 섞여 관리가 불편함

---

#### ✅ 2) `addEventListener()` 방식 (추천)

```html
<button id="hello-btn">인사하기</button>

<script>
  const button = document.getElementById("hello-btn");
  button.addEventListener("click", () => {
    alert("안녕하세요!");
  });
</script>
```

> 장점: JS에서 모든 이벤트 제어 가능. 구조가 깔끔함

---

### 3. 주요 이벤트 종류

| 이벤트 이름      | 설명             |
| ----------- | -------------- |
| `click`     | 요소를 클릭했을 때     |
| `mouseover` | 마우스를 올렸을 때     |
| `mouseout`  | 마우스가 벗어났을 때    |
| `keydown`   | 키보드를 눌렀을 때     |
| `submit`    | 폼(form)이 제출될 때 |

---

### 4. 실습: 버튼 클릭 시 텍스트 바꾸기

**HTML**

```html
<h2 id="message">아직 클릭 안 했어요</h2>
<button id="change-btn">눌러보세요</button>
```

**JavaScript**

```javascript
const btn = document.getElementById("change-btn");
const msg = document.getElementById("message");

btn.addEventListener("click", () => {
  msg.textContent = "버튼이 클릭됐어요!";
});
```

---

### 🧪 실습 과제

1. 버튼 클릭 시 텍스트 바꾸기
2. 마우스를 버튼 위에 올렸을 때 색 바꾸기
3. 키보드 입력 감지해서 콘솔에 찍기

---

### 💡 팁

* 하나의 요소에 여러 이벤트를 연결할 수 있어요.
* 익명 함수(화살표 함수)를 자주 씁니다: `() => { ... }`
* `e.target`을 사용하면 이벤트가 일어난 요소를 알 수 있어요.

---

## 🎤 강의 대사 (강사용 스크립트)

> 안녕하세요, 오늘은 웹페이지에서 사용자의 행동에 따라 반응하게 만드는 \*\*이벤트(Event)\*\*를 배워보겠습니다.
>
> 우리가 웹을 사용할 때 가장 많이 하는 게 뭘까요? 클릭하고, 타이핑하고, 마우스를 움직이는 일이죠. 자바스크립트는 이런 동작들을 **이벤트로 감지하고 처리**할 수 있어요.
>
> 먼저 예제를 하나 볼게요. 아래처럼 버튼을 하나 만들고, 누르면 텍스트가 바뀌는 코드를 작성해볼게요:

```javascript
const btn = document.getElementById("change-btn");
btn.addEventListener("click", () => {
  alert("버튼이 클릭됐습니다!");
});
```

> 여기서 중요한 건 `addEventListener()`입니다. 이건 말 그대로 "이벤트가 발생했을 때 듣고 있다가, 어떤 일을 하겠다"는 뜻이에요.

> 이제 실습을 해볼게요. 버튼을 클릭했을 때 메시지를 바꾸고, 마우스를 올렸을 때 색을 바꿔보고, 키보드 입력도 감지해봅시다.

> 여러분이 만들 웹페이지는 결국 사용자와의 대화입니다. 그 대화를 주고받기 위한 핵심이 바로 이벤트입니다.

---

필요하시다면 해당 내용을 `.html` + `.js` 실습 템플릿으로도 제공해드릴 수 있어요.
다음 날(Day 3: 입력값 다루기)도 계속 만들어드릴까요?
