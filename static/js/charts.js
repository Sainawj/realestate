// Example chart data for Expenditure vs Income Chart
const expenditureIncomeCtx = document.getElementById('expenditureIncomeChart').getContext('2d');
const expenditureIncomeChart = new Chart(expenditureIncomeCtx, {
    type: 'pie',
    data: {
        labels: ['Expenditure', 'Income'],
        datasets: [{
            label: 'Expenditure vs Income',
            data: [65, 35],
            backgroundColor: ['#FF6384', '#36A2EB']
        }]
    }
});

// Wallet Expenditure (Last 6 Months) Chart
const walletCtx = document.getElementById('walletChart').getContext('2d');
const walletChart = new Chart(walletCtx, {
    type: 'bar',
    data: {
        labels: ['April', 'May', 'June', 'July', 'August', 'September'],
        datasets: [{
            label: 'Wallet Expenditure (Ksh)',
            data: [1000000, 850000, 1200000, 900000, 1100000, 950000],
            backgroundColor: '#FFCE56'
        }]
    }
});

