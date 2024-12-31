document.getElementById("function_select").addEventListener("change", function () {
    console.log(this.value);
    if (this.value == "add_coffee") {
        document.getElementById("item_area").innerHTML = `
        <select class="form-select shadow mb-3 fw-bold text-center" id="item_select"
            style="border-radius: 1.2rem;min-height:58px;font-size: 13px;" aria-label="Default select example">
            <div id="item_area">
                <option value="" selected>
                    請選擇寄杯品項
                </option>
            </div>
            <option value="70">70元品項</option>
            <option value="80">80元品項</option>
        </select>`;
        document.getElementById("number_area").innerHTML = `
        <div class="form-floating mb-3 ">
            <input type="text" class="form-control shadow" id="add_coffee_number" placeholder="name@example.com"
                style="border-radius: 1.2rem;">
            <label for=" floatingInput" class="d-inline-flex justify-content-center align-items-center"
                style="font-size: 12px;"><ion-icon name="cafe-outline" style="font-size: 20px;"
                    class="mx-2"></ion-icon><span></span>
                寄杯數量（包含贈送）</span></label>
        </div>`;
    } else if (this.value == "take_away") {
        document.getElementById("item_area").innerHTML = `
        <select class="form-select shadow mb-3 fw-bold text-center" id="item_select"
            style="border-radius: 1.2rem;min-height:58px;font-size: 13px;" aria-label="Default select example">
            <div id="item_area">
                <option value="" selected>
                    請選擇取杯品項
                </option>
            </div>
            <option value="70">70元品項</option>
            <option value="80">80元品項</option>
        </select>`;
        document.getElementById("number_area").innerHTML = `<div class="form-floating mb-3 ">
            <input type="text" class="form-control shadow" id="add_coffee_number" placeholder="name@example.com"
                style="border-radius: 1.2rem;">
            <label for=" floatingInput" class="d-inline-flex justify-content-center align-items-center"
                style="font-size: 12px;"><ion-icon name="cafe-outline" style="font-size: 20px;"
                    class="mx-2"></ion-icon><span></span>
                取杯數量</span></label>
        </div>`;
    } else {
        document.getElementById("item_area").innerHTML = `        
        <select class="form-select shadow mb-3 fw-bold text-center" id="item_select"
            style="border-radius: 1.2rem;min-height:58px;font-size: 13px;" aria-label="Default select example" disabled>
            <option value="" selected>
                請先選擇功能
            </option>
        </select>`
        document.getElementById("number_area").innerHTML = `
        <div id="number_area">
        <div class="form-floating mb-3 ">
            <input type="text" class="form-control shadow" id="add_coffee_number" placeholder="name@example.com"
                style="border-radius: 1.2rem;" disabled>
            <label for=" floatingInput" class="d-inline-flex justify-content-center align-items-center"
                style="font-size: 12px;"><ion-icon name="cafe-outline" style="font-size: 20px;"
                    class="mx-2"></ion-icon><span></span>
                請先選擇功能</span></label>
        </div>
        </div>`;
    }
});

document.getElementById("submit_button").addEventListener("click", function () {
    alert("Submit button clicked");
    var coffeeData = {
        phone: $('#add_coffee_phone').val(),
        function: $('#function_select').val(),
        item: $('#item_select').val(),
        number: $('#add_coffee_number').val()
    };
    if (coffeeData.phone == '' || coffeeData.phone == undefined || coffeeData.phone.length <= 7 || coffeeData.function == '' || coffeeData.function == undefined || coffeeData.item == '' || coffeeData.item == undefined || coffeeData.number == '' || coffeeData.number == undefined) {
        if (coffeeData.phone.length <= 7) {
            alert('電話號碼格式錯誤');
        }
        alert('請輸入完整資料');
        console.log('【SYSTEM】 coffeeData:', coffeeData);
    }
    else {
        $.ajax({
            url: '/api/coffee',
            type: 'POST',
            data: JSON.stringify(coffeeData),
            contentType: 'application/json',
            success: function (response) {
                console.log('【SYSTEM】 ' + response.message);
                if (response.message == 'updated') {
                    alert('更新成功');
                }
                else if (response.message == 'added') {
                    alert('加入成功');
                }
                $.ajax({
                    url: '/linebot-push?phone=' + coffeeData.phone + '&function=' + coffeeData.function + '&item=' + coffeeData.item + '&number=' + coffeeData.number,
                    type: 'GET',
                    contentType: 'application/json',
                    success: function (response) {
                        console.log('【SYSTEM】 ' + response.message);
                        if (response.message == 'updated') {
                            alert('更新成功');
                        }
                        else if (response.message == 'added') {
                            alert('加入成功');
                        }
                        window.location.reload();
                    },
                    error: function (error) {
                        alert('發生問題，請再試一次');
                    }
                });
                window.location.reload();
            },
            error: function (error) {
                alert('發生問題，請再試一次');
            }
        });
    }
});

$('#add_coffee_phone').on('input', function () {
    var phone = this.value;
    if (phone === '') {
        $('#predict_area').html('');
        return;
    }
    $.ajax({
        url: '/api/coffee?phone=' + phone,
        type: 'GET',
        contentType: 'application/json',
        success: function (response) {
            console.log('【SYSTEM】 response:', response);
            if (response.length != 0) {
                let resultHtml = '';
                for (let i = 0; i < Math.min(response.length, 3); i++) {
                    resultHtml += `
                        <div class="alert alert-success" role="alert">
                            ${response[i].phone}<br>70元品項：${response[i].left[70]}<br>80元品項：${response[i].left[80]}
                        </div>
                    `;
                }
                $('#predict_area').html(resultHtml);
            } else {
                $('#predict_area').html(`
                <div class="alert alert-warning" role = "alert">
                    無法找到相關資料
                </div>
                `);
            }
        },
        error: function (error) {
            console.log('【SYSTEM】 Error fetching data for phone:', phone);
        }
    });
});