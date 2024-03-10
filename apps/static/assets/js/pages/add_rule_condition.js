// Hàm xử lý sự kiện submit của form
document.getElementById('add_rule_condition').addEventListener('submit', function(event) {
    event.preventDefault(); // Ngăn chặn việc gửi form mặc định
    var resource = document.getElementById('resource').value;
    var condition = document.getElementById('condition').value;
    var valueCondition = document.getElementById('value_condition').value;
    data1 ={
        'resource': resource ,
        'condition':condition ,
        'value':valueCondition
    }
    post_condition(data1)
});

// Hàm xử lý khi nhận được giá trị option
function post_condition(data1) {
    fetch('/rule_condition', {
        method: 'POST', // hoặc 'GET' tùy thuộc vào yêu cầu của bạn
        headers: {
            'Content-Type': 'application/json',
            // Nếu cần thêm các headers khác, bạn có thể thêm vào đây
        },
        body: JSON.stringify(data1)
    })
        .then(response => response.json())
        .then(data => {
            console.log(data)
            const newId = data.id
            window.location.href = '/add_rule_action.html?id=' + newId;
        })
        .catch(error => {
            console.error('Error:', error);
        });
}