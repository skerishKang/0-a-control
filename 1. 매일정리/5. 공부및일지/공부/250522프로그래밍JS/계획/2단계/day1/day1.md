# 📘 JavaScript 2단계 – Day 1

## 주제: DOM(Document Object Model) 이해하기

---

## 📗 교과서

### 🧠 학습 목표

* DOM이 무엇인지 이해한다.
* 자바스크립트로 HTML 요소를 선택하고 조작할 수 있다.
* 기본적인 스타일 변경 및 텍스트 수정 기능을 익힌다.

---

### 1. DOM이란?

**DOM(Document Object Model)** 은 웹페이지의 구조를 자바스크립트가 이해하고 조작할 수 있도록 객체(Object) 형태로 표현한 것이다.

```html
<!-- 예시 HTML -->
<h1 id="main-title">안녕하세요</h1>
```

위 HTML은 자바스크립트에서 다음처럼 다룰 수 있다:

```javascript
const title = document.getElementById("main-title");
title.innerText = "반가워요!";
```

* `document`: 현재 웹 문서 전체
* `getElementById`: 특정 ID를 가진 요소를 가져옴
* `innerText`: 요소의 안쪽 텍스트를 가져오거나 바꿈

---

### 2. DOM 선택 방법

| 메서드                               | 설명                      |
| --------------------------------- | ----------------------- |
| `getElementById("id")`            | ID로 요소 선택               |
| `getElementsByClassName("class")` | 클래스명으로 요소 리스트 선택        |
| `getElementsByTagName("tag")`     | 태그명으로 요소 리스트 선택         |
| `querySelector("선택자")`            | CSS 선택자 문법으로 첫 번째 요소 선택 |
| `querySelectorAll("선택자")`         | CSS 선택자 문법으로 모든 요소 선택   |

> 📌 `querySelector`는 매우 자주 사용되며, CSS 선택자 문법 그대로 활용할 수 있어 유용하다.

---

### 3. DOM 조작 예시

```javascript
const title = document.querySelector("#main-title");
title.innerText = "제목 변경됨!";
title.style.color = "blue";
title.style.fontSize = "2em";
```

---

### 4. 실습 과제

🔧 **\[실습 1] 제목 바꾸기**

1. HTML 파일에 `<h1 id="main-title">안녕하세요</h1>` 추가
2. 자바스크립트로 해당 요소 선택
3. 텍스트와 색상을 변경해보기

---

### 💡 팁

* 웹 브라우저에서 `F12`를 눌러 **개발자 도구**를 열고 `Console`에서 코드를 실습해볼 수 있음
* `style` 속성을 통해 글자 크기, 색상 등을 직접 바꿀 수 있음

---

## 🎤 강의 대사 (강사용 스크립트)

> 안녕하세요, 오늘은 자바스크립트로 HTML을 조작하는 방법, \*\*DOM(Document Object Model)\*\*을 배워보겠습니다.
>
> DOM은 웹페이지를 자바스크립트가 이해할 수 있도록 만든 구조입니다. 우리가 보는 웹페이지는 사실 브라우저 안에서 \*\*문서 객체(=Object)\*\*로 바뀌어서 처리되고 있어요.
>
> 먼저 DOM에서 가장 중요한 건 **요소를 선택하는 방법**이에요. 예를 들어 `getElementById("main-title")`은 ID가 `main-title`인 요소를 가져오죠.
>
> 자, 실습해볼게요. 브라우저 콘솔창 열고, 아래 코드를 입력해 보세요.

```javascript
const title = document.getElementById("main-title");
title.innerText = "자바스크립트로 바꿨어요!";
```

> 잘 되셨죠? 그리고 이렇게 스타일도 바꿀 수 있습니다:

```javascript
title.style.color = "green";
title.style.fontSize = "2em";
```

> DOM 조작은 앞으로의 모든 웹 프로그래밍의 기초가 됩니다.
> 꼭 직접 타이핑하면서 눈으로 결과를 확인해보세요.
> 다음 시간에는 이 HTML 요소에 **이벤트를 연결해서** 상호작용하게 만들어볼 거예요.

---

