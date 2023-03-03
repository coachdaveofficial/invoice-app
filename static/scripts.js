// Empty JS for your own code to be here

$(document).ready(function() {


    const $estimateList = $('#estimate-list');
    const $servicesOptions = $('#services-options');
    const serviceAPI = '/api/service/';
    const $addServiceBtn = $('#add-service-estimate');
    const $estimateForm = $('#estimate');
    const $estimateSubmitBtn = $('#estimate-submit-btn');
    const $estimateTotals = $('#estimate-total-cost');


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
        <button class="btn-sm btn-danger" id="remove-estimate-item">Remove</button>
                <div class="ms-2 me-auto">
                    <div><b>${content.data.description}</b></div>
                    <div>
                    <label for"service-${content.data.id}-estimate-quantity">Quantity:</label>
                    <input class="form-control" id="service-${content.data.id}-estimate-quantity" type="number" value="1" min="0">
                    
                    </div>
                    
                </div>
                
                <span>Price:</span>
                <span id="estimate-price-${content.data.id}" class="cost badge bg-primary rounded-pill">${content.data.price_per_unit}</span>
                
                </li>`
    };

    $(document).on('change', ':input[type="number"]', async function(){
        let listId = this.id;
        let serviceId = listId.split('-')[1];
        let service = await getService(serviceId);
        let servicePrice = service.data.price_per_unit;
        let quantity = this.value;
        $(`#estimate-price-${serviceId}`).text(parseInt(quantity) * parseFloat(servicePrice));
        updateEstimateTotalHTML();
        
    } );
    // the function below removes list items on estimate modal on click
    $(document).on('click', 'button#remove-estimate-item', function() {
        $(this).closest('li').remove();
        updateEstimateTotalHTML();
    });

    $('#confirm-invoice').on('click', 'button.btn-primary', async function() {
        let estimateId = $(this).attr('id');
        estimateId = estimateId.split('-')[4];

        await axios.post(`/invoices/finalize/${estimateId}`).then(
            function(response) {
                if (response.status == 200) {
                    window.location.href = `/invoices/${estimateId}`;
                }
            }
        )
    })
    
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

        
        await axios.post('invoices/add', {
            services: serviceIdQuantityPair,
            customerId: custId
        }
        ).then(function (response) {
            if (response.status == 200) {
                window.location.href = `/estimates/${response.data.id}`;
            }
          })
    
        
    });

    

})




