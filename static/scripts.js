// Empty JS for your own code to be here

$(document).ready(function() {


    const $estimateList = $('#estimate-list');
    const $servicesOptions = $('#services-options');
    const serviceAPI = '/api/service/';
    const $addServiceBtn = $('#add-service-estimate');
    const $estimateForm = $('#estimate');
    const $estimateSubmitBtn = $('#estimate-submit-btn');
    const $estimateTotals = $('#estimate-total-cost');

    // update # counter on HTML tables
    function updateListCounter(tableRowClass) {
        rows = $(`.${tableRowClass}`);
        // update the index column for each row
        rows.each(function(index) {
            if (!index) {
                index = 0
            }
            $(this).find("#service-index").text(index + 1);
        });
    };
    updateListCounter('service-rows');

    async function getService(id) {
        let service = await axios.get(`${serviceAPI}/${id}`)
        if (service.data.id > 0) {
            return service;
        }
        return null;
    };

    function updateEstimateTotalHTML() {
        var listItems = $(".cost");
        let cost = 0;
        listItems.each(function(idx, span) {
            let itemPrice = $(span).text();
            cost += parseFloat(itemPrice);
            });

            $('#estimate-total').text(String(cost));
    };

    function createListHTML(content) {

        return `<li id="service-${content.data.id}-estimate" class="list-group-item d-flex justify-content-between align-items-start">
        <button class="mx-2 btn btn-sm btn-outline-danger" id="remove-estimate-item">Remove</button>
                <div class="ms-2 me-auto">
                    <div><b>${content.data.description}</b></div>
                    <div>
                    <label for"service-${content.data.id}-estimate-quantity">Quantity:</label>
                    <input class="form-control" id="service-${content.data.id}-estimate-quantity" type="number" value="1" min="0">
                    
                    </div>
                    
                </div>
                
                <span>Price:</span>
                <span id="estimate-price-${content.data.id}" class="cost mx-2 badge bg-success rounded-pill">${content.data.rate}</span>
                
                </li>`
    };
    // update total price when making changes on estimate modal
    $(document).on('change', ':input[type="number"]', async function(){
        let listId = this.id;
        let serviceId = listId.split('-')[1];
        let service = await getService(serviceId);
        let servicePrice = service.data.rate;
        let quantity = this.value;
        $(`#estimate-price-${serviceId}`).text(parseInt(quantity) * parseFloat(servicePrice));
        updateEstimateTotalHTML();
        
    } );
    // removes list items on estimate modal on click
    $(document).on('click', 'button#remove-estimate-item', function() {
        $(this).closest('li').remove();
        updateEstimateTotalHTML();
    });
    // disables the save changes button unless a due date is provided
    $('#invoice-due-date').on('change', function() {
        if ($('#invoice-due-date').val() != '') {
            $('button.btn-primary').attr('disabled', false);
        } else {
            $('button.btn-primary').attr('disabled', true);
        }

        
    })
    // create invoice from estimate 
    $('#confirm-invoice').on('click', 'button.btn-primary', async function() {
        let estimateId = $(this).attr('id');
        estimateId = estimateId.split('-')[4];
        let dueDate = $('#invoice-due-date').val()

        await axios.post(`/invoices/${estimateId}/finalize`, {
            due: dueDate
        }
        ).then(function(response) {
                if (response.status == 200) {
                    window.location.href = `/invoices/${estimateId}`;
                }
            }
        );
    });
    
    $addServiceBtn.on('click', async function(e) {
        e.preventDefault()
        let id = $servicesOptions.val();
        let service = await getService(id);
        let listHTML = createListHTML(service);
        $estimateList.append(listHTML);
        updateEstimateTotalHTML();
    
    });

    $estimateSubmitBtn.on('click', async function(e) {

        // e.preventDefault();
    

        let serviceIdQuantityPair = [];
        // get selected Customer's id
        let custId = $('#customer-select').val();
    
        // Loop through each list item in the ordered list
        $("#estimate-list li").each(function() {
            // Get the value of the service ID
            let sId = $(this).attr('id');
            // the service id is formatted in HTML as 'service-1-estimate' so split() is used to get the '1' by itself
            sId = sId.split('-')[1];

            let serviceQuantity = $(`#service-${sId}-estimate-quantity`).val()
            
            // Add the service ID to the array
            serviceIdQuantityPair.push({serviceId: sId, quantity: serviceQuantity});
        });

        
        await axios.post('invoices/', {
            services: serviceIdQuantityPair,
            customerId: custId
        }
        ).then(function (response) {
            if (response.status == 200) {
                window.location.href = `/estimates/${response.data.id}`;
            }
          })
    
        
    });

    // on click of edit or delete button /services/ page
    $(document).on('click', "button[id^='service-']", function() {
        let btnId = $(this).attr('id');
        let action = btnId.split('-')[2];
        let serviceId = btnId.split('-')[1];
        if (action === 'delete') {
            $('#service-delete-btn').on('click', async () => {
                $(`#service-${serviceId}-tr`).remove()
                updateListCounter('service-rows');
                await axios.post(`/services/${serviceId}/delete`)
            }).then(function(response) {
                console.log(response)
            }
        );
        } 
        let desc = $(`#serv-${serviceId}-desc`);
        let rate = $(`#serv-${serviceId}-rate`);
        let unit = $(`#serv-${serviceId}-unit`);
        let descInput = $('#description-edit-input');
        let rateInput = $('#rate-edit-input');
        let unitInput = $('#unit-edit-input');

        let descVal = $(`#serv-${serviceId}-desc`)
                                                .text()
                                                .trim();
        let rateVal = parseFloat($(`#serv-${serviceId}-rate`)
                                                        .text()
                                                        .trim()
                                                        .split('$')[1]);
        let unitVal = $(`#serv-${serviceId}-unit`)
                                                .text()
                                                .trim();
        descInput.val(descVal);
        rateInput.val(rateVal);
        unitInput.val(unitVal);

        $('#service-edit-btn').on('click', async () => {
            desc.text(descInput.val())

            await axios.post(`/services/${serviceId}/edit`)
            })
            .then(function(response) {
                console.log(response)
                }
            );
             
    })

});




