document.addEventListener('DOMContentLoaded', function() {
    // ── Tab Selection Logic ──
    const tabs = document.querySelectorAll('.tab-btn');
    const sections = document.querySelectorAll('.section-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const target = tab.dataset.tab;

            // Update Buttons
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // Update Sections
            sections.forEach(s => {
                s.classList.remove('active');
                if (s.id === `section-${target}`) {
                    s.classList.add('active');
                }
            });
        });
    });

    // ── Data Definition ──
    const financialData = {
        available: 16905006,  // 현금 잔액(0.5M) + 제예금 잔액(16.4M)
        reserves: 687944807,   // 장기수선/하자보수 충당금 + 예비비 + 이익잉여금 + 관리비예치금
        liabilities: 25877961  // 유동부채 합계
    };

    // ── Currency Formatter ──
    const formatCurrency = (val) => {
        return new Intl.NumberFormat('ko-KR', {
            style: 'currency',
            currency: 'KRW',
            maximumFractionDigits: 0
        }).format(val).replace('₩', '') + '원';
    };

    // ── Chart Initialization ──
    const financeCanvas = document.getElementById('financeChart');
    if (financeCanvas) {
        const ctx = financeCanvas.getContext('2d');
        
        const grad1 = ctx.createLinearGradient(0, 0, 0, 400);
        grad1.addColorStop(0, '#10b981');
        grad1.addColorStop(1, '#059669');

        const grad2 = ctx.createLinearGradient(0, 0, 0, 400);
        grad2.addColorStop(0, '#1e3a8a');
        grad2.addColorStop(1, '#3b82f6');

        const grad3 = ctx.createLinearGradient(0, 0, 0, 400);
        grad3.addColorStop(0, '#ef4444');
        grad3.addColorStop(1, '#b91c1c');

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['사용 가능 자금', '미래 대비 충당금', '지불 예정 부채'],
                datasets: [{
                    data: [financialData.available, financialData.reserves, financialData.liabilities],
                    backgroundColor: [grad1, grad2, grad3],
                    borderWidth: 0,
                    hoverOffset: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            font: { family: 'Pretendard', size: 12, weight: '600' }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.label || '';
                                if (label) label += ': ';
                                label += formatCurrency(context.raw);
                                return label;
                            }
                        }
                    }
                },
                cutout: '70%',
                animation: { animateScale: true, animateRotate: true }
            }
        });
    }

    // ── Animation Effects ──
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'all 0.6s cubic-bezier(0.16, 1, 0.3, 1)';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100 * index);
    });
});
