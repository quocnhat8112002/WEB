$(window).ready(function() {
    // gửi lệnh get  api lấy thông tin của phòng
    // document.getElementById('editName').value = 'phkafha';
});

function updateRoom() {
    const urlParams = new URLSearchParams(window.location.search);
    const room_id = urlParams.get('room_id');
    console.log('Room_id lấy được là:' ,room_id);
    // Lấy giá trị từ các trường nhập liệu
    var name = document.getElementById('editName').value;
    var description = document.getElementById('editDescription').value;
    var time = document.getElementById('editTime').value;

    if (name){
        console.log("da kiem tra xong")
        var data = {
            name: name,
            description: description
        };
        console.log("da vao ham 3")
    
        // Gửi yêu cầu PUT đến API`
        fetch(`/edit_room/${room_id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            // Kiểm tra xem có lỗi không
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if(time){
                edit_time_condition(time);
            }
            window.location.href = '/index';
        })
        .catch(error => {
            console.error('Error:', error);
        });
    } else {
        alert('Please enter a room name.');
    }

}
function edit_time_condition(time){
    const urlParams = new URLSearchParams(window.location.search);
    const room_id = urlParams.get('room_id');
    var data = {
        time_condition: time
    };
    fetch(`/room_status/time/${room_id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json', // Đặt loại nội dung là JSON
        },
        body: JSON.stringify(data), // Chuyển đổi đối tượng JavaScript thành chuỗi JSON
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        window.location.href = '/index';
    })
    .catch(error => {
        console.error('Error:', error);
    });
    
}
