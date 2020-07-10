
// USER LOGIN function
function loginUser() {
    // set  form into variable 
    let form = $("#user_login");
    // ends here ~ set  form into variable 

    let formObject = {}
    form.serializeArray().map(function(x){formObject[x.name] = x.value;})

    
    // validate LOGIN form
    form.validate({
        rules: {
            email: {
                required: true,
                minlength: 7,
                maxlength: 60,
                emailValidation: true
            },
            password: {
                required: true,
                minlength: 8,
                maxlength: 40
            },
            user_type: {
                required: true,
            }
        },
        highlight: function(element) {
            // add a class "has_error" to the element
            $(element).next('div').addClass('has_error');
        },
        unhighlight: function(element) {
            // remove the class "has_error" from the element
            $(element).next('div').removeClass('has_error');
        },
        errorPlacement: function(error, element) {
            error.appendTo(element.next('div'));
            element.next('div').show();
        },
        success: function(error, element) {
            error.remove();
            $(element).next('div').removeClass('has_error');
            $(element).next('div').hide();
        }
    });
    // ends here ~ validate LOGIN form

    // code block works if form is valid or not
    if(form.valid()) {
        $("#global-loading-modal").show('modal');
        let ajaxData = formObject;

        // ajax call to login user
        $.ajax({
            type: "POST",
            dataType: "json",
            url: "/login",
            data: JSON.stringify(ajaxData),
            success: function(resp) {
                $("#global-loading-modal").hide('modal');
                let response = resp;
                // code block works if responseType is success
                if(response.responseType == 'success') {
                    if(response.messageType == 'success') {

                        toastr.success(response.message,'Success');
                        if(response.isRedirectNext == true) {
                            window.location.href = response.nextPageUrl;
                        }
                        
                    } else if(response.messageType == 'error') {

                        toastr.error(response.message,'Error');
                        if(response.isRedirectNext == true) {
                            window.location.href = response.nextPageUrl;
                        }
                    }
                }
                // ends here ~ code block works if responseType is success
            }
        });
        // ends here ~ ajax call to login user
    }
    // ends here ~ code block works if form is valid or not
}
// ends here ~ USER LOGIN function



// function for toggle login form div
$("#show-forgot-pswd-form-div").hide();
function toggleLoginFormDiv() {
    $("#show-login-form-div").toggle();
    $("#show-forgot-pswd-form-div").toggle();
}
// ends here ~ function for toggle login form div

// forgot password function
function userForgotPswdForm() {
    // set  form into variable 
    let form = $("#forgot-password-form");
    // ends here ~ set  form into variable 

    let formObject = {}
    form.serializeArray().map(function(x){formObject[x.name] = x.value;})

    
    // validate forgot password form
    form.validate({
        rules: {
            forgotUserEmail: {
                required: true,
                emailValidation: true
            }
        },
        highlight: function(element) {
            // add a class "has_error" to the element
            $(element).next('div').addClass('has_error');
        },
        unhighlight: function(element) {
            // remove the class "has_error" from the element
            $(element).next('div').removeClass('has_error');
        },
        messages: {
            userEmail: {
                required: "Please Provide Email Address",
            }
        },
        errorPlacement: function(error, element) {
            error.appendTo(element.next('div'));
            element.next('div').show();
        },
        success: function(error, element) {
            error.remove();
            $(element).next('div').removeClass('has_error');
            $(element).next('div').hide();
        }
    });
    // ends here ~ validate forgot password form

    // code block works if form is valid or not
    if(form.valid()) {
        $("#global-loading-modal").show('modal');
        let ajaxData = {};
        ajaxData['email'] = formObject['forgotUserEmail'];
        ajaxData['token_purpose'] = 'forgot-password';

        // ajax call to login admin user
        $.ajax({
            type: "POST",
            dataType: "json",
            url: "/gen-dynamic-purpose-token",
            data: JSON.stringify(ajaxData),
            success: function(resp) {
                $("#global-loading-modal").hide('modal');
                let response = resp;
                // code block works if responseType is success
                if(response.responseType == 'success') {
                    if(response.messageType == 'success') {
                        // toastr.success(response.message,'Success');
                        // show sweetAlert box
                        Swal.fire({
                          icon: 'success',
                          title: response.message,
                          showConfirmButton: true,
                        })
                        // ends here ~ show sweetAlert box

                        if(response.isRedirectNext == true) {
                            window.location.href = response.nextPageUrl;
                        }
                    } else if(response.messageType == 'error') {
                        toastr.error(response.message,'Error');
                        if(response.isRedirectNext == true) {
                            window.location.href = response.nextPageUrl;
                        }
                    } else if(response.messageType == 'info') {
                        // toastr.error(response.message,'Error');
                        // show sweetAlert box
                        Swal.fire({
                          icon: 'info',
                          title: response.message,
                          showConfirmButton: true,
                        })
                        // ends here ~ show sweetAlert box

                        if(response.isRedirectNext == true) {
                            window.location.href = response.nextPageUrl;
                        }
                    }
                }
                // ends here ~ code block works if responseType is success
            }
        });
        // ends here ~ ajax call to login admin user
    }
    // ends here ~ code block works if form is valid or not
}
// ends here ~ forgot password function