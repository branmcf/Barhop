$(function () {

    function errorHandler() {

    }

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

    var current_trophy_id = null;
    var order_array = []

    function startIndexRefresh() {
        
        $('.orderReadyCol').each(function(i, obj) {
              order_array.push(obj.id);
        });

        $.ajax({
            url: '/account/new_order/',
            type:'POST',
            data:{
              order_data:order_array.toString(),
            },
            success: function (data){
              if (data['error_msg']){
                console.log("error message");
              }
              else{  
                $("#emptyReady").remove();
                $('#unassignedCol').append(data);
              }      
            }
        }); 

    }


    function updateOrder(order_id) {

        $.ajax({
          url: '/account/order_ready/',
          type:'POST',
          data:{
            order_id:order_id,
            'flag': 'flag'
          },
          success: function (data){
            if (data['error_msg']){
              console.log("error message");
            }
            else{          
              order_id = order_id.toString();
              $(".ready_"+order_id).remove();
              $("#emptyClose").remove();
              if ($(".close_"+order_id.toString()).length) {
                console.log("");
                }
              else{
                $('#orderListToClose').append(data);
                }              
              $("#overlayID").hide();
            }
          }
        });

    }

    WS4Redis({
        uri: 'ws://' + window.location.host + '/ws/barhop?subscribe-user',
        receive_message: receiveMessage,
        heartbeat_msg: '--heartbeat--'
    });

    // receive a message though the Websocket from the server
    function receiveMessage(msg) {
        startIndexRefresh();
        if (msg.indexOf('ready') > -1){
            $(msg).remove();
            order_id = msg.split("_")[1];
            updateOrder(order_id)
        }
        if (msg.indexOf('close') > -1){
            $(msg).remove();
        }
    }

    function removeOrder(msg) {}
               
        // if(html){
        //     alert("aaa");
        //     $('#orderListToClose').append(html);
      
});