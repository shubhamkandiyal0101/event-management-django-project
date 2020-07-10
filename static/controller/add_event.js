let saveFunctionFire = true;
// ckeditor for course description
CKEDITOR.replace('event_long_desc');
let longDescContentInstance = CKEDITOR.instances['event_long_desc'];
// ends here ~ ckeditor for course description


// dynamic error function for ckeditor fields
function handleCkeditorMsgError(elementCkeditorInstance, elementErrorMsgDivId) {
    let elementErrorMsgDiv = $(elementErrorMsgDivId);
    if(saveFunctionFire == true) {
        let localInstanceData = elementCkeditorInstance.getData();
        let localInstanceTxt = $(localInstanceData).text();
        if(localInstanceTxt.length == '') {
            elementErrorMsgDiv.text('Content field must not be Blank');
            elementErrorMsgDiv.show();
            return false;
        } else if(localInstanceTxt.length < 10) {
            elementErrorMsgDiv.text('Content must be contain 10 characters');
            elementErrorMsgDiv.show();
            return false;
        } else {
            elementErrorMsgDiv.hide();
            return true;
        }
    }
}
// ends here ~ dynamic error function for ckeditor fields



// custom jQuery Validator error placement
function highlightJqueryValid(errorDiv) {
	$(errorDiv).addClass('has_error');
}
function unhighlightJqueryValid(errorDiv) {
	$(errorDiv).removeClass('has_error');
}
function errorPlacementJqueryValid(txtErrMsg, errorDiv) {
    $(errorDiv).text(txtErrMsg);
	$(errorDiv).show();
}
function successJqueryValid(errorDiv) {
	$(errorDiv).removeClass('has_error');
	$(errorDiv).hide();
}
// ends here ~ custom jQuery Validator error placement

// create event function
function createEventFn() {
	// set form into variables
	let form = $("#add_edit_event");
	// ends here ~ set form into variables

    let formObject = {}
    form.serializeArray().map(function(x){formObject[x.name] = x.value;})

    let isCkeditorFieldsValid = (handleCkeditorMsgError(longDescContentInstance, '#event_long_desc_err_div'))

    // set missed values in formObject
    formObject['event_long_desc'] = longDescContentInstance.getData();
        // ends here ~ set missed values in formObject

    // validate add/edit event form
    form.validate({
        rules: {
            event_name: {
                required: true,
                minlength: 10,
                maxlength: 100,
            },
            event_short_desc: {
                required: true,
                minlength: 10,
                maxlength: 300
            },
            venue: {
                required: true,
                minlength: 10,
                maxlength: 150
            },
            venue_district: {
                required: true,
            },
            event_start_datetime: {
                required: true,
            },
            event_end_datetime: {
                required: true,
            },
            tkt_start_datetime: {
                required: true,
            },
            tkt_end_datetime: {
                required: true,
            },
            pincode: {
            	required: true,
            	minlength: 6,
            	maxlength: 6
            },
            total_tkt_qty: {
            	required: true
            },
            total_price: {
            	required: true
            }
        },
        highlight: function(element) {

            // add a class "has_error" to the element
            $(element).next('div').addClass('has_error');
            
            let elementAttrName = $(element).attr("name");
            if (elementAttrName == "event_start_datetime" ) {
                highlightJqueryValid("#event_start_datetime_err");
            } else if(elementAttrName == 'event_end_datetime') {
            	highlightJqueryValid('#event_end_datetime_err')
            } else if(elementAttrName == 'tkt_start_datetime') {
            	highlightJqueryValid('#tkt_start_datetime_err')
            } else if(elementAttrName == 'tkt_end_datetime') {
            	highlightJqueryValid('#tkt_end_datetime_err')
            }
        },
        unhighlight: function(element) {
            // remove the class "has_error" from the element
            $(element).next('div').removeClass('has_error');

            let elementAttrName = $(element).attr("name");
            if (elementAttrName == "event_start_datetime" ) {
                unhighlightJqueryValid("#event_start_datetime_err");
            } else if(elementAttrName == 'event_end_datetime') {
            	unhighlightJqueryValid('#event_end_datetime_err')
            } else if(elementAttrName == 'tkt_start_datetime') {
            	unhighlightJqueryValid('#tkt_start_datetime_err')
            } else if(elementAttrName == 'tkt_end_datetime') {
            	unhighlightJqueryValid('#tkt_end_datetime_err')
            }
        },
        errorPlacement: function(error, element) {
            error.appendTo(element.next('div'));
            element.next('div').show();

            let txtErrMsg = error[0].innerText;
            let elementAttrName = $(element).attr("name");
            if (elementAttrName == "event_start_datetime" ) {
            	errorPlacementJqueryValid(txtErrMsg, '#event_start_datetime_err');
            } else if(elementAttrName == 'event_end_datetime') {
            	errorPlacementJqueryValid(txtErrMsg,'#event_end_datetime_err')
            } else if(elementAttrName == 'tkt_start_datetime') {
            	errorPlacementJqueryValid(txtErrMsg,'#tkt_start_datetime_err')
            } else if(elementAttrName == 'tkt_end_datetime') {
            	errorPlacementJqueryValid(txtErrMsg,'#tkt_end_datetime_err')
            }

        },
        success: function(error, element) {
            error.remove();
            $(element).next('div').removeClass('has_error');
            $(element).next('div').hide();

            let elementAttrName = $(element).attr("name");
            if (elementAttrName == "event_start_datetime" ) {
            	successJqueryValid('#event_start_datetime_err')
            } else if(elementAttrName == 'event_end_datetime') {
            	successJqueryValid('#event_end_datetime_err')
            } else if(elementAttrName == 'tkt_start_datetime') {
            	successJqueryValid('#tkt_start_datetime_err')
            } else if(elementAttrName == 'tkt_end_datetime') {
            	successJqueryValid('#tkt_end_datetime_err')
            }
        }
    });
    // ends here ~  validate add/edit event form

    if(form.valid()) {
        if (isCkeditorFieldsValid == false) {
          return false;
        }

        // ajax call to create new event
        // $('#show-loading-modal').modal('show');
        let ajaxData = formObject;
        $.ajax({
            type: "POST",
            dataType: "json",
            url: "/organizer/add-event",
            data: JSON.stringify(ajaxData),
            success: function(resp) {
                // $('#show-loading-modal').modal('hide');
                let response = resp;
                // code block works if responseType is success
                if(response.responseType == 'success') {
                    if(response.messageType == 'success') {
                        // show sweetAlert box
                        Swal.fire({
                          icon: 'success',
                          title: response.message,
                          showConfirmButton: true,
                        })
                        // ends here ~ show sweetAlert box
                        // toastr.success(response.message,'Success');
                        if(response.isRedirectNext == true) {
                            window.location.href = response.nextPageUrl;
                        }
                    } else if(response.messageType == 'error') {
                        // show sweetAlert box
                        Swal.fire({
                          icon: 'error',
                          title: response.message,
                          showConfirmButton: true,
                        })
                        // ends here ~ show sweetAlert box
                        // toastr.error(response.message,'Error');
                    }
                }
                // ends here ~ code block works if responseType is success
            }
        });
        // ends here ~ ajax call to create new event

    }

}
// ends here ~ create event function

// // USER LOGIN function
// function loginUser() {
//     // set  form into variable 
//     let form = $("#user_login");
//     // ends here ~ set  form into variable 

//     let formObject = {}
//     form.serializeArray().map(function(x){formObject[x.name] = x.value;})

    
//     // validate LOGIN form
//     form.validate({
//         rules: {
//             email: {
//                 required: true,
//                 minlength: 7,
//                 maxlength: 60,
//                 emailValidation: true
//             },
//             password: {
//                 required: true,
//                 minlength: 8,
//                 maxlength: 40
//             },
//             user_type: {
//                 required: true,
//             }
//         },
//         highlight: function(element) {
//             // add a class "has_error" to the element
//             $(element).next('div').addClass('has_error');
//         },
//         unhighlight: function(element) {
//             // remove the class "has_error" from the element
//             $(element).next('div').removeClass('has_error');
//         },
//         errorPlacement: function(error, element) {
//             error.appendTo(element.next('div'));
//             element.next('div').show();
//         },
//         success: function(error, element) {
//             error.remove();
//             $(element).next('div').removeClass('has_error');
//             $(element).next('div').hide();
//         }
//     });
//     // ends here ~ validate LOGIN form

//     // code block works if form is valid or not
//     if(form.valid()) {
//         // $("#global-loading-modal").show('modal');
//         let ajaxData = formObject;

//         // ajax call to login user
//         $.ajax({
//             type: "POST",
//             dataType: "json",
//             url: "/login",
//             data: JSON.stringify(ajaxData),
//             success: function(resp) {
//                 // $("#global-loading-modal").hide('modal');
//                 let response = resp;
//                 // code block works if responseType is success
//                 if(response.responseType == 'success') {
//                     if(response.messageType == 'success') {

//                         toastr.success(response.message,'Success');
//                         if(response.isRedirectNext == true) {
//                             window.location.href = response.nextPageUrl;
//                         }
                        
//                     } else if(response.messageType == 'error') {

//                         toastr.error(response.message,'Error');
//                         if(response.isRedirectNext == true) {
//                             window.location.href = response.nextPageUrl;
//                         }
//                     }
//                 }
//                 // ends here ~ code block works if responseType is success
//             }
//         });
//         // ends here ~ ajax call to login user
//     }
//     // ends here ~ code block works if form is valid or not
// }
// // ends here ~ USER LOGIN function