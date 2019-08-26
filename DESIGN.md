DESIGN.MD: DOCUMENT FOR EXPLAINING TECHNICAL CHOICES

There is a small story to the motivation behind my project.                                                                                                                                                  otivation behind my project.

This past summer I worked at the Native American Youth Enrichment Program (NAYEP) through
the Phillips Brooks House Association. I came in to the actual camp at the end (I broke
my jaw during training and had to fly home after surgery, so it took me a few weeks to
recover and return), and I was put on evening shuttle duty. NAYEP is different from other
SUP programs in that it isn't geographically associated--indigeonous youth come from all
over Greater Boston. So, we used Harvard's shuttles to pick kids up from all over the place.
I would leave for camp around 6 am and return around 6 pm!

Since I came in at the end and I was sick, I didn't realize how this was actually a problem.
Unlike during the school year when the drivers can use Rider, there was no map application or
physical look for the shuttle driver to follow. Since not every camper came every day, the
route would actually alter every day, even between morning and afternoon, based on the bus
attendance. The driver was getting absolutely lost not only getting from point to point, but
also going to points that were completely out of the way because he was just following the
formula of the route. (In fact, he was using Google maps on his personal phone to input point
to point). I came in at week 4.5 of camp after surgery, so he did this twice a day for 20-40
campers for 8 weeks. To make matters worse, we would do fieldtrips 1-2x per week where the driver
would attempt to get to the route from wherever in Massachusetts we were. So, at times we would
drive past several campers houses, and they would get dropped off an hour later! Just because the
driver would route to the first stop of this formulaic route he was following. Try to imagine the
look on a tired 8-year old's face who has just run around for hours at a water park, seeing their
house fly by. The repercussions run deep. These are young children who don't know who to attribute
blame to, and they act up believing they were treated unfairly--you punish them and the effect
snowballs.

The day I realized that was around the time I reflected on taking CS50, and I set my mind in
August to develop some type of application for the camp. I believe I accomplished that goal!


My bus-application is built around the central principal that an administrator without any CS
knowledge can simply take the attentance of his/her students, and that action of taking attendance
will dynamically generate a route that the bus driver and administrator can follow. The bus driver
can follow the route to drive, and the administrator can follow the route to know which student
gets off next. In NAYEP, we text the parents a time estimate of when we'll be at their house. By
splitting up the administrator and driver logins, the bus driver can use the map to do their job
and the administrator can use it to do their job--independent of each other. Since we are dealing
with minors, I wanted the administrator to have the power, and the bus driver to only have access
to the map.

IMPLEMENTATION.DB
USERS: stores two columns (username and hash). There are two inputs in this database: admin and driver.
CAMPERS: stores five columns. There are the values for each camper, but I also stores the final_destination
latitude and longitude in here (under the camper_name of final_destination). Since I store
final_destination here, below in /ADMIN_DASHBOARD.HTML when I iterate through the database printing out campers
I have to ensure in JINJA that final_destination is printed out as a camper. It's set to off_bus = False by
default since I want the final destination to be appended at the end of my Leaflet Routing waypoint array. So,
I have to pass it through to ROUTING.JS a different way.

camper_name (text)
address (text)
on_bus (text, True for on_bus and False by default)
latitude (double_precision)
longitude (double_precision)


Access coded thru if/else check of session in Python flask).


/CAMPER_REGISTRATION.HTML
In my application, the administrator has a page where to enter camper names/addresses, and remove them.
I do this in /CAMPER_REGISTATION.HTML. There are two input fields w/ submit buttons: registar and remove,
and one JINJA template that dynamically spits out all the registared campers upon any changes. If a button
is hit, I have to get which one it is: REGISTAR or REMOVE, then check if the inputs are valid. Since these
inputs are going straight to my campers database, I insert the address, but I also immediately convert it
to latitude and longitude. If the lat/lng conversion doesn't output a valid number, it means the address
isn't valid and won't work in Leaflet Routing waypoints (this is the API I used for route plotting). So,
checking for this here and immediately outputing an error is crucial to do upon registration.
Of course if you add things, you must be able to remove them, the REMOVE just undoes what REGISTAR inputs.

/ADMIN_DASHBOARD.HTML and SCRIPTS.JS
The campers inputted from /CAMPER_REGISTRATION.HTML go into the camper database in IMPLEMENTATION.DB. So,
this page uses JINJA to iterate through printing through all the campers as checkboxes, and then printing
all of the campers in either a list of campers on bus and off bus based on the value of ON_BUS DB value.
In taking attendance there are two actions, LOCK-attendance or RESET-attendance. ADMIN_DASHBOARD.HTML uses
the JS file SCRIPTS.JS. Here the lock action makes the commiting change to change the ON_BUS value in the DB.
So, RESET actually calls LOCK. The most challenging part was not making the changes in the DB but reflected
the changes to the lists on the page itself. The AJAX in LOCK forces the page to reload in the success function.

/DRIVER_DESTINATION.HTML and ROUTING.JS and /DRIVER_DASHBOARD.HTML
These three files deal directly with the route: taking the values of the ON_BUS campers and organizing the
waypoints in an efficient order and displaying the route via LEAFLET ROUTING MACHINE. Disclaimer: Leaflet
Routing Machine is very much a project, so it has a ton of bugs, but none the-less it was fun to work with and
sort through all the threads where the creator was showing workarounds to mistakes his users are finding.
The way Leaflect routing works is that it displays a route connecting the waypoints in exactly the order you
send in the waypoint array. So, I was faced with the traveling salesman problem: my starting destination is
going to be determined by geolocation, and my final destination will be where is inputted into /DRIVER_DESTINATION_HTML.
I split up it such as this so that, if the driver is returning from a fieldtrip, and the camp staff are going to the
school instead of campus after dropping off, the maps will autoroute from the fieldtrip destination to create a
route to drop of all the campers taking the bus, and then go to a different final_destination upon the admin's
camp organization requirements.
ROUTING.JS is interested in ordering the waypoints. I had tough time with grabbing the starting position by GPS
with navigator.geolocation because CS50 IDE uses HTTP by default, and the browsers have a security limit that it
will not permit location access without the site using HTTPS. Ends up that to get HTTPS connection needs a physical
entering of the HTTPS:// in front of the URL. So, I wanted this ordering to occur ONLOAD of the map (in
/DRIVER_DASHBOARD.HTML), so that the an error alert can prompt telling the user to connect via HTTPS, and the calculation
can occur any time that page is reloaded. So if the bus moves and wanted to recalculate the route, all the driver has
to do is reload the page.
So upon loading, navigator.geolocation grabs the location of the device and appends it to a new empty array. Then the
waypoints, which is a L.Routing.waypoint Objects array is fed distance by distance iteratively to go from point-to-point
by the shortest distance. I understand this solution to the traveling salesman has limitations, but it was the best I
came up with! The reordered waypoints are added one by one to the new waypoints array, and the last waypoint added
post-reordering is the final_destination that the camp administrators want to go after dropping all the campers off. In
SUP, we don't care to wind our way back home: our priority is to get the campers off ASAP to their families and then hit
the road to wherever we go. So the waypoints array is ordered accordingly.
L.Routing.control creates the map with the new waypoints array. I created my own markers so that it's clear where we are
at in the route, and enabling geocoder allows the names to pop-up in he navigator so that the driver can x-mark the stops
visited. There is an error in the Leaflet Routing Machine API so that, if you don't want the route to be dragable, you have
to place the attribute before the function to which it belongs for only that element. Overall, this was challenging.


REFLECTION
If I could make this a larger project (and had the cash), I would really love to translate it into a mobile application
that uses Google maps or iPhone maps to route. I was really bumbed about having to use Leaflet Routing instead of the Google
Maps API. Especially because Leaflet Routing is so new it's so new and has a lot of bugs, and there are huge limitations on
what it cannot do. I want to be able to keep track of the point on the route so that a text message can be generate to the
parent's phone based on the time to their house along the route. I wish there was a solution to the traveling salesman in
OSRM (there's a very new one but it has so little documentation that I don't think there are enough threads to incorportate
it into Leaflet Routing Machine--which uses Leaflet which uses OSM!).

I'm excited I got the functionality! I think the next step is getting the dynamic route-to phone messaging. It was a lot
to do for one person, but now I have a much better handle on how to use Python flask, squlite, and communicating between
the server and JS.