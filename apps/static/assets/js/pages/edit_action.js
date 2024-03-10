// Hàm xử lý sự kiện submit của form
document.getElementById('edit_rule_action').addEventListener('submit', function(event) {
    event.preventDefault(); // Ngăn chặn việc gửi form mặc định
    var device = document.getElementById('device').value;
    var valueAction = document.getElementById('value_action').value;
    data ={
        'device':device ,
        'value':valueAction
    }
    put_action(data)
});
function put_action(data){
    const url = window.location.href;
    const match = url.match(/\/edit_action\/(\d+)/);
    const id = match[1]; // Lấy giá trị số từ đường dẫn
    fetch(`/rule_action/${id}`, {
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