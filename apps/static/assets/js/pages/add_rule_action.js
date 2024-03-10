document.getElementById('add_rule_action').addEventListener('submit', function(event) {
    event.preventDefault(); // Ngăn chặn việc gửi form mặc định
    var device = document.getElementById('device').value;
    var valueAction = document.getElementById('value_action').value;
    const urlParams = new URLSearchParams(window.location.search);
    const id = urlParams.get('id');
    data ={
        'id_rule' : id,
        'device': device ,
        'value': valueAction
    }
    post_action(data)
});
function post_action(data){
    fetch('/rule_action', {
        method: 'POST', // hoặc 'GET' tùy thuộc vào yêu cầu của bạn
        headers: {
            'Content-Type': 'application/json',
            // Nếu cần thêm các headers khác, bạn có thể thêm vào đây
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(data => {
            console.log("Thêm hành động mới thành công")
        })
        .catch(error => {
            console.error('Error:', error);
        });
    
}
function button() {
    window.location.href = '/index';
}