let isProcessing = false; // Biến trạng thái kiểm soát việc gửi yêu cầu

async function control(id) {
    // Kiểm tra xem có đang xử lý yêu cầu nào không
    if (isProcessing) {
        console.log('Đang xử lý yêu cầu, vui lòng đợi...');
        return; // Nếu có yêu cầu đang xử lý, thì không thực hiện yêu cầu mới
    }

    isProcessing = true; // Đánh dấu là đang xử lý

    const data = {};
    const topicOne = "modelx/192.168.87.122/request/one";
    const topicEff = "modelx/192.168.87.122/request/eff";
    const off_all = {
        topic: topicOne,
        channels: [1, 2, 3, 4, 5, 9, 10],
        value: 0
    };
    const on_all = {
        topic: topicOne,
        channels: [1, 2, 3, 4, 5, 9, 10],
        value: 1
    };
    const eff = {
        topic: topicEff,
        id: 1,
        value: 1
    };

    switch (id) {
        case 5:
            Object.assign(data, { topic: topicOne, channels: [9, 10], value: 1 });
            break;
        case 6:
            Object.assign(data, off_all);
            break;
        case 7:
            Object.assign(data, eff);
            break;
        case 8:
            Object.assign(data, on_all);
            break;
        default:
            Object.assign(data, { topic: topicOne, channels: [id], value: 1 });
            break;
    }
    console.log(data);
    // Hàm hứa hẹn tạo delay
    await new Promise(resolve => setTimeout(resolve, 1500)); // Delay 2 giây trước khi gửi fetch

    try {
        const response = await fetch('/post_mqtt', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const result = await response.json();
        console.log('API Response:', result); // Xử lý kết quả từ API
    } catch (error) {
        console.error('Error:', error); // Xử lý lỗi nếu có
    } finally {
        isProcessing = false; // Đặt lại trạng thái sau khi yêu cầu hoàn tất
    }
}
