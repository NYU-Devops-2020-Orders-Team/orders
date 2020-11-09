$(function () {
    var row_num = 1;

    const CLEAR = 0;
    const UPDATE = 1;
    

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************
    // Updates the form with data from the response
    function update_form_data(res) {
        $("#order_id").val(res.id);
        $("#order_customer_id").val(res.customer_id);
        $("#order_created_date").val(res.created_date);

        row_num = 0;
        $("#order_items").empty();
        for (var i = 0; i < res.order_items.length; i++) { 
            add_row();
            var item = res.order_items[i];
            var prefix = "#order_item" + i + "_";
            $(prefix + "item_id").val(item.item_id);
            $(prefix + "product_id").val(item.product_id);
            $(prefix + "quantity").val(item.quantity);
            $(prefix + "price").val(item.price);
            $(prefix + "status").val(item.status);
        }
    }

    // Clears all form field
    function clear_form_data() {
        $("#order_customer_id").val("");
        $("#order_created_date").val("");

        row_num = 0;
        $("#order_items").empty();
        add_row();
    }

    // Adds one more row for row_num th item
    function add_row() {
        var prefix = "order_item" + row_num + "_";
        var code = `<div class="form-group"> \
                    <div class="col-sm-2"></div> \
                    <div class="col-sm-2"> \
                        <input type="text" class="form-control" id="${prefix}item_id" placeholder="Enter Item ID"> \
                    </div> \
                    <div class="col-sm-2"> \
                        <input type="text" class="form-control" id="${prefix}product_id" placeholder="Enter Product ID"> \
                    </div>\
                    <div class="col-sm-2">\
                        <input type="text" class="form-control" id="${prefix}quantity" placeholder="Enter Quantity"> \
                    </div> \
                    <div class="col-sm-2"> \
                        <input type="text" class="form-control" id="${prefix}price" placeholder="Enter Price"> \
                    </div> \
                    <div class="col-sm-2">  \
                        <select class="form-control" id="${prefix}status"> \
                        <option disabled selected value> -- select status -- </option> \
                            <option value="PLACED">Placed</option> \
                            <option value="SHIPPED">Shipped</option> \
                            <option value="DELIVERED">Delivered</option> \
                            <option value="CANCELLED">Cancelled</option> \
                        </select> \
                    </div> \
                    </div>`;
        $("#order_items").append(code);
        row_num += 1;
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // Updates form and message after done or fail
    function update_form_and_message(ajax, done_action, fail_action) {
        ajax.done(function(res){
            if (done_action == CLEAR) clear_form_data();
            else if (done_action == UPDATE) update_form_data(res);
            flash_message("Success");
        });

        ajax.fail(function(res){
            if (fail_action == CLEAR) clear_form_data();
            else if (fail_action == UPDATE) update_form_data(res);
            flash_message(res.responseJSON.message);
        });
    }

    // ****************************************
    // Delete an Order
    // ****************************************
    $("#delete-btn").click(function () {
        var order_id = parseInt($("#order_id").val());

        var ajax = $.ajax({
            type: "DELETE",
            url: "/orders/" + order_id,
            contentType: "application/json",
            data: '',
        })

        update_form_and_message(ajax, UPDATE, CLEAR);
    });


    // ****************************************
    // Retrieve an Order
    // ****************************************
    $("#retrieve-btn").click(function () {
        var order_id = parseInt($("#order_id").val());

        var ajax = $.ajax({
            type: "GET",
            url: "/orders/" + order_id,
            contentType: "application/json",
            data: ''
        })

        update_form_and_message(ajax, UPDATE, CLEAR);
    });


    // ****************************************
    // Ship an Order
    // ****************************************
    $("#ship-btn").click(function () {
        var order_id = parseInt($("#order_id").val());

        var ajax = $.ajax({
            type: "PUT",
            url: "/orders/" + order_id + "/ship",
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Deliver an Order
    // ****************************************
    $("#deliver-btn").click(function () {
        var order_id = parseInt($("#order_id").val());

        var ajax = $.ajax({
            type: "PUT",
            url: "/orders/" + order_id + "/deliver",
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Cancel an Order
    // ****************************************
    $("#cancel-btn").click(function () {
        var order_id = parseInt($("#order_id").val());

        var ajax = $.ajax({
            type: "PUT",
            url: "/orders/" + order_id + "/cancel",
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Ship an Item in an Order
    // ****************************************
    $("#ship-item-btn").click(function () {
        var order_id = parseInt($("#order_id").val());
        var item_id = parseInt($("#item_id").val()); 

        var ajax = $.ajax({
            type: "PUT",
            url: "/orders/" + order_id + "/items/" + item_id + "/ship",
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Deliver an Item in an Order
    // ****************************************
    $("#deliver-item-btn").click(function () {
        var order_id = parseInt($("#order_id").val());
        var item_id = parseInt($("#item_id").val()); 

        var ajax = $.ajax({
            type: "PUT",
            url: "/orders/" + order_id + "/items/" + item_id + "/deliver",
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Cancel an Item in an Order
    // ****************************************
    $("#cancel-item-btn").click(function () {
        var order_id = parseInt($("#order_id").val());
        var item_id = parseInt($("#item_id").val()); 

        var ajax = $.ajax({
            type: "PUT",
            url: "/orders/" + order_id + "/items/" + item_id + "/cancel",
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Add One More Row for Oder Items
    // ****************************************
    $("#add-row-btn").click(function () {
        add_row();
    });


    // ****************************************
    // Create an Order
    // ****************************************
    $("#create-btn").click(function () {
        var customer_id = parseInt($("#order_customer_id").val());
        var order_items = [];
        
        for (var i = 0; i < row_num; i++) {
            var prefix = "#order_item" + i + "_";
            var item = {
                "item_id": parseInt($(prefix + "item_id").val()), 
                "product_id": parseInt($(prefix + "product_id").val()), 
                "quantity": parseInt($(prefix + "quantity").val()), 
                "price": parseFloat($(prefix + "price").val()), 
                "status": $(prefix + "status").val()
            };
            order_items.push(item);
        }

        var data = {
            "customer_id": customer_id,
            "order_items": order_items
        };

        var ajax = $.ajax({
            type: "POST",
            url: "/orders",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update an Existing Order
    // ****************************************
    $("#update-btn").click(function () {
        var order_id = parseInt($("#order_id").val());
        var customer_id = parseInt($("#order_customer_id").val());

        var data = {
            "customer_id": customer_id
        };

        var ajax = $.ajax({
                type: "PUT",
                url: "/orders/" + order_id,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update an Existing Order Item
    // ****************************************
    $("#update-item-btn").click(function () {
        var order_id = parseInt($("#order_id").val());
        var item_id = parseInt($("#item_id").val());
        var data = {};

        for (var i = 0; i < row_num; i++) {
            var prefix = "#order_item" + i + "_";
            var id = parseInt($(prefix + "item_id").val());
            if (id == item_id) {
                data = {
                    "item_id": parseInt($(prefix + "item_id").val()), 
                    "product_id": parseInt($(prefix + "product_id").val()), 
                    "quantity": parseInt($(prefix + "quantity").val()), 
                    "price": parseFloat($(prefix + "price").val()), 
                    "status": $(prefix + "status").val()
                };
                break;
            }
        }

        var ajax = $.ajax({
                type: "PUT",
                url: "/orders/" + order_id + "/items/" + item_id,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Clear the form
    // ****************************************
    $("#clear-form-btn").click(function () {
        $("#order_id").val("");
        $("#item_id").val("");
        clear_form_data()
    });


    // ****************************************
    // List All Orders
    // ****************************************
    $("#list-all-btn").click(function () {
        var ajax = $.ajax({
            type: "GET",
            url: "/orders",
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            $("#search_results").empty();
            $("#search_results").append('<table class="table-striped" cellpadding="10">');
            var header = '<tr>'
            header += '<th style="width:10%">Order ID</th>'
            header += '<th style="width:10%">Customer ID</th>'
            header += '<th style="width:20%">Created Date</th>'
            header += '<th style="width:60%">Order Items</th></tr>'
            $("#search_results").append(header);
            var first_order = "";
            for(var i = 0; i < res.length; i++) {
                var order = res[i];
                var row = "<tr><td>"+order.id+"</td><td>"+order.customer_id+"</td><td>"+order.created_date+"</td><td>"+order.order_items+"</td></tr>";
                $("#search_results").append(row);
                if (i == 0) {
                    first_order = order;
                }
            }
            $("#search_results").append('</table>');

            // copy the first result to the form
            if (first_order != "") {
                update_form_data(first_order)
            }
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });
})
