// NOTE: Here is code written for all things which is related to web (or without login user)

// if $ is undefined then set correct value of $  
if($ == undefined) {
    $ = jQuery;
}
// ends here ~ if $ is undefined then set correct value of $

// settings for toastr js
toastr.options.progressBar = true;
// ends here ~ settings for toastr js

// settings and variable for SweetAlert
// ends here ~ settings and variable for SweetAlert


// function for admin login (file name: adminLogin.html)
function adminFormLogin() {
    // set  form into variable 
	let form = $("#admin-login-form");
    // ends here ~ set  form into variable 

	let formObject = {}
    form.serializeArray().map(function(x){formObject[x.name] = x.value;})
    console.log(formObject)

    
    // validate admin login form
    form.validate({
        rules: {
            adminEmail: {
                required: true,
                emailValidation: true
            },
            adminPassword: {
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
        messages: {
            adminEmail: {
                required: "Please Provide Email Address",
            },
            adminPassword: {
                required: "Please Provide Password",
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
    // ends here ~ validate admin login form

    if(form.valid()) {
        // code works if form is valid
        let ajaxData = {};
        ajaxData['email'] = formObject['adminEmail'];
        ajaxData['password'] = formObject['adminPassword'];

        // ajax call to login admin user
        $.ajax({
            type: "POST",
            dataType: "json",
            url: "/dynamic-user-login/admin",
            data: JSON.stringify(ajaxData),
            success: function(resp) {
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

        // ends here ~ code works if form is valid
    }
}
// ends here ~ function for admin login (file name: adminLogin.html)

// user login 
function userFormLogin() {
    // set  form into variable 
    let form = $("#user-login-form");
    // ends here ~ set  form into variable 

    let formObject = {}
    form.serializeArray().map(function(x){formObject[x.name] = x.value;})
    console.log(formObject)

    
    // validate admin login form
    form.validate({
        rules: {
            userEmail: {
                required: true,
                emailValidation: true
            },
            userPassword: {
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
        messages: {
            userEmail: {
                required: "Please Provide Email Address",
            },
            userPassword: {
                required: "Please Provide Password",
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
    // ends here ~ validate admin login form

    if(form.valid()) {
        // code works if form is valid
        let ajaxData = {};
        ajaxData['email'] = formObject['userEmail'];
        ajaxData['password'] = formObject['userPassword'];

        // ajax call to login admin user
        $.ajax({
            type: "POST",
            dataType: "json",
            url: "/dynamic-user-login/student",
            data: JSON.stringify(ajaxData),
            success: function(resp) {
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

        // ends here ~ code works if form is valid
    }
}
// ends here ~ user login

//########################################################
//ALL CUSTOM JQUERY VALIDATOR VALIDATION
//########################################################

// check email is valid or not
$.validator.addMethod("emailValidation", function(emailVal, element) {
    return emailRegex.test(emailVal)
}, "Please Provide valid Email Address");
// ends here ~ check email is valid or not

// check mobile number is valid or not
$.validator.addMethod("mobileValidation", function(mobileVal, element) {
    return mobileRegex.test(mobileVal)
}, "Please Provide valid Mobile Number");
// ends here ~ check mobile number is valid or not

// check name is valid or not
$.validator.addMethod("nameValidation", function(nameVal, element) {
    return nameRegex.test(nameVal)
}, "Please Only Provide Character without Spaces (Allowed:[A-Za-z])");
// ends here ~ check name is valid or not

//########################################################
//ENDS HERE ~ ALL CUSTOM JQUERY VALIDATOR VALIDATION
//########################################################
