/*
ROUTING.JS: JAVASCRIPT FILE FOR CONFIGURING "LEAFLET ROUTING" MAP AND USES POINT-TO-POINT
SHORTEST DISTANCE ALGORITHM TO REORDER WAYPOINTS

LEAFLET ROUTING PLOTS WAYPOINTS IN THE EXACT ORDER PASSED IN:
I USED POINT-TO-POINT SHORTEST DISTANCE CALCULATION TO AVOID TRAVELING SALES MAN PROBLEM.
IT APPEARS THERE IS NO STRAIGHTFORWARD METHOD ALREADY PROVIDED BY LEAFLET, LEAFLET ROUTING, OR
OSRM TO TAKE ON THE TRAVELING SALESMAN PROBLEM.

GEOLOCATION REQUIRES HTTPS, AND DOES NOT WORK ON HTTP (REQUIRES USER TO MANUALLY ENTER HTTPS SINCE
IDE USES HTTP BY DEFAULT)
*/

// GLOBAL VARIABLES
// stores starting waypoint (determined by driver's GPS location)
var start_waypoint = null;
// store locations/names of campers
var waypoints = [];
// stores reordered waypoints with initial starting and final_destination points (to beginning and end resp)
var new_waypoint_ordering = [];


// CREATE MAP ADD TILES TO IT
var map = L.map('map');

L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);


// CUSTOM MARKERS FOR WAYPOINTS
var childIcon = L.icon({
    iconUrl: '/static/child_pin_icon.png',
    iconSize: [40, 40], // size of the icon
});
var harvardIcon = L.icon({
    iconUrl: '/static/harvard_destination_icon.png',
    iconSize: [40, 40], // size of the icon
});
var startIcon = L.icon({
    iconUrl: '/static/starting_destination_icon.png',
    iconSize: [40, 40], // size of the icon
});


// HELPER METHOD: FINDS DISTANCE BETWEEN TWO WAYPOINTS
// reference to https://stackoverflow.com/questions/43167417/calculate-distance-between-two-points-in-leaflet
function getDistance(origin, destination) {
    // return distance in meters
    var lon1 = toRadian(origin.latLng.lng),
        lat1 = toRadian(origin.latLng.lat),
        lon2 = toRadian(destination.latLng.lng),
        lat2 = toRadian(destination.latLng.lat);

    var deltaLat = lat2 - lat1;
    var deltaLon = lon2 - lon1;

    var a = Math.pow(Math.sin(deltaLat/2), 2) + Math.cos(lat1) * Math.cos(lat2) * Math.pow(Math.sin(deltaLon/2), 2);
    var c = 2 * Math.asin(Math.sqrt(a));
    var EARTH_RADIUS = 6371;
    return c * EARTH_RADIUS * 1000;
}
function toRadian(degree) {
    return degree*Math.PI/180;
}


// HELPER METHOD: GETS STARTING_WAYPOINT BY DRIVER'S DEVICE GPS LOCATION
// GEOLOCATION REQUIRES HTTPS NOT HTTP CONNECTION TO WORK
function get_position() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function success(current_location) {
                let crd = current_location.coords;
                start_waypoint = L.Routing.waypoint(L.latLng(crd.latitude, crd.longitude), "start");
                create_map_points();
            },
            function error(err) {
                alert("load as HTTPS NOT HTTP");
                console.warn(`ERROR(${err.code}): ${err.message}`);
        });
    }
}


// HELPER METHOD: REORDERS WAYPOINTS INTO NEW_WAYPOINT_ORDERING BY POINT_TO_POINT SHORTEST DISTANCE
// I USE THIS ALGORITHM TO SOLVE TRAVELING SALESMAN BECAUSE CAMPERS MUST BE DROPPED OFF ASAP AND FIRST
function reorder() {
    // temporary variables
    var temp_index = 0;
    var temp_dist = [];
    var current_waypoint = null;

    // for each waypoint
    for (let i=0, size=waypoints.length; i < size; i++) {
        // reset variables
        temp_index = 0;
        temp_dist = [];

        // get the last waypoint visited
        current_waypoint = new_waypoint_ordering[new_waypoint_ordering.length - 1];

        // calculate all the distances from the last waypoint visited to all the other waypoints
        for (let i=0, size=waypoints.length; i < size; i++)
            temp_dist.push(getDistance(current_waypoint, waypoints[i]));

        // find the index of the smallest distance in the array temp_dist
        temp_index = temp_dist.indexOf(Math.min(...temp_dist));

        // add that element to the new_waypoint_ordering
        new_waypoint_ordering.push(waypoints[temp_index]);

        // remove the waypoint from waypoints, since we have already visited it
        waypoints.splice(temp_index, 1);
    }
}


// METHOD CALLED BY DRIVER_DASHBOARD.HTML ONLOAD
function create_map_points() {
    // retreive the names and lat/lng of the campers on the bus
	let elements = JSON.parse(String(document.getElementById("mapsection").getAttribute("value")));
	var latitudes = elements.latitudes;
	var longitudes = elements.longitudes;
	var pointnames = elements.pointnames;

    // retreive the final destination of the bus (camp counselor/staff drop off)
	let elements_final = JSON.parse(String(document.getElementById("hidden_value").getAttribute("value")));
	let latitude_final = elements_final.latitudes;
	let longitude_final = elements_final.longitudes;
	let pointname_final = elements_final.pointnames;
	var final_waypoint = L.Routing.waypoint(L.latLng(parseFloat(latitude_final[0].latitude), parseFloat(longitude_final[0].longitude)), pointname_final);

    // add the camper's names and destinations to waypoint array
    for (let i = 0, size=latitudes.length; i < size; i++)
        waypoints.push(L.Routing.waypoint(L.latLng(parseFloat(latitudes[i].latitude), parseFloat(longitudes[i].longitude)), pointnames[i].camper_name));

    //  first point on the map is the starting location (determined by driver's current GPS device location)
    new_waypoint_ordering.push(start_waypoint);

    // reorder the waypoints
    reorder();

    // final point of the waypoint is controlled by admin input (once all counselors have been dropped)
    new_waypoint_ordering.push(final_waypoint);

    // for location control
    var geocoder = L.Control.Geocoder.nominatim();

    // alas, create the route!
    L.Routing.control({
        addWaypoints: false,
        plan: L.Routing.plan(new_waypoint_ordering, {

            // custom marker reference from https://gis.stackexchange.com/questions/236934/leaflet-routing-control-change-marker-icon
            createMarker: function (i, start, n){
                var marker_icon = null;
                if (i == 0) {
                    marker_icon = startIcon;
                } else if (i == n -1) {
                    marker_icon =  harvardIcon;
                }
                else {
                    marker_icon = childIcon;
                }
                var marker = L.marker (start.latLng, {
                            draggable: false,
                            bounceOnAdd: false,
                            bounceOnAddOptions: {
                                duration: 1000,
                                height: 800,
                                function(){
                                    (bindPopup("camper_point").openOn(map));
                                }
                            },
                            icon: marker_icon
                });
                return marker;
            },
            routeWhileDragging: false,
            draggableWaypoints: false,
            geocoder: geocoder
        })
    }).addTo(map);
}