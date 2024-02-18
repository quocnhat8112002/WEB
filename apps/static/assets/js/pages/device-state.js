function convertStatus(value) {
    return value === "0" ? 'Off' : 'On';
}
$(window).ready(function(){
    getData();
});

const socket = io();
//Tạo một đối tượng socket sử dụng Socket.IO để kết nối với máy chủ.
socket.on('connect', function(data) {
    // Khi kết nối Socket.IO được thiết lập thành công, sự kiện 'connect' sẽ được kích hoạt.
    // Trong trường hợp này, một hàm callback được gọi và in ra một thông báo
    console.log('I am connected!!!');
});


socket.on('data', function(data) {
    // Lắng nghe sự kiện 'data'. Khi server gửi dữ liệu với sự kiện này, hàm callback được kích hoạt.
    getData();
    
});


function updateData(data){
    console.log("du lieu moi nhat la:")
    console.log(data)
     // Xử lý kết quả và hiển thị lên bảng
     const tbody = document.querySelector('#root tbody');
     tbody.innerHTML = '';
     const defaultRow1 = document.createElement('tr');
    defaultRow1.innerHTML = `
        <td>0</td>
        <td>Điều hòa</td>
        <td><button id="button-1" data-id="${data[0].id}" data-switch-id="1" data-value="${data[0].value}" onclick="toggleSwitch(this)">${convertStatus(data[0].value)}</button></td>
    `;
    tbody.appendChild(defaultRow1);

    const defaultRow2 = document.createElement('tr');
    defaultRow2.innerHTML = `
        <td>1</td>
        <td>Các thiết bị khác</td>
        <td><button id="button-2" data-id="${data[1].id}" data-switch-id="2" data-value="${data[1].value}" onclick="toggleSwitch(this)">${convertStatus(data[1].value)}</button></td>
    `;
    tbody.appendChild(defaultRow2);
}

function getData(){
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
            console.log(data)
            updateData(data)
        })
        .catch(error => console.error('Error:', error));
}

function toggleSwitch(button) {
    const id = button.dataset.id;
    const switchId = button.dataset.switchId;
    let value = button.dataset.value;
    // Thay đổi giá trị từ "1" thành "0" và ngược lại
    value = (value === "1") ? 0 : 1;    
    console.log(switchId)
    console.log(value)
    console.log(id)
    // Gửi yêu cầu đến server thông qua Socket.IO
    const data = {
        'id': id,
        [`sw${switchId}`]: value
    };
    console.log(data)
    socket.emit('client_request', data);    
    

}