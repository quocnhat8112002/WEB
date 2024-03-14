function convertStatus(value) {
    return value === "0" ? 'Off' : 'On';
}
$(window).ready(function(){
    getData1();
    getData2();
});
const socket = io();
window.reqId ="";
//Tạo một đối tượng socket sử dụng Socket.IO để kết nối với máy chủ.
socket.on('connect', function(data) {
    // Khi kết nối Socket.IO được thiết lập thành công, sự kiện 'connect' sẽ được kích hoạt.
    // Trong trường hợp này, một hàm callback được gọi và in ra một thông báo
    console.log('I am connected!!!');
});

socket.on('data', function(data) {
    // Lắng nghe sự kiện 'data'. Khi server gửi dữ liệu với sự kiện này, hàm callback được kích hoạt.
    getData1();
    getData2();
});
//Xử lí phản hồi từ esp
socket.on('respone', function(data) {
    console.log(data)
    const fbValue = data.fb;
    const rqId1 = data.reqId;
    const rqId2 = window.reqId
    const id = data.id;
    // So sánh giá trị của trường "fb"
    if (rqId1 == rqId2) {
        console.log(rqId2)
        if ( fbValue == "0"){
            alert("Điều khiển thành công rơ le có id:" + id)
            getData1();
        } else {
            alert("Điều khiển thất bại rơ le có id:" + id);
        }
    } 
});

function updateData1(data){
     const tbody = document.querySelector('#root tbody');
     tbody.innerHTML = '';
     const spinnerDiv = document.createElement('div');
    spinnerDiv.id = 'spinner';
    spinnerDiv.classList.add('spinner');
    tbody.appendChild(spinnerDiv);
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
        <td>Quạt - Máy chiếu</td>
        <td><button id="button-2" data-id="${data[1].id}" data-switch-id="2" data-value="${data[1].value}" onclick="toggleSwitch(this)">${convertStatus(data[1].value)}</button></td>
    `;
    tbody.appendChild(defaultRow2);
    
}

function getData1(){
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
            updateData1(data)
        })
        .catch(error => console.error('Error:', error));
}
//Hàm đợi xử lí
function startLoading() {
    let spinnerId = 'spinner';
    // Hiển thị spinner bằng cách đặt display thành 'block'
    var spinnerElement = document.getElementById(spinnerId);
    spinnerElement.id = 'unique-spinner-id';
    console.log("Element spinner:", spinnerElement);

    // Thêm log để xác nhận hiển thị spinner
    console.log("Trước khi hiển thị:", spinnerElement.style.display);
    spinnerElement.style.display = 'block';
    console.log("Sau khi hiển thị:", spinnerElement.style.display);

    // Giả lập một tác vụ giả định (đợi 2 giây) và sau đó ẩn đi spinner
    setTimeout(function () {
        // Thêm log để xác nhận ẩn spinner
        console.log("Trước khi ẩn:", spinnerElement.style.display);
        spinnerElement.style.display = 'none';
        //Đặt lại id như ban đầu khi thực hiện xong
        spinnerElement.id = 'spinner';
        console.log("Sau khi ẩn:", spinnerElement.style.display);
    }, 2000);
}

function toggleSwitch(button) {
    window.reqId = uuidv4();
    console.log("rqID:" ,reqId);
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
        'reqId':reqId,
        'id': id,
        [`sw${switchId}`]: value
    };
    console.log(data)
    //Gọi api gửi lệnh
    fetch('/request/esp', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        // Xử lý kết quả
        console.log("gưi thành công")
        startLoading();
    })
    .catch(error => {
        console.error('Error:', error);
        alert("Gửi lệnh thất bại!")
    });    

}
//Phần thông số
//////////////////////////////////////////////////
function updateData2(data){
    // Xử lý kết quả và hiển thị lên bảng
    let e = '';
    let temp = '';
    let humi = '';

    // Duyệt qua từng bản ghi trong device_states
    data.device_states.forEach(record => {
        // Kiểm tra giá trị của resource và gán vào biến tương ứng
        if (record.resource === "e") {
            e = record.value;
        } else if (record.resource === "temp") {
            temp = record.value;
        } else if (record.resource === "humi") {
            humi = record.value;
        }
    });
    const tbody = document.querySelector('#parameter tbody');
    tbody.innerHTML = '';
    const defaultRow1 = document.createElement('tr');
   defaultRow1.innerHTML = `
       <td>${e}</td>
       <td>${temp} Độ C</td>
       <td>${humi} %</td>

   `;
   tbody.appendChild(defaultRow1);
}

function getData2(){
   const urlParams = new URLSearchParams(window.location.search);
   const room_id = urlParams.get('room_id');
   const type = "sensor"
   fetch(`/latest_device_state/${room_id}/${type}`)
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
           updateData2(data)
       })
       .catch(error => console.error('Error:', error));
}

//Phần xử lí lọc thông tin tra cứu 
///////////////////////////////////////////////////
// Hàm xử lý sự kiện submit của form
document.getElementById('myForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Ngăn chặn việc gửi form mặc định

    // Lấy giá trị của option được chọn
    const selectedOption = document.getElementById('thongso').value;

    // Gọi hàm getData với giá trị option người dùng chọn
    getData3(selectedOption);
});

// Hàm xử lý khi nhận được giá trị option
function getData3(selectedOption) {
    const urlParams = new URLSearchParams(window.location.search);
    const room_id = urlParams.get('room_id');
    fetch(`/device_state/${room_id}/${selectedOption}`)
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
           updateData3(data)
       })
       .catch(error => console.error('Error:', error));
}
function updateData3(data){
    
    const tbody = document.querySelector('#thongtin tbody');
    tbody.innerHTML = '';
    data.device_states.forEach(record => {
        const newRow = document.createElement('tr');
        newRow.innerHTML = `
            <td>${record.device_id}</td>
            <td>${record.device_name}</td>
            <td>${record.resource}</td>
            <td>${record.value} </td>
            <td>${record.time_stamp} %</td>

        `;
        tbody.appendChild(newRow);
    });
}