// const socket = io('http://127.0.0.1:5000');


function toggleSwitch(button) {
    const socket = io('http://127.0.0.1:5000');

    // const socket = io();
    socket.on('connect', function() {
        // Khi kết nối Socket.IO được thiết lập thành công, sự kiện 'connect' sẽ được kích hoạt.
        // Trong trường hợp này, một hàm callback được gọi và in ra một thông báo
        console.log('I am connected!!!');
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
        const jsonData = JSON.stringify(data);

        socket.emit('client_request', jsonData);
    });
        
    

}