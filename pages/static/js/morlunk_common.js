$(document).ready(function() {
/*
	$('.controlpane').hover(function() {
		// Animate expansion to content size
		// Use workaround here:
		// http://stackoverflow.com/questions/5003220/javascript-jquery-animate-to-auto-height
		var curHeight = $(this).height();
		$(this).css({'height': 'auto'});
		var autoHeight = $(this).height();
		$(this).height(curHeight).stop().animate({
			'height': autoHeight
		});
	}, function() {
		// Contract to height of .panebanner
		var panebannerHeight = $('.panebanner').height();
		$(this).stop().animate({
			'height': panebannerHeight
		})
	});
*/
});

function buyItem(identifier) {
    $.get("/minecraft/store/buy/", { "item": identifier })
    .success(function(data) {
    	var response = jQuery.parseJSON(data)
        if(response.result == "success") {
            $().toastmessage('showSuccessToast', "Success! Your item has been sent to your stash.");
        } else if(response.result == "insufficient_funds") {
            $().toastmessage('showWarningToast', "You need more Paosos to purchase this item!");
        } else {
            $().toastmessage('showErrorToast', "An unexpected error occurred when purchasing this item!")
        }
    });

}