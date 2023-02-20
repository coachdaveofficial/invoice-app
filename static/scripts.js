// Empty JS for your own code to be here
$(document).ready(function() {


    const $estimateList = $('#estimate-list');
    const $servicesOptions = $('#services-options');
    const serviceAPI = '/api/service/'
    const $addServiceBtn = $('#add-service-estimate')


    async function getService(id) {
        let service = await axios.get(`${serviceAPI}/${id}`)
        if (service.data.id > 0) {
            console.log(service);
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
        // return `<li id="service-${content.id}-estimate" class="list-group-item">${content.data.description}<span class="badge bg-primary text-end">${content.data.price_per_unit}</span></li>`

        return `<li id="service-${content.data.id}-estimate" class="list-group-item d-flex justify-content-between align-items-start">
                <div class="ms-2 me-auto">
                    <div><b>${content.data.description}</b></div>
                    <label for"service-${content.data.id}-estimate-quantity">Quantity:</label><input class="form-control" id="service-${content.data.id}-estimate-quantity" type="number" value="1" min="0">
                </div>
                <span>Price:</span>
                <span id="estimate-price-${content.data.id}" class="cost badge bg-primary rounded-pill">${content.data.price_per_unit}</span>
                </li>`
    }

    $(document).on('change', ':input[type="number"]', async function(){
        let listId = this.id;
        let serviceId = listId.split('-')[1];
        let service = await getService(serviceId);
        let servicePrice = service.data.price_per_unit;
        let quantity = this.value;
        $(`#estimate-price-${serviceId}`).text(parseInt(quantity) * parseFloat(servicePrice));
        updateEstimateTotalHTML();
        
    } );

    
    $addServiceBtn.on('click', async function(e) {
        e.preventDefault()
        let id = $servicesOptions.val();
        let service = await getService(id);
        let listHTML = createListHTML(service);
        $estimateList.append(listHTML);
        updateEstimateTotalHTML();
    
    })

})




