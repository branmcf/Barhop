$(function () {

    function errorHandler() {

    }

    function validateFile(file) {
        var response = {};
        response.error = "";
        response.valid = true;
        if (file.type != "image/jpeg" && file.type != "image/png") {
            response.valid = false;
            response.error += "Only jpg and png files are allowed.";
        }
        if (file.size > 5000000) {
            response.valid = false;
            response.error += "File size limit exceeded.";
        }

        return response;
    }

    function asyncFileUpload(Url, formData) {
        $.ajax({
            url: Url,  //Server script to process data
            type: 'POST',
            xhr: function () {  // Custom XMLHttpRequest
                var myXhr = $.ajaxSettings.xhr();
                if (myXhr.upload) { // Check if upload property exists
//                myXhr.upload.addEventListener('progress',progressHandlingFunction, false); // For handling the progress of the upload
                }
                return myXhr;
            },
            //Ajax events
            beforeSend: function () {
                //$(imgHolder).addClass("uploading");
            },
            error: errorHandler,
            // Form data
            data: formData,
            //Options to tell jQuery not to process data or worry about content-type.
            cache: false,
            contentType: false,
            processData: false
        }).done(function (data) {

            if (data.ok) {
                msg = "<p class='green msg'>Image upload complete.</p>"
                $('.user-image').attr('src', '/static/images/profile/200x200/' + data.image_path)
            } else {
                msg = "<p class='red msg'>|message|</p>";
                msg = msg.replace('|message|', data.errors['file']);
            }
            $('#img-res').html(msg);
        });
    }

    $("input[type='file']").on("change", function (e) {
        e.preventDefault();
        var fileData = this.files[0];
        var valid = validateFile(fileData);
        if (!valid.valid) {
            alert(valid.error);
            return;
        }
        if (this.files && this.files[0]) {
            var reader = new FileReader();
            reader.onload = function (e) {
                var formData = new FormData();
                formData.append('file', fileData);
                Url = '/accounts/image/upload/';
                asyncFileUpload(Url, formData);
            };
            reader.readAsDataURL(this.files[0]);
        }
    });

    $("#get_price_form").submit(function (ev) {

        $('.form-group').removeClass('has-error');
        $('.help-block').remove();

        var data = {
            amount: $("#id_amount").val(),
            detail: $("#id_detail").val(),
            customer_id: customer_id,
            conversation_id: conversation_id
        };
        $.ajax({
            type: 'POST',
            url: '/payment/send_price/',
            data: data,
            dataType: 'json', // what type of data do we expect back from the server
            encode: true
        }).done(function (data) {
            if (!data.success) {
                if (data.errors.amount) {
                    $('#amount_group').addClass('has-error'); // add the error class to show red input
                    $('#amount_group').append('<div class="help-block">' + data.errors.amount + '</div>'); // add the actual error message under our input
                }

                if (data.errors.detail) {
                    $('#detail_group').addClass('has-error'); // add the error class to show red input
                    $('#detail_group').append('<div class="help-block">' + data.errors.detail + '</div>'); // add the actual error message under our input
                }
            } else {

                $("#price_info").modal('hide');
                $("#id_amount").val('');
                $("#id_detail").val('');
                $('#trophy_' + current_trophy_id).click();
            }
        });
        ev.preventDefault();
    });

    $("#trophy_form").submit(function (ev) {
        ev.preventDefault();
        $('.form-group').removeClass('has-error');
        $('.help-block').remove();

        var data = {
            trophy: $("#id_trophy").val(),
            message: $("#id_message").val(),
            default_order_response: $("#id_default_order_response").val()
        };
        $.ajax({
            type: 'POST',
            url: '/trophy/edit/' + $('#id_modal_trophy').val() + '/',
            data: data,
            dataType: 'json', // what type of data do we expect back from the server
            encode: true
        }).done(function (data) {
            if (!data.success) {
                if (data.errors.trophy) {
                    $('#trophy_group').addClass('has-error'); // add the error class to show red input
                    $('#trophy_group').append('<div class="help-block">' + data.errors.trophy + '</div>'); // add the actual error message under our input
                }

                if (data.errors.message) {
                    $('#message_group').addClass('has-error'); // add the error class to show red input
                    $('#message_group').append('<div class="help-block">' + data.errors.message + '</div>'); // add the actual error message under our input
                }
            } else {
                $('#add_trophy').modal('hide');
                $("#id_trophy").val('');
                $("#id_message").val('');
                location.reload()
            }
        });
    });

    $('#confirm-delete').on('show.bs.modal', function (e) {
        $('#delete_trophy').attr('data-target_id', $(e.relatedTarget).data('id'));
    });

    $('#confirm-block').on('show.bs.modal', function (e) {
        $('#block_user').attr('data-target_id', $(e.relatedTarget).data('customer-id'));
    });

    $('#confirm-order-close').on('show.bs.modal', function (e) {
        $('#close_order').attr('data-target_id', $(e.relatedTarget).data('id'));
    });

    $('#edit_trophy').on('show.bs.modal', function (e) {
        $('#id_modal_trophy').val($(e.relatedTarget).data('id'));
        $('#delete_trophy').attr('data-target_id', $(e.relatedTarget).data('id'));
    });

    var customer_id = null;
    var order_customer_id = null;
    var conversation_id = null;

    $('#price_info').on('show.bs.modal', function (e) {
        customer_id = $(e.relatedTarget).data('customer-id');
        conversation_id = $(e.relatedTarget).data('id');
    });

    $('#order_ready').on('show.bs.modal', function (e) {
        order_customer_id = $(e.relatedTarget).data('customer-id');
        conversation_id = $(e.relatedTarget).data('id');

    });

    $('#delete_trophy').click(function (ev) {
        ev.preventDefault();
        var id = $(this).attr('data-target_id');
        $.get('/trophy/delete/' + id + '/').done(function (data) {
            if (!data.success) {
                alert(data['message'])
            } else {
                //$('#trophy_' + id).remove();
                $('#confirm-delete').modal('hide');
                location.reload()
            }
        });
    });

    $('.trophy-edit').click(function (ev) {
        ev.preventDefault();
        var id = $(this).data('id');

        $.get('/trophy/get/' + id + '/').success(function (data) {
            if (data.success) {
                var d = data.data;
                $('#id_trophy').val(d.trophy);
                $('#id_message').val(d.message);
                $('#id_default_order_response').val(d.default_order_response);
            }
        });
    });

    $('body').on('click', '.order-ready', function (ev) {
        ev.preventDefault();
        var id = $(this).data('id');

        $.get('/trophy/default_order_response/' + id + '/').success(function (data) {
            if (data.success) {
                var d = data.data;
                $('#id_order_message').val(d.default_order_response);
            }
        })
    });

    $('#close_order').click(function (ev) {
        ev.preventDefault();
        var id = $(this).attr('data-target_id');
        $.get('/route/close_conversation/' + id + '/').done(function (data) {
            if (!data.success) {
                alert(data['message'])
            } else {
                $('#conversation_' + id).remove();
                $('#confirm-order-close').modal('hide');
                window.location.href = '/';
            }
        });
    });

    $('#block_user').click(function (ev) {
        ev.preventDefault();
        var id = $(this).attr('data-target_id');
        $.get('/block/' + id + '/').done(function (data) {
            if (!data.success) {
                alert(data['message'])
            } else {
                $('#confirm-block').modal('hide');
            }
        });
    });

    $("#order_ready_form").submit(function (ev) {

        $('.form-group').removeClass('has-error');
        $('.help-block').remove();

        var data = {
            message: $("#id_order_message").val(),
            customer_id: order_customer_id,
            conversation_id: conversation_id
        };
        $.ajax({
            type: 'POST',
            url: '/route/order_ready/',
            data: data,
            dataType: 'json', // what type of data do we expect back from the server
            encode: true
        }).done(function (data) {
            if (!data.success) {
                if (data.errors.message) {
                    $('#order_message_group').addClass('has-error'); // add the error class to show red input
                    $('#order_message_group').append('<div class="help-block">' + data.errors.message + '</div>'); // add the actual error message under our input
                }
            } else {
                $("#order_ready").modal('hide');
                $("#id_message").val('');
                $('#trophy_' + current_trophy_id).click();
            }
        });
        ev.preventDefault();
    });

    var current_trophy_id = null;

    $('.trophy_item').click(function (ev) {
        ev.preventDefault();
        var id = $(this).data('id');
        current_trophy_id = id;
        $.get('/trophy/conversation/' + id + '/').success(function (data) {
            if (!data.success) {
                alert(data.message);
            } else {
                var html = '';
                $.each(data.data, function (k, v) {
                    html += '<div class="media' + ((v.has_new_message) ? ' alert-info"' : '"') + ' id=' + v.conversation_id + '>' +
                        '<div class="media-left media-middle">' +
                        '<a href="/route/view_conversation/' + v.conversation_id + '"><img class="media-object" src="/static/images/profile/200x200/' + v.customer_image + '" height="200" width="200"></a></div>' +
                        '<div class="media-body">' +
                        '<h4 class="media-heading">' + v.customer_username + '</h4>' +
                        '<div class="well">' + v.recent_message + '</div>' +
                        '<span style="display:inline;">' +
                        '<button type="button" class="btn btn-success" data-toggle="modal" data-target="#price_info" data-id="' + v.conversation_id + '" data-customer-id="' + v.customer_id + '">Send Invoice </button>' +
                        '<button type="button" class="btn btn-info order-ready" data-toggle="modal" data-target="#order_ready" data-id="' + v.conversation_id + '" data-customer-id="' + v.customer_id + '">Order Ready </button>' +
                        '<button type="button" class="btn btn-warning" data-toggle="modal" data-target="#confirm-order-close" data-id="' + v.conversation_id + '">Close Order </button>' +
                        '</span> </div> </div>'
                });

                $('#conversation_section').html(html);
                $.each(data.new_conv_trop, function (k, v) {
                    $('#trophy_' + v).parent().addClass('list-group-item-info');
                });
            }
        })
    });

    function startIndexRefresh() {
        //setTimeout(startIndexRefresh, 60000);
        if (current_trophy_id == null) {
            return false;
        }
        $.get('/trophy/conversation/' + current_trophy_id + '/', function (data) {
            if (data.success) {
                var html = '';
                $.each(data.data, function (k, v) {
                    html += '<div class="media' + ((v.has_new_message) ? ' alert-info"' : '"') + ' id=' + v.conversation_id + '>' +
                        '<div class="media-left media-middle">' +
                        '<a href="/route/view_conversation/' + v.conversation_id + '"><img class="media-object" src="/static/images/profile/200x200/' + v.customer_image + '" height="200" width="200"></a></div>' +
                        '<div class="media-body">' +
                        '<h4 class="media-heading">' + v.customer_username + '</h4>' +
                        '<div class="well">' + v.recent_message + '</div>' +
                        '<span style="display:inline;">' +
                        '<button type="button" class="btn btn-success" data-toggle="modal" data-target="#price_info" data-id="' + v.conversation_id + '" data-customer-id="' + v.customer_id + '">Send Invoice </button>' +
                        '<button type="button" class="btn btn-info order-ready" data-toggle="modal" data-target="#order_ready" data-id="' + v.conversation_id + '" data-customer-id="' + v.customer_id + '">Order Ready </button>' +
                        '<button type="button" class="btn btn-warning" data-toggle="modal" data-target="#confirm-order-close" data-id="' + v.conversation_id + '">Close Order </button>' +
                        '</span> </div> </div>'
                });
                $('#conversation_section').html(html);
                $.each(data.new_conv_trop, function (k, v) {
                    $('#trophy_' + v).parent().addClass('list-group-item-info');
                });
            }
        });
    }

    if (current_trophy_id == null) {
        current_trophy_id = $('.trophy_item').data('id');
    }


    WS4Redis({
        uri: 'ws://' + location.hostname + '/ws/barhop?subscribe-user',
        receive_message: receiveMessage,
        heartbeat_msg: '--heartbeat--'
    });

    // receive a message though the Websocket from the server
    function receiveMessage(msg) {
        startIndexRefresh();
    }


});