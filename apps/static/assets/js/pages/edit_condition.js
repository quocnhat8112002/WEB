$(window).ready(function() {
    
});
// Hàm xử lý sự kiện submit của form
document.getElementById('edit_rule_condition').addEventListener('submit', function(event) {
    event.preventDefault(); // Ngăn chặn việc gửi form mặc định
    var condition = document.getElementById('condition').value;
    var valueCondition = document.getElementById('value_condition').value;
    data ={
        'condition':condition ,
        'value':valueCondition
    }
    put_condition(data)
});
function put_condition(data){
    const url = window.location.href;
    const match = url.match(/\/edit_condition\/(\d+)/);
    const id = match[1]; // Lấy giá trị số từ đường dẫn
    fetch(`/rule_condition/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            window.location.href = '/edit_rule.html';
        })
        .catch(error => console.error('Error:', error));
}