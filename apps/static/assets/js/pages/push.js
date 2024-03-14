const socketI = io();
socketI.on('rule', function(data) {
    console.log('đã nhận được sk');
    fetch('/room_id')
    .then(response => {
        if (!response.ok) {
        throw new Error('Failed to fetch room_id');
        }
        return response.json();
    })
    .then(data => {
        alert("Tự động tắt sw thành công phòng có id là:"+ data)
    })
    .catch(error => {
        console.error('Error fetching room_id:', error);
    });
});
socketI.on('err', function(data) {
    console.log('đã nhận được thông báo lỗi');
    alert(data)    
});