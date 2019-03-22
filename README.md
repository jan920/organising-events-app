# organising-events-app

Backend for application created for organising events. 

For running the program follow instructions in instal_instructions which describes how to run it locally, deploy to google cloud and run tests. However, any of the former won't run without "serviceAccountKey.json" containing firebase service account credentials which I am not providing from security reasons.

## Endpoints

All of the following endpoints are protected by Firebase authorisation

#### The app so far includes following endpoints:

##### USERS:

###### POST /user
Check if user exists and if yes return information about user in json otherwise create new profile

###### GET /user/`<userID>`
Return all info about user

###### POST /user/`<userID`</edit
Receive body in json and based on that change information about user in database

###### DELETE /user/`<userID>`
Delete user

###### GET /user/`<userID>`/followers
Return list in json of users followers

###### GET /user/`<userID>`/following
Return list in json of users being followed by this user

###### GET /user/`<userID>`/organised_events
Return list in json of events organised by this user

###### GET /user/`<userID>`/attending_events
Return list in json of events this user is attending

###### GET /user/`<userID>`/declined_events
Return list in josn of events this user has declined

###### GET /user/`<userID>`/visited_events
Return list in json of events this user has visited

###### POST user/`<userId>`/follow
Follow another user

##### EVENTS:
###### POST /event
Create new event in database based on info received in json

###### GET /event/`<eventID>`
Return info about an event in json

###### POST /event/`<eventID>`/edit
If user is organiser edit event based on information received in body

###### DELETE /event/`<eventID>`
Delete event if user is organiser of the event

###### POST /event/`<eventID>`/invite
invite users whose ids are received in json

###### POST /event/`<eventID>`/attend/
Add event into current users attending events

###### POST /event/`<eventID>`/came
Set that user just came to the event

###### POST /event/`<eventID>`/left
Add user into list of users who left the event

###### GET /event/`<eventID>`/guest_list
Return list of invited users

###### GET /event/`<eventID>`/attendees
Return list of attending users

###### GET /event/`<eventID>`/showed_up
Return list of users who showed

###### GET /event/`<eventID>`/left
Return list of users who left under key users

###### GET /event/`<eventID>`/posts
Return list of posts

##### SEARCH:

###### GET /search/user
Search user by name

###### GET /search/events
Search event by name|datetime|date|location

##### POSTS:
###### POST /event/`<eventID>`/post
Create post

###### GET /event/`<eventID>`/post/`<postID>`
Return information about post

###### POST /event/`<eventID>`/post/`<postID>`
Edit post

###### DELETE /event/`<eventID>`/post/`<postID>`
Delete post

##### FEED:

###### GET /feed
Return list of 10 events

