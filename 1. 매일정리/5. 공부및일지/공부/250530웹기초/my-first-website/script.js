// === 1. 계산기 기능 ===
function calculate() {
    // 입력값 가져오기
    const num1 = parseFloat(document.getElementById('num1').value);
    const num2 = parseFloat(document.getElementById('num2').value);
    const resultDiv = document.getElementById('result');
    
    // 입력값 검증
    if (isNaN(num1) || isNaN(num2)) {
        resultDiv.innerHTML = '❌ 숫자를 입력해주세요!';
        resultDiv.style.background = '#f8d7da';
        resultDiv.style.color = '#721c24';
        return;
    }
    
    // 계산 수행
    const sum = num1 + num2;
    const difference = num1 - num2;
    const product = num1 * num2;
    const quotient = num2 !== 0 ? (num1 / num2).toFixed(2) : '무한대';
    
    // 결과 표시
    resultDiv.innerHTML = `
        <strong>📊 계산 결과</strong><br>
        ➕ ${num1} + ${num2} = ${sum}<br>
        ➖ ${num1} - ${num2} = ${difference}<br>
        ✖️ ${num1} × ${num2} = ${product}<br>
        ➗ ${num1} ÷ ${num2} = ${quotient}
    `;
    resultDiv.style.background = '#d4edda';
    resultDiv.style.color = '#155724';
}

// === 2. 배경색 변경 기능 ===
function changeColor() {
    const colors = [
        '#ff6b6b', '#4ecdc4', '#45b7d1', '#f9ca24', 
        '#f0932b', '#eb4d4b', '#6c5ce7', '#74b9ff',
        '#fd79a8', '#fdcb6e', '#e17055', '#81ecec'
    ];
    
    // 랜덤 색상 선택
    const randomColor = colors[Math.floor(Math.random() * colors.length)];
    
    // body 배경색 변경 (부드러운 전환 효과)
    document.body.style.transition = 'background-color 0.5s ease';
    document.body.style.backgroundColor = randomColor;
    
    // 색상 정보 알림
    console.log(`배경색이 ${randomColor}로 변경되었습니다!`);
    
    // 3초 후 원래 색상으로 복귀
    setTimeout(() => {
        document.body.style.backgroundColor = '#f4f4f4';
    }, 3000);
}

// === 3. 메시지 추가 기능 ===
let messageCount = 0;

function addMessage() {
    const messages = [
        '🎉 웹 개발 공부 화이팅!',
        '💻 코딩이 재미있어지고 있어요!',
        '🚀 오늘도 한 걸음 더 성장했네요!',
        '✨ 멋진 웹사이트를 만들어가고 있어요!',
        '🎯 목표를 향해 꾸준히 나아가요!',
        '🌟 당신은 훌륭한 개발자가 될 거예요!',
        '💪 포기하지 말고 계속 도전해요!',
        '🎊 매일매일 발전하는 모습이 보여요!'
    ];
    
    messageCount++;
    const messageContainer = document.getElementById('messages');
    const randomMessage = messages[Math.floor(Math.random() * messages.length)];
    
    // 새 메시지 엘리먼트 생성
    const messageElement = document.createElement('div');
    messageElement.className = 'message';
    messageElement.innerHTML = `
        <strong>메시지 #${messageCount}</strong><br>
        ${randomMessage}
        <button onclick="removeMessage(this)" style="float: right; background: #dc3545; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer;">삭제</button>
    `;
    
    // 메시지 추가
    messageContainer.appendChild(messageElement);
    
    // 스크롤을 새 메시지로 이동
    messageElement.scrollIntoView({ behavior: 'smooth' });
}

// === 4. 메시지 삭제 기능 ===
function removeMessage(button) {
    const messageElement = button.parentElement;
    messageElement.style.animation = 'slideOut 0.5s ease forwards';
    
    setTimeout(() => {
        messageElement.remove();
    }, 500);
}

// === 5. 키보드 이벤트 처리 ===
document.addEventListener('keydown', function(event) {
    // Enter 키로 계산 실행
    if (event.key === 'Enter') {
        const num1 = document.getElementById('num1');
        const num2 = document.getElementById('num2');
        
        // 입력 필드에 포커스가 있을 때만 계산 실행
        if (document.activeElement === num1 || document.activeElement === num2) {
            calculate();
        }
    }
    
    // 스페이스바로 배경색 변경
    if (event.key === ' ' && event.target.tagName !== 'INPUT') {
        event.preventDefault(); // 페이지 스크롤 방지
        changeColor();
    }
});

// === 6. 페이지 로드 완료 시 실행 ===
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎉 웹사이트가 성공적으로 로드되었습니다!');
    
    // 환영 메시지
    setTimeout(() => {
        addMessage();
    }, 1000);
    
    // 입력 필드에 포커스 효과
    const inputs = document.querySelectorAll('input[type="number"]');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.style.transform = 'scale(1.05)';
            this.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.3)';
        });
        
        input.addEventListener('blur', function() {
            this.style.transform = 'scale(1)';
            this.style.boxShadow = 'none';
        });
    });
    
    // 카드 호버 효과 강화
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.borderLeft = '5px solid #667eea';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.borderLeft = 'none';
        });
    });
});

// === 7. 슬라이드 아웃 애니메이션 CSS 추가 ===
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(100px);
        }
    }
`;
document.head.appendChild(style);

// === 8. 콘솔 환영 메시지 ===
console.log(`
🎯 개발자 도구를 열어보셨네요!
🚀 이 웹사이트의 기능들:
   - Enter: 계산하기
   - 스페이스바: 배경색 변경
   - 버튼들을 클릭해보세요!

💻 행복한 코딩 되세요! 
`);

