$(window).ready(function() {
    
});

function addDevice() {
    const urlParams = new URLSearchParams(window.location.search);
    const room_id = urlParams.get('room_id');
   
    console.log("ID la:" + room_id)
    // Lấy giá trị từ các trường nhập liệu
    var name = document.getElementById('name').value.trim();
    var id = document.getElementById('id').value.trim();
    var type = document.getElementById('type').value.trim();
    var description = document.getElementById('description').value;
    var info = document.getElementById('info').value;

    if (name && id) {
        // Tạo đối tượng chứa dữ liệu
        var requestData = {
            room_id: room_id,
            id : id,
            name: name,
            type: type,
            description: description,
            info: info
        };

        // Gửi yêu cầu POST đến API
        fetch('/device', {
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
            window.location.href = '/room_control.html?room_id=' + room_id;
        })
        .catch(error => {
            console.error('Error:', error);
        });
    } else {
        alert('Please enter a room name.');
    }
}