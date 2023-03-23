// Empty JS for your own code to be here

$(document).ready(function() {


    const $estimateList = $('#estimate-list');
    const $servicesOptions = $('#services-options');
    const serviceAPI = '/api/service/';

    const $addServiceBtn = $('#add-service-estimate');
    const $estimateForm = $('#estimate');
    const $estimateSubmitBtn = $('#estimate-submit-btn');
    const $estimateTotals = $('#estimate-total-cost');

    function returnPaymentDataURL(invoiceId) {
        return `/invoices/${invoiceId}/payment/data`
    }

    function createPaymentTableRow(paymentObject) {
        const dateString = paymentObject.date;
        const date = new Date(dateString);
        const formattedDate = date.toLocaleDateString('en-US', { month: '2-digit', day: '2-digit', year: 'numeric' });


        return `<tr>
        <th id="invoice-${paymentObject.invoice_id}-modal-payment-date">${formattedDate}</th>
        <td id="invoice-${paymentObject.invoice_id}-modal-payment-amount">$${paymentObject.amount}</td>
        <td id="invoice-${paymentObject.invoice_id}-modal-reference-num">${paymentObject.ref_num}</td>
        </tr>`
    };

    // update # counter on HTML tables
    function updateListCounter(tableRowName) {
        rows = $(`.${tableRowName}-rows`);
        // update the index column for each row
        rows.each(function(index) {
            if (!index) {
                index = 0
            }
            $(this).find(`#${tableRowName}-index`).text(index + 1);
        });
    };
    updateListCounter('service');
    updateListCounter('customer');
    updateListCounter('estimate');
    // show invoice info when invoice row is clicked 
    $(document).on('click', '#invoice-table-body td', async function(e) {
        const invoiceModalLabel = $('#invoiceModalLabel');
        const invoiceModalCustomerName = $("#invoice-modal-customer-name");
        const invoiceModalCustomerPhone = $("#invoice-modal-customer-phone");
        const invoiceModalCustomerEmail = $("#invoice-modal-customer-email");
        const viewInvoiceModalBtn = $("#view-invoice-modal-btn");
        const paymentInfoTableRow = $("#invoice-modal-tbody");

        let invoiceId = $(this).parent().attr('id').split('-')[1];
        let URL = returnPaymentDataURL(invoiceId);

        await axios.get(URL).then(function(response) {
            invoiceModalLabel.text(`Invoice # ${response.data.invoice_id}`);
            invoiceModalCustomerName.text(response.data.customer_name);
            invoiceModalCustomerPhone.text(response.data.customer_phone);
            invoiceModalCustomerEmail.text(response.data.customer_email);
            paymentInfoTableRow.html('');
            for (let payment of response.data.payment_info) {
                    noPaymentsForInvoice = false;
                    let tableRow = createPaymentTableRow(payment);
                    paymentInfoTableRow.append(tableRow);
                };

            if (response.data.payment_info.length == 0) {

                paymentInfoTableRow.append('<tr><td>N/A</td><td>No Payments Yet</td><td>N/A</td></tr>');
                }
            viewInvoiceModalBtn.attr('href', `invoices/${response.data.invoice_id}`)
        })


    })

    // redirect to estimate details when estimate TD is clicked
    $(document).on('click', '.estimate-rows', function() {
        let estimateId = $(this).attr('id').split('-')[1];
        window.location.href = `/estimates/${estimateId}`;
    })
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
    function createServiceRowHTML(serviceId, description, rate, unit) {
        return `<tr class="service-rows" id="service-${serviceId}-tr">
							<th id="service-index">
	
							</th>
							<td id="serv-${serviceId}-desc">
								${description}
							</td>
							<td id="serv-${serviceId}-rate">
								$${rate}
							</td>
							<td id="serv-${serviceId}-unit">
								${unit}
							</td>
							<td>
								<div class="btn-group" id="edit-delete-service">
									<button class="btn btn-sm btn-block btn-info" id="service-${serviceId}-edit" data-bs-toggle="modal" data-bs-target="#editService">Edit</button>
									<button class="btn btn-sm btn-block btn-danger" id="service-${serviceId}-delete" data-bs-toggle="modal" data-bs-target="#confirmServiceDelete">Delete</button>
								</div>
								
							</td>
						</tr>`
    };
    // update total price when making changes on estimate modal
    $(document).on('change', 'input[id$="-estimate-quantity"]', async function(){
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
        // if delete button clicked, remove that row on table and remove service from company's list of services
        if (action === 'delete') {
            $('#service-delete-btn').on('click', async () => {
                $(`#service-${serviceId}-tr`).remove()
                updateListCounter('service');
                // this route does not actually delete the service from the DB, but rather remove the company's access to it
                await axios.post(`/services/${serviceId}/delete`)
            }).then(function(response) {
                console.log(response)
            }
        );
        } 
        // if edit button clicked, get service info and preload into edit service form
        let desc = $(`#serv-${serviceId}-desc`);
        let rate = $(`#serv-${serviceId}-rate`);
        let unit = $(`#serv-${serviceId}-unit`);
        let comp_id = $("tbody[id^='services-for-company-']").attr('id').split('-')[3];
        console.log(comp_id)
        // inputs on modal edit service form
        let descInput = $('#description-edit-input');
        let rateInput = $('#rate-edit-input');
        let unitInput = $('#unit-edit-input');

        let descVal = desc.text().trim();
        let rateVal = parseFloat(rate
                                    .text()
                                    .trim()
                                    .split('$')[1]
                                );
        let unitVal = unit.text().trim();
        descInput.val(descVal);
        rateInput.val(rateVal);
        unitInput.val(unitVal);

        $('#service-edit-btn').on('click', async () => {
            desc.text(descInput.val());
            let newRow = createServiceRowHTML(serviceId, descInput.val(), parseFloat(rateInput.val()), unitInput.val());
            $(`#service-${serviceId}-tr`).replaceWith(newRow);
            updateListCounter('service');


            await axios.post(`/services/${serviceId}/edit`, {
                company_id: comp_id,
                description: descInput.val(),
                rate: rateInput.val(),
                unit: unitInput.val()
                })
                .then(function(response) {
                    console.log(response)
                    }
                );
            });
            
        });
    // disable service edit if fields are blank
    $(document).on('input', "input[id$='edit-input']", function() {
        let empty = false
        $('#description-edit-input, #rate-edit-input').each(function() {
            
            if ($(this).val() == '') {
                empty = true;
                }
            });
            if (empty) {
                $('#service-edit-btn').prop('disabled', true);
            } else {
                $('#service-edit-btn').prop('disabled', false);
            }
    });     
    
    $(document).on('click', "button[id^='customer-']", function() {
        let btnId = $(this).attr('id');
        let action = btnId.split('-')[2];
        let customerId = btnId.split('-')[1];

        // if delete button clicked, remove that row on table and remove customer from company's list of customers
        if (action === 'delete') {
            $('#customer-delete-btn').on('click', async () => {
                $(`#customer-${customerId}-tr`).remove()
                updateListCounter('customer');
                await axios.post(`/customers/${customerId}/delete`)
                }).then(function(response) {
                    console.log(response)
                    });
        } else if (action === 'edit') {
            // autofill edit form with current customer info
            $(".edit-customer input").each(function() {
                let fieldName = $(this).attr('name');
                let customerCol = $(`td[id$="${customerId}-${fieldName}"]`);
                let colValue = customerCol.text().trim();
                $(this).val(colValue);
            }); 

            $('#customer-edit-btn').on('click', async () => {
                await axios.post(`/customers/${customerId}/edit`, 
                {
                    full_name: $('#full-name-edit-input').val(),
                    address: $('#address-edit-input').val(),
                    tax_id: $('#tax-id-edit-input').val(),
                    phone: $('#phone-edit-input').val(),
                    email: $('#email-edit-input').val()
                }).then(function(response) {
                    console.log(response)
                    Object.entries(response.data).forEach(function([key, value]) {
                        console.log(key, value);
                        $(`#cust-${customerId}-${key}`).text(value)
                      });
                    })
            })
        }
    });
})
