
function ListRoom(){
    console.log("abchahd");
    // ajax get api
    // console.log ket qua ra man hinh
    fetch('/room/list')
        .then(response => {
            // Kiểm tra xem có lỗi không
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            // Chuyển đổi dữ liệu JSON
            return response.json();
        })
        .then(data => {
            // Hiển thị dữ liệu JSON trên console
            console.log('API Response:', data);
            //TOFO: render ra table
            // table html
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

// add room
function addRoom() {
    console.log("addroom")
    // Lấy giá trị từ các trường nhập liệu
    var name = document.getElementById('name').value.trim();
    var description = document.getElementById('description').value;

    if (name  !== ''){
        // Tạo đối tượng FormData để chứa dữ liệu
        var formData = new FormData();
        formData.append('name', name);
        formData.append('description', description);

        // Gửi yêu cầu POST đến API
        fetch('/add_room', {
            method: 'POST',
            body: formData
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
            window.location.href = '/index';
        })
        .catch(error => {
            console.error('Error:', error);
        });

    } else {
        alert('Please enter a room name.');
    }
    
}


