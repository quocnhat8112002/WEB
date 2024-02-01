$(window).ready(function(){
    const urlParams = new URLSearchParams(window.location.search);
    const room_id = urlParams.get('room_id');
    fetch(`/device/${room_id}/get_by_type`)
        .then(response => {
            // Kiểm tra xem có lỗi không
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            // Chuyển đổi dữ liệu JSON
            return response.json();
        })
        .then( data => {
             // Xử lý kết quả và hiển thị lên bảng
             const tbody = document.querySelector('#root tbody');
             tbody.innerHTML = '';

             data.forEach(device => {
                 const row = document.createElement('tr');
                 row.innerHTML = `
                     <td>${device.id}</td>
                     <td>${device.name}</td>
                 `;
                 tbody.appendChild(row);
             });
        })
        .catch(error => console.error('Error:', error));
});
// $(window).ready(function() {
//     const urlParams = new URLSearchParams(window.location.search);
//     const room_id = urlParams.get('room_id');
//     // gửi lệnh get  api lấy thông tin mới nhất của device(quạt ,..) trong csdl 
//     fetch('/latest_device_state')
//         .then(response => {
//             // Kiểm tra xem có lỗi không
//             if (!response.ok) {
//                 throw new Error(`HTTP error! Status: ${response.status}`);
//             }
//             // Chuyển đổi dữ liệu JSON
//             return response.json();
//         })
//         .then(data => {
//             // Hiển thị dữ liệu JSON trên console
//             console.log('API Response:', data);
//             //TOFO: render ra table
//             // table html
//         })
//         .catch(error => {
//             console.error('Error:', error);
//         });

//     // gán dataToShow = dữ liệu vừa lấy đc
//     dataToShow = data;

//     //  dong code de show man hinh
//     showData(dataToShow);
//     console.log("ID la:" + room_id)
// });

const socket = io();
//Tạo một đối tượng socket sử dụng Socket.IO để kết nối với máy chủ.
socket.on('connect', function(data) {
    // Khi kết nối Socket.IO được thiết lập thành công, sự kiện 'connect' sẽ được kích hoạt.
    // Trong trường hợp này, một hàm callback được gọi và in ra một thông báo
    console.log('I am connected!!!');
  });


socket.on('data', function(data) {
    // Lắng nghe sự kiện 'data'. Khi server gửi dữ liệu với sự kiện này, hàm callback được kích hoạt.
    // Dữ liệu được nhận từ server được gán vào biến dataToShow.
    // Hàm showData(dataToShow) sau đó được gọi để xử lý và hiển thị dữ liệu mới lên trang web.
    // console.log(data);
    dataToShow = data;
    showData(dataToShow);
});

function showData(data) {
    console.log(data)
    // id = data['id_room'];
    // temp = data['temp'];
    // // hien thi ra man hinj
    // document.getElementById('id_room').value = id;

    
}