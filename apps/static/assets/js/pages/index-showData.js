$(window).ready(function(){
    getData();
});

socket.on('connect', function(data) {
    
    console.log('I am connected!!!');
  });
socket.on('data', function(data) {
    getData();
});

function updateLatestStatus(data) {
    console.log("có gọi hàm")
    // Truy cập vào tất cả các phần tử có thuộc tính get-data-room-id
    // Truy cập vào tất cả các phần tử td có id bắt đầu bằng 'latest-status-'
    const latestStatusElements = document.querySelectorAll('[id^="latest-status-"]');

    // Duyệt qua mỗi phần tử và thực hiện các thao tác
    latestStatusElements.forEach(element => {
        // Lấy giá trị room.id từ id của phần tử
        const roomId = element.id.replace('latest-status-', '');
        console.log(roomId)
        // Kiểm tra xem có dữ liệu không và dữ liệu có tồn tại
        if (data && data.device_states.length > 0) {
            // Kiểm tra trạng thái của từng phòng
            let isAnyOn = false;
            for (const device of data.device_states) {
                if (device.room_id == roomId && device.value === "1") {
                    isAnyOn = true;
                    break; // Thoát khỏi vòng lặp khi đã tìm thấy trạng thái "On"
                }
            }

            // Log để kiểm tra
            console.log(`roomId: ${roomId}`);
            console.log(`isAnyOn: ${isAnyOn}`);

            // Thực hiện cập nhật trạng thái mới nhất trên giao diện
            element.textContent = isAnyOn ? "On" : "Off";
        }
    });

}

function getData(){
    const type = "controller"
    fetch(`/latest_deviceState/${type}`)
        .then(response => {
            // Kiểm tra xem có lỗi không
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            // Chuyển đổi dữ liệu JSON
            return response.json();
        })
        .then( data => {
            console.log(data)
            updateLatestStatus(data);
        })
        .catch(error => console.error('Error:', error));
}


