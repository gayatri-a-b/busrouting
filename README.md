# busrouting

A Flask-based website that solves an application of the Traveling Salesman Problem. Given a list input of addresses (a bus roster), a starting point, and an ending point, the application generates an interactive map with directions for getting from point-to-point the shortest distance. 
This was my CS50 final project.

## Accessing the application 
Please use Chrome web brower.
Visit https://ide50-gayatrib.cs50.io:8080/login.
(To start the application, in the terminal, `flask run` from within the `project/implementation` folder)

There are two fixed login combinations
1) ADMIN PORTAL
username: admin
password: ilovestudents
2) DRIVER PORTAL
username: admin
password: ilovedriving

Once logged in, there is a navigation bar at the top.


### ADMIN PORTAL
1) `/admin_dashboard` or `/`
PURPOSE: taking attendance to mark which students will be on the bus. Changes made here (upon resetting or locking in the attendance) will be automatically reflected under "Bus Roster" and "NOT ON BUS" on this page, and in the map in /driver_dashboard.

* Bus Attendance: select the checkmarks for which students will be riding the bus Hit "LOCK" to lock in the attendance.
Hit "RESET" to reset the attendance.


2) `/camper_registration`
PURPOSE: registering/unregistering campers. Changes made here will be automatically reflected on this page and in /admin_dashboard

* Add Camper: enter the name and drop-off location for each camper. Hit "REGISTER" to register the camper.
* Remove Camper: select which camper to remove. Hit "REMOVE" to remove the camper.


3) `/driver_dashboard`
PURPOSE: show the best point-to-point route for dropping off the camper at their respective drop-off locations

* Automatically updates/populates map with campers coming on the bus, starting location, and final destination. Leaflet Routing-provided navigation itinerary with ability for the driver to click x for the campers dropped off. Blue dot traces the route.
* Adding points to the map or dragging the route is intentionally disabled.


4) `/driver_destination`
PURPOSE: allows admin to change the address of the final stop for the bus (dropping off counselors). Changes will be reflected on the page under "Current Destination Address" and in the Harvard waypoint on the map in /driver_dashboard.

* Set Destination: enter address. Hit "SET/RESET"


5) `/logout`
PURPOSE: facilitate logout

* Log out feature located in navigation bar.


### DRIVER PORTAL
1) `/driver_dashboard` or `/
PURPOSE: show the best point-to-point route for dropping off the camper at their respective drop-off locations

* Automatically updates/populates map with campers coming on the bus, starting location, and final destination. Leaflet Routing-provided navigation itinerary with ability for the driver to click x for the campers dropped off. Blue dot traces the route.
natigation bar allows.
* Adding points to the map or dragging the route is intentionally disabled.


2) `/logout`
PURPOSE: facilitate logout
* Log out feature located in navigation bar.


## MAPS HTTPS REQUIREMENT
The map feature requires a HTTPS connection. If you login with the default HTTP then the screen will prompt you to go to HTTPS. This means litterally go into the url and type "HTTPS://" in front of the url.
This requirement is a safety feature of contemporary browsers, and you have to do this manually because the CS50 IDE directs URLs to using HTTP by default.

## Note
### Comment
The DRIVER does not have access to any of the ADMIN's content. They can only access `/driver_dashboard`.
The ADMIN however, can access all of the DRIVER's content (which is just /driver_dashboard).
This is for security reasons, dealing with minors.

### The Motivation Behind `busrouting`
I had a specific problem in mind that I wanted to solve when I designed this application. It's intended to be a solution for summer camps, such at the Phillips Brooks House Association Native American Youth Enrichment Program. Every morning and after the Harvard Shuttle would pick-up and drop-off camper to and from their individual household--located all over Boston. The Shuttle would always have as one point--whether start or end--Johnston Gate. But the other start/end point would often vary, coming from fieldtrips all over the place or the Condon School. Moreover, the bus roster was always changing--even between morning and evening--based on each student's individual family situation. And coming from fieldtrips, the usual bus route was completely different.

The bus driver often got lost, or we would go to stops that we didn't need to, or we would drive all the way back to the school after a fieldtrip just to stick to the bus route. And there was always a communication gap between the driver and us, the counselors. Most morning and afternoons took two hours or more each.

This website application aims to solve that problem by making the route dynamic, and merging the step of taking attendance and routing. Moreover, the counselors can keep an eye on the campers while track of the route on their phone.

### Acknoledgement
This website derives its concepts from the CS50 Finance problem set.
