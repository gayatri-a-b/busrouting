/*
SCRIPTS.JS: JAVASCRIPT FILE FOR FUNCTIONALITY OF ADDING/REMOVING CAMPERS
*/

// GLOBAL VARIABLES
// keeps track of lock's toggle functionality
var toggle_value = false;
// stores names of all campers on_bus
var camper_names = [];


// METHOD CALLED BY ADMIN_DASHBOARD.HTML "LOCK BUTTON" ONSUBMIT
function lock() {
	// get the names of all campers
    let items = document.getElementsByName('bus_campers');

	for(let i=0; i<items.length; i++){
		// add all the campers coming on the bus to camper_names
		if(items[i].checked)
			camper_names.push(items[i].value);
		// disable all the checkboxes when lock() is called
		if(items[i].type=='checkbox')
		    items[i].disabled=!toggle_value;
    }

    // change the toggle value
	toggle_value = !toggle_value;

	// CONNECTING TO APPLICATION.PY VIA POST
	// THIS FORCES THE PAGE TO RELOAD ONCE LOCK HAS BEEN HIT (FORCES JINJA TO RELOAD THE CAMP ROSTERS)
	// reference to my co-worker Salem who just got a job at Exxon!
	$.ajax({
		type: "POST",
		contentType: "application/json; charset=utf-8",
		url: "/admin_dashboard",
		data: JSON.stringify({bus_campers: camper_names, "attendance_action": 'lock'}),
		success: function (data) {
			// FORCE RELOAD
			window.location.reload(true);
		},
		error: function() {
			alert("error");
		},
		dataType: "json"
	});
}


// METHOD CALLED BY ADMIN_DASHBOARD.HTML "RESET BUTTON" ONSUBMIT
function reset() {
	// take all the camper_names off the bus
	camper_names = [];

	// uncheck all the boxes
    let items=document.getElementsByName('bus_campers');
		for(let i=0; i<items.length; i++){
			if(items[i].type=='checkbox')
			    items[i].checked=false;
	}

	// call lock to update and the page
	lock();
}