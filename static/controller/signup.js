
// Request Activate Account Email OTP
function reqActivateAccEmail() {
    // set  form into variable 
    let form = $("#user_signup");
    // ends here ~ set  form into variable 

    let formObject = {}
    form.serializeArray().map(function(x){formObject[x.name] = x.value;})

    console.log(' >> >> ',formObject)

        
    // validate email to generate OTP
    form.validate({
        rules: {
            email: {
                required: true,
                minlength: 7,
                maxlength: 60,
                emailValidation: true
            },
            first_name: {
                required: false
            },
            last_name: {
                required: false
            },
            password: {
                required: false
            },
            otp: {
                required: false
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
    // ends here ~ validate email to generate OTP

    // code block works if form is valid or not
    if(form.valid()) {

        // $("#global-loading-modal").show('modal');
        formObject['token_purpose'] = 'activate_account';
        let ajaxData = formObject;

        // ajax call to request OTP
        $.ajax({
            type: "POST",
            dataType: "json",
            url: "/gen-dynamic-purpose-token",
            data: JSON.stringify(ajaxData),
            success: function(resp) {
                // $("#global-loading-modal").hide('modal');
                let response = resp;
                // code block works if responseType is success
                if(response.responseType == 'success') {
                    if(response.messageType == 'success') {
                        toastr.success(response.message,'Success');
                    } else if(response.messageType == 'error') {
                        toastr.error(response.message,'Error');
                    } else if(response.messageType == 'info') {
                        toastr.info(response.message,'Info');
                    }
                }
                // ends here ~ code block works if responseType is success
            }
        });
        // ends here ~ ajax call to request OTP
    }
    // ends here ~ code block works if form is valid or not
}
// ends here ~ ajax call to request OTP
    
// USER SIGN UP function
function signupUser() {
    // set  form into variable 
    let form = $("#user_signup");
    // ends here ~ set  form into variable 

    let formObject = {}
    form.serializeArray().map(function(x){formObject[x.name] = x.value;})

    
    // validate SIGN UP form
    form.validate({
        rules: {
            first_name: {
                required: true,
                minlength: 2,
                maxlength: 30
            },
            last_name: {
                required: true,
                minlength: 2,
                maxlength: 30
            },
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
            is_staff: {
                required: true,
            },
            otp: {
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
    // ends here ~ validate SIGN UP form

    // code block works if form is valid or not
    if(form.valid()) {
        // $("#global-loading-modal").show('modal');
        isStaff = formObject['is_staff'];
        isStaff = (isStaff == 'true') ? true : false;
        formObject['is_staff'] = isStaff;

        let ajaxData = formObject;

        // ajax call to login admin user
        $.ajax({
            type: "POST",
            dataType: "json",
            url: "/signup",
            data: JSON.stringify(ajaxData),
            success: function(resp) {
                // $("#global-loading-modal").hide('modal');
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
        // ends here ~ ajax call to login admin user
    }
    // ends here ~ code block works if form is valid or not
}
// ends here ~ USER SIGN UP function