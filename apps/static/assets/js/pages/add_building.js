$(window).ready(function() {
    
});

function addBuilding() {
    // Lấy giá trị từ các trường nhập liệu
    var name = document.getElementById('name').value.trim();
    var description = document.getElementById('description').value;

    if (name) {
        // Tạo đối tượng chứa dữ liệu
        var requestData = {
            name: name,
            description: description,
        };

        // Gửi yêu cầu POST đến API
        fetch('/add_building', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        })
        .then(response => {
            // Kiểm tra xem có lỗi không
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            // Chuyển đổi dữ liệu JSON
            return response.json();
        })
        .then(data => {
            // Xử lý kết quả từ server (nếu cần)
            console.log('API Response:', data);
            // window.location.href = '/room_control.html?room_id=' + room_id;
        })
        .catch(error => {
            console.error('Error:', error);
        });
    } else {
        alert('Please enter a room name.');
    }
}