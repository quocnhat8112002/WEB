$(window).ready(function(){
    getData1();
    getData2();
});
function convertStatus1(condition) {
    if (condition === '0') {
        return 'Bằng';
    } else if (condition === '1') {
        return 'Lớn hơn';
    } else if (condition === '2') {
        return 'Nhỏ hơn';
    } else {
        return 'Không xác định';
    }
}
function convertStatus2(resource, value) {
    // Kiểm tra loại resource
    if (resource === 'pir') {
        return convertValue(value);
    } else {
        return value + '(A)';
    }
}

function convertValue(value) {
    switch (value) {
        case '0':
            return 'Tắt';
        case '1':
            return 'Bật';
        default:
            return 'Không xác định';
    }
}
// hàm hiển thị bảng
function updateData1(data){
    const tbody = document.querySelector('#edit_condition tbody');
    tbody.innerHTML = '';
    data.forEach((item, index) => {
        const row = document.createElement('tr');
        const editLink = `/edit_condition/${item.id}`; 
        row.innerHTML = `
            <td>${item.id}</td>
            <td>${item.resource}</td>
            <td>${convertStatus1(item.condition)}</td>
            <td>${convertStatus2(item.resource, item.value)}</td>
            <td>
                <a href="${editLink}" class="nav-item nav-link edit_rule_condition">
                <div style="display: flex; justify-content: center; align-items: center; height: 100%;">
                    <i class="feather icon-edit"></i>
                </div>
                </a>
            </td>
        `;
        tbody.appendChild(row);
    }); 
}
function updateData2(data){
    const tbody = document.querySelector('#edit_action tbody');
    tbody.innerHTML = '';
    data.forEach((item, index) => {
        const row = document.createElement('tr');
        const editLink = `/edit_action/${item.id}`; 
        row.innerHTML = `
            <td>${item.id}</td>
            <td>${item.id_rule}</td>
            <td>${item.device}</td>
            <td>${convertValue(item.value)}</td>
            <td>
                <a href="${editLink}" class="nav-item nav-link edit_rule_action">
                <div style="display: flex; justify-content: center; align-items: center; height: 100%;">
                    <i class="feather icon-edit"></i>
                </div>
                </a>
            </td>
        `;
        tbody.appendChild(row);
    }); 
}

// hàm lấy dữ liệu
function getData1(){
    fetch(`/rule_condition`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then( data => {
            console.log(data)
            updateData1(data)
        })
        .catch(error => console.error('Error:', error));
}
function getData2(){
    fetch(`/rule_action`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then( data => {
            console.log(data)
            updateData2(data)
        })
        .catch(error => console.error('Error:', error));
}