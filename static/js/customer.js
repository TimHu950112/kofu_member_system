$(document).ready(function () {
    console.log(' 【SYSTEM】 customer.js loaded');
    $('#customer_input').on('input', function () {
        var input = $(this).val();
        $('#customer_result').empty();
        if (input !== '') {
            $.ajax({
                url: '/api/customer?phone=' + input,
                type: 'GET',
                success: function (response) {
                    if (response.length == 0) {
                        $('#customer_result').empty();
                        $('#customer_result').append('<h5>無結果</h5>');
                    }
                    for (var i = 0; i < 3; i++) {
                        permanent_status = 'ㄧ般會員';
                        if (response[i].permanent_status == true) {
                            permanent_status = '永久會員';
                        }
                        if (parseInt(response[i].active_year) == parseInt(new Date().getFullYear()) || response[i].permanent_status == true) {
                            $('#customer_result').append(`
                    <div class="shadow pt-2 p-2 mt-2 mb-4 d-flex justify-content-between align-items-center position-relative z-0"
                        style = "border-radius: 1.2rem;" >
                        <div class="m-0" style="font-size: 10px; color:rgba(76, 76, 76, 0.502)">
                            <p class="ms-2 mt-0 mb-0" style="font-size: 15px; color:black;">`+ response[i].phone + ` • ` + response[i].name + `</p>
                            <p class="ms-2 mt-0 mb-0 text-start">消費次數 • ✔︎ 100% (000)<br>於`+ response[i].active_year + `年有效<br>★` + permanent_status + `</p>
                                </div>
                                <ion-icon name="person-circle-outline" class="img img-fluid me-1 z-1 text-dark" alt=""
                                    style="border-radius:0.7rem;width:90px;height:90px"></ion-icon>

                                <div class="shadow position-absolute translate-middle z-3 d-inline-flex align-items-center justify-content-center  top-100 start-100"
                                    style=" border-radius:50%; width: 35px;height: 35px;background-color:white;">
                                    <ion-icon name="send-outline" style="font-size: 18px;"></ion-icon>
                                </div>
                    </div>`);
                        }
                    }
                },
                error: function (error) {
                    console.log('【SYSTEM】 error:', error);
                    $('#customer_result').empty();
                    $('#customer_result').append(`
                    <div class="alert alert-warning d-flex align-items-center mt-2" role="alert">
                        <ion-icon name = "warning-outline" class= "me-2" style = "font-size:25px" ></ion-icon>
                            <div>
                                連線錯誤，請檢查網路或登入狀態
                            </div>
                    </div > `);
                }
            });
        } else {

        }
    });

    $('#add_customer_phone').on('input', function () {
        var input = $(this).val();
        if (input !== '' && input.length == 10) {
            $.ajax({
                url: '/api/customer?phone=' + input,
                type: 'GET',
                success: function (response) {
                    if (response.length == 1) {
                        console.log("【SYSTEM】 only one result:", response);
                        $('#add_customer_name').val(response[0].name);
                        alert('已經是會員');
                    }
                }
            });
        } else {

        }
    });

    $('#add_customer').on('click', function () {
        var customerData = {
            name: $('#add_customer_name').val(),
            phone: $('#add_customer_phone').val(),
            permanent_status: $('#permanent_status').is(":checked")
        };
        if (customerData.name == '' || customerData.name == undefined || customerData.phone == '' || customerData.phone == undefined) {
            alert('請輸入完整資料');
            console.log('【SYSTEM】 customerData:', customerData);
        }
        else if (customerData.phone.length != 10) {
            $('#phone_area').empty();
            $('#phone_area').append(`
                <div class="form-floating mb-1 is-invalid">
                    <input type="text" class="form-control shadow is-invalid" id="add_customer_phone"
                        placeholder="name@example.com" style="border-radius: 1.2rem;">
                    <label for=" floatingInput" class="d-inline-flex justify-content-center align-items-center"
                        style="font-size: 12px;"><ion-icon name="call-outline" style="font-size: 20px;"
                            class="mx-2"></ion-icon><span></span>
                        電話號碼</span></label>
                </div>
                <div class="invalid-feedback m-2">
                    手機號碼格式錯誤
                </div>`);
            $('#add_customer_phone').val(customerData.phone);
        }
        else {
            $('#add_customer').attr('disabled', true);
            $.ajax({
                url: '/api/customer',
                type: 'POST',
                data: JSON.stringify(customerData),
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
        }
    });
});