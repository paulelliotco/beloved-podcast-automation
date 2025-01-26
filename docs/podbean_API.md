Podbean API
Authentication
Login Dialog - 1. Invoking the Login Dialog
This is for third-party apps to connect to Podbean in order to manage a user's podcast. To manage your own podcast via API, Please go to 5. Client Credentials and 6. Get Multiple Podcasts Tokens

get
https://api.podbean.com/v1/dialog/oauth
Example usage
https://api.podbean.com/v1/dialog/oauth?redirect_uri=http%3A%2F%2FYOUR_ENCODED_REDIRECT_URL&scope=podcast_read+podcast_update+episode_publish+episode_read&response_type=code&client_id=YOUR_CLIENT_ID
Header
Field	Type	Description
User-Agent	String	
It contains the name and version number of the browser or other client application. Servers can use this string to identify the client application and version information.

User-Agent
User-Agent: MyApp/1.2.3 (Example)
Parameter
Field	Type	Description
client_id	String	
The client identifier.

redirect_uri	String	
The URL that you want to redirect the person logging in back to.

Note : Because this parameter is passed by using URL query string, you need to manually urlencode it or use standard function like http_build_query to build query string

scope	String	
A space separated list of Permissions to request from the person using your app.

stateoptional	String	
An arbitrary unique string created by your app to guard against Cross-site Request Forgery.

Size range: 0..1000

response_typeoptional	String	
Determines whether the response data included when the redirect back to the app occurs is in URL parameters or fragments.

Allowed values: "code", "token"

Request Code Success : Response 302 Found with Get Params
Field	Type	Description
code	String	
Authentication code The code is used to exchange for an Access Token

Request Token Success : Response 302 Found with URL fragment Params
Field	Type	Description
access_token	String	
expires_in	Int	
scope	String	
Returns a space separated list of all Permissions granted to the app by the user at the time of login.

token_type	String	
Allowed values: "Bearer"

Success-Response when response_type=code
Success-Response when response_type=token
HTTP/1.1 302 Found
YOUR_REDIRECT_URI?code=Mclai20remJNIal1
Error : Response 302 Found with Get Params
Name	Description
error	
The type of identification errors.

error_description	
Error User Denied
Error Params Invalid
HTTP/1.1 302 Found
YOUR_REDIRECT_URI?error=access_denied&error_description=The+user+denied+access+to+your+application
Exchanging Code for an Access Token - 2. Exchanging Code for an Access Token
To get an access token, make an HTTP GET request to the following OAuth endpoint:

post
https://api.podbean.com/v1/oauth/token
Example usage
curl -u YOUR_CLIENT_ID:YOUR_CLIENT_SECRET \
 https://api.podbean.com/v1/oauth/token \
  -X POST -d 'grant_type=authorization_code&code=CODE&redirect_uri=YOUR_REDIRECT_URI'
Header
Field	Type	Description
Authorization	String	
HTTP Basic authentication use client_id as username and use client_secret as password.

User-Agent	String	
It contains the name and version number of the browser or other client application. Servers can use this string to identify the client application and version information.

Authorization
User-Agent
Authorization: Basic dGVdF9jbGllbnRaWQ1MTp0ZXN0X2NsaWVdF9zZWNyZQ=
Parameter
Field	Type	Description
code	String	
Authorization Code from above request

grant_type	String	
Allowed values: authorization_code

redirect_uri	String	
The parameter received from the Login Dialog redirect above.

Response JSON format
Field	Type	Description
access_token	String	
refresh_token	String	
token_type	String	
Allowed values: Bearer

scope	String	
expires_in	Int	
Success-Response
HTTP/1.1 200 OK
{
  "access_token": YOUR_ACCESS_TOKEN,
  "token_type": TYPE,
  "expires_in":	SECONDS_TIL_EXPIRATION
  "token_type": "Bearer",
  "scope":"podcast_read episode_read podcast_update episode_publish",
  "refresh_token": REFRESH_TOKEN
}
Invalid code
HTTP/1.1 400 Bad Request
{
     "error": "invalid_grant",
     "error_description": "Authorization code doesn't exist or is invalid for the client"
 }
Inspecting Access Tokens - 3. Inspecting Access Tokens
Whether or not your app uses code or token as your response_type from the Login dialog, it will have received an access token. You can perform automated checks on these tokens using a API endpoint:

get
https://api.podbean.com/v1/oauth/debugToken
Example usage
curl -u YOUR_CLIENT_ID:YOUR_CLIENT_SECRET \
 https://api.podbean.com/v1/oauth/debugToken \
  -G -d 'access_token=YOUR_ACCESS_TOKEN'
Header
Field	Type	Description
Authorization	String	
HTTP Basic authentication use client_id as username and use client_secret as password.

User-Agent	String	
It contains the name and version number of the browser or other client application. Servers can use this string to identify the client application and version information.

Authorization
User-Agent
Authorization: Basic dGVdF9jbGllbnRaWQ1MTp0ZXN0X2NsaWVdF9zZWNyZQ=
Parameter
Field	Type	Description
access_token	String	
The token you need to inspect.

Response JSON format
Field	Type	Description
app_id	String	
app_name	String	
expires_in	Int	
scopes	String	
is_valid	Boolean	
issued_at	Int	
A space separated list of Permissions to request from the person using your app.

podcast_id	String	
Success-Response:
HTTP/1.1 200 OK
{
  "app_id": "0ru3DTJP",
  "app_name": "podbean test app",
  "expires_in": 1484894277,
  "is_valid": true,
  "issued_at": 1484289477,
  "scopes": "podcast_read episode_read podcast_update",
  "podcast_id": "90dbib3uEd"
 }
Invalid code:
HTTP/1.1 400 Bad Request
{"error":"invalid_token","error_description":""}
Refreshing Tokens - 4. Refreshing Tokens
You will need to periodically refresh your access tokens when they expire:

post
https://api.podbean.com/v1/oauth/token
Example usage
curl -u YOUR_CLIENT_ID:YOUR_CLIENT_SECRET \
https://api.podbean.com/v1/oauth/token \
-X POST -d 'grant_type=refresh_token&refresh_token=REFRESH_TOKEN'
Header
Field	Type	Description
Authorization	String	
HTTP Basic authentication use client_id as username and use client_secret as password.

User-Agent	String	
It contains the name and version number of the browser or other client application. Servers can use this string to identify the client application and version information.

Authorization
User-Agent
Authorization: Basic dGVdF9jbGllbnRaWQ1MTp0ZXN0X2NsaWVdF9zZWNyZQ=
Parameter
Field	Type	Description
refresh_token	String	
grant_type	String	
Allowed values: refresh_token

Response JSON format
Field	Type	Description
access_token	String	
token_type	String	
Allowed values: Bearer

scope	String	
expires_in	Int	
Success-Response
HTTP/1.1 200 OK
{
  "access_token": YOUR_ACCESS_TOKEN,
  "token_type": TYPE,
  "expires_in":	SECONDS_TIL_EXPIRATION
  "token_type": "Bearer",
  "scope":"podcast_read episode_read podcast_update episode_publish",
}
Invalid code
HTTP/1.1 400 Bad Request
{
     "error": "invalid_grant",
     "error_description": "Authorization code doesn't exist or is invalid for the client"
 }
Get Access Token By Client ID and Client Secret - 5. Client Credentials
To get an access token to manage your own account, make an HTTP GET request to the following OAuth endpoint:

post
https://api.podbean.com/v1/oauth/token
Example usage
curl -u YOUR_CLIENT_ID:YOUR_CLIENT_SECRET \
https://api.podbean.com/v1/oauth/token \
-X POST -d 'grant_type=client_credentials'
Header
Field	Type	Description
Authorization	String	
HTTP Basic authentication use client_id as username and use client_secret as password.

User-Agent	String	
It contains the name and version number of the browser or other client application. Servers can use this string to identify the client application and version information.

Authorization
User-Agent
Authorization: Basic dGVdF9jbGllbnRaWQ1MTp0ZXN0X2NsaWVdF9zZWNyZQ=
Parameter
Field	Type	Description
grant_type	String	
Allowed values: client_credentials

expires_inoptional	Int	
Default value: 604800

Size range: 60-604800

podcast_idoptional	String	
You can get podcast_id from here.If no podcast_id is provided, the default podcast is used

Response JSON format
Field	Type	Description
access_token	String	
The authorization of the podcasts owned by the user or specified by API

token_type	String	
Allowed values: Bearer

scope	String	
expires_in	Int	
Success-Response
HTTP/1.1 200 OK
{
  "access_token": YOUR_ACCESS_TOKEN,
  "token_type": TYPE,
  "expires_in":	SECONDS_TIL_EXPIRATION
  "token_type": "Bearer",
  "scope":"podcast_read episode_read podcast_update episode_publish private_members"
}
Invalid code
HTTP/1.1 400 Bad Request
{
     "error": "invalid_grant",
     "error_description": "The grant type is unauthorized for this client_id"
 }
Get Multiple Podcasts Access Token By Client ID and Client Secret - 6. Get Multiple Podcasts Tokens
To get an access token to manage your own account, make an HTTP GET request to the following OAuth endpoint:

post
https://api.podbean.com/v1/oauth/multiplePodcastsToken
Example usage
curl -u YOUR_CLIENT_ID:YOUR_CLIENT_SECRET \
https://api.podbean.com/v1/oauth/multiplePodcastsToken \
-X POST -d 'grant_type=client_credentials'
Header
Field	Type	Description
Authorization	String	
HTTP Basic authentication use client_id as username and use client_secret as password.

User-Agent	String	
It contains the name and version number of the browser or other client application. Servers can use this string to identify the client application and version information.

Authorization
User-Agent
Authorization: Basic dGVdF9jbGllbnRaWQ1MTp0ZXN0X2NsaWVdF9zZWNyZQ=
Parameter
Field	Type	Description
grant_type	String	
Allowed values: client_credentials

expires_inoptional	Int	
Default value: 604800

Size range: 60-604800

podcast_idoptional	String	
You can get podcast_id from here.If no podcast_id is provided, the default podcast is used

Response JSON format
Field	Type	Description
access_token	String	
The authorization of the podcasts owned by the user or specified by API

token_type	String	
Allowed values: Bearer

scope	String	
expires_in	Int	
podcasts	Object[]	
Contains all the access tokens for podcasts belonging to the user.

Success-Response
HTTP/1.1 200 OK
{
  "access_token": YOUR_ACCESS_TOKEN,
  "token_type": TYPE,
  "expires_in":	SECONDS_TIL_EXPIRATION
  "token_type": "Bearer",
  "scope":"podcast_read episode_read podcast_update episode_publish private_members"
  "podcasts": [{
     "access_token": YOUR_ACCESS_TOKEN,
     "expires_in": 604800,
     "token_type": "Bearer",
     "scope": "podcast_read episode_read podcast_update episode_publish podcast_read episode_read private_members",
     "title": TITLE,
     "link": LINK,
     "podcast_id": YOUR_PODCAST_ID
   }]
}
Invalid code
HTTP/1.1 400 Bad Request
{
     "error": "invalid_grant",
     "error_description": "The grant type is unauthorized for this client_id"
 }
Podcast
Get Podcast - 1. Get Podcast
Get authorized podcast information

get
https://api.podbean.com/v1/podcast
Example usage
curl https://api.podbean.com/v1/podcast \
-G -d 'access_token=YOUR_ACCESS_TOKEN'
Header
Field	Type	Description
User-Agent	String	
It contains the name and version number of the browser or other client application. Servers can use this string to identify the client application and version information.

User-Agent
User-Agent: MyApp/1.2.3 (Example)
Parameter
Field	Type	Description
access_token	String	
Response JSON format
Field	Type	Description
podcast	Object	
Podcast Object

Success-Response:
HTTP/1.1 200 OK
{
"podcast": {
"title": "Your Podcast title",
"desc": "Podcast desc",
"logo": "https://imglink",
"website": "https://website",
"category_name": "Technology:Podcasting",
"allow_episode_type": [
"public",
"premium"
],
"object": "Podcast"
}
}
Invalid code:
HTTP/1.1 400 Bad Request
{
"error": "invalid_token",
"error_description": "The access token provided is invalid"
}
Episode
Get Episodes - 1. Get Episodes
Get authorized podcast episode list

get
https://api.podbean.com/v1/episodes
Example usage
curl https://api.podbean.com/v1/episodes \
-G -d 'access_token=YOUR_ACCESS_TOKEN' -d 'offset=0' -d 'limit=10'
Header
Field	Type	Description
User-Agent	String	
It contains the name and version number of the browser or other client application. Servers can use this string to identify the client application and version information.

User-Agent
User-Agent: MyApp/1.2.3 (Example)
Parameter
Field	Type	Description
access_token	String	
offsetoptional	Int	
The (zero-based) offset of the first item in the collection to return

Default value: 0

limitoptional	Int	
The maximum number of entries to return. If the value exceeds the maximum, then the maximum value will be used. You can find more instructions here

Default value: 20

Size range: 0-100

Response JSON format
Field	Type	Description
episodes	Object[]	
Array of Episode Object

offset	Int	
The (zero-based) offset of the first item in the collection to return

limit	Int	
The maximum number of entries to return. If the value exceeds the maximum, then the maximum value will be used.

count	Int	
has_more	Bool	
Whether or not there are more elements available after this set. If false, this set comprises the end of the list.

Success-Response
{
"episodes": [
{
"id": "IWPNG2FB3F",
"title": "Good day 8",
"content": "Time you <b>enjoy</b> wasting, was not wasted.",
"logo": "http://yoursubdomain.podbean.com/mf/web/xm46wb/2017022802474032.jpg",
"media_url": "https://yoursubdomain.podbean.com/mf/play/ts6tyk/2017022810121184.premium_ts6tyk.m4a",
"player_url": "https://www.podbean.com/player-v2/?xxx=xxx",
"permalink_url": "https://yoursubdomain.podbean.com/e/permalink",
"publish_time": 1488276731,
"status": "publish",
"type": "public",
"season_number":1,
"episode_number":1,
"apple_episode_type":"full",
"transcripts_url":"https://mcdn.podbean.com/mf/web/rtm7g2/transcript.srt",
"content_explicit":"clean"
"object": "Episode"
},
{
"id": "MMK7I2FB3D",
"title": "Good day 7",
"content": "Time you <b>enjoy</b> wasting, was not wasted.",
"logo": null,
"media_url": "https://yoursubdomain.podbean.com/mf/play/7bx8bw/2017022809580229.premium_7bx8bw.m4a",
"permalink_url": "https://yoursubdomain.podbean.com/e/permalink2",
"publish_time": 1488275882,
"status": "publish",
"type": "premium",
"season_number":1,
"episode_number":1,
"apple_episode_type":"full",
"transcripts_url":"https://mcdn.podbean.com/mf/web/rtm7g2/transcript.srt",
"content_explicit":"clean",
"object": "Episode"
}
],
"offset": 0,
"limit": 20,
"has_more": false,
"count":2
}
Invalid code
HTTP/1.1 400 Bad Request
{
     "error": "invalid_token",
     "error_description": "The access token provided is invalid"
}
Publish New Episode - 2. Publish New Episode
To publish an episode, you should have episode_publish permission

post
https://api.podbean.com/v1/episodes
Example usage
curl https://api.podbean.com/v1/episodes \
-X POST \
-d access_token=YOUR_ACCESS_TOKEN \
-d title="Good day" \
-d content="Time you <b>enjoy</b> wasting, was not wasted." \
-d status=publish \
-d type=public \
-d media_key=audio.mp3
-d logo_key=logo.jpg
-d transcripts_key=transcripts.srt
-d season_number=1
-d episode_number=1
-d apple_episode_type=full
-d publish_timestamp=1667850511
-d content_explicit=clean
Header
Field	Type	Description
User-Agent	String	
It contains the name and version number of the browser or other client application. Servers can use this string to identify the client application and version information.

User-Agent
User-Agent: MyApp/1.2.3 (Example)
Parameter
Field	Type	Description
access_token	String	
title	String	
Size range: 5..200

content	String	
HTML code except style and script is supported.

Size range: 0..100000

status	String	
Allowed values: "publish", "draft", "future"

type	String	
The episode type you can publish is based on the allow_episode_type of the Podbean object allow_episode_type returned by the Get Podcast you invoke.

Allowed values: "public", "premium", "private"

logo_keyoptional	String	
Use this parameter when you upload the image from your local device. Refer to Episode Publishing Process

media_keyoptional	String	
Use this parameter when you upload the media files from your local device. Refer to Episode Publishing Process

transcripts_keyoptional	String	
If you already uploaded episode transcripts file. Refer to Episode Publishing Process

remote_logo_urloptional	String	
You can enter a remote image URL instead of uploading the file from your local device. Podbean will get the image through the remote URL.

remote_media_urloptional	String	
You can enter a remote audio/video file URL instead of uploading the file from your local device. Podbean will get the audio/video file through the remote audio/video file URL.

remote_transcripts_urloptional	String	
You can enter a transcript URL instead of uploading the transcript file from your local device. Podbean will get the transcript through the URL.

season_numberoptional	String	
If an episode is within a season use this tag.Where season is a non-zero integer (1, 2, 3,etc.) representing your season number (maximum is 65535).

episode_numberoptional	String	
If all your episodes have numbers and you would like to be ordered based on them use this tag for each one (maximum is 65535).

apple_episode_typeoptional	String	
The episode type is “Full” by default. If an episode is a trailer or bonus content, use this tag.

publish_timestampoptional	String	
The publishing timestamp of an episode. The episode will be listed based on its publishing time, from New to Old by default. If it is not set, the "current time" will be set as its publishing time.

content_explicitoptional	String	
The episode parental advisory information. Episodes containing explicit material aren’t available in some Apple Podcasts territories.

Response JSON format
Field	Type	Description
episode	Object	
Episode Object

Success-Response:
HTTP/1.1 200 OK
{
 "episode" : {
      "id": "IWPNG2FB3F",
      "title": "Good day 8",
      "content": "Time you <b>enjoy</b> wasting, was not wasted.",
      "logo": null,
      "media_url": "https://yoursubdomain.podbean.com/mf/play/ts6tyk/2017022810121184.premium_ts6tyk.m4a",
      "player_url": "https://www.podbean.com/player-v2/?xxx=xxx",
      "permalink_url": "https://yoursubdomain.podbean.com/e/permalink",
      "publish_time": 1488276731,
      "status": "publish",
      "type": "premium",
      "season_number":1,
      "episode_number":1,
      "apple_episode_type":"full",
      "transcripts_url":"https://mcdn.podbean.com/mf/web/rtm7g2/transcript.srt",
      "content_explicit":"clean",
      "object": "Episode"
 }
}
Invalid code:
HTTP/1.1 400 Bad Request
{
     "error": "invalid_token",
     "error_description": "The access token provided is invalid"
}
Update Episode - 3. Update Episode
To update an episode, you should have episode_publish permission

post
https://api.podbean.com/v1/episodes/YOUR_EPISODE_ID
Header
Field	Type	Description
User-Agent	String	
It contains the name and version number of the browser or other client application. Servers can use this string to identify the client application and version information.

User-Agent
User-Agent: MyApp/1.2.3 (Example)
Parameter
Field	Type	Description
access_token	String	
title	String	
Size range: 5..200

content	String	
HTML code except style and script is supported.

Size range: 0..100000

status	String	
Allowed values: "publish", "draft", "future"

type	String	
The episode type you can publish is based on the allow_episode_type of the Podbean object allow_episode_type returned by the Get Podcast you invoke.

Allowed values: "public", "premium", "private"

logo_keyoptional	String	
If you already uploaded episode logo. Refer to Episode Publishing Process

media_keyoptional	String	
If you already uploaded episode media file. Refer to Episode Publishing Process

transcripts_keyoptional	String	
If you already uploaded episode transcripts file. Refer to Episode Publishing Process

remote_media_urloptional	String	
You can enter a remote audio/video file URL instead of uploading the file from your local device. Podbean will get the audio/video file through the remote audio/video file URL.

remote_logo_urloptional	String	
You can enter a remote image URL instead of uploading the file from your local device. Podbean will get the image through the remote URL.

remote_transcripts_urloptional	String	
You can enter a transcript URL instead of uploading the transcript file from your local device. Podbean will get the transcript through the URL.

season_numberoptional	String	
If an episode is within a season use this tag.Where season is a non-zero integer (1, 2, 3,etc.) representing your season number (maximum is 65535).

episode_numberoptional	String	
If all your episodes have numbers and you would like to be ordered based on them use this tag for each one (maximum is 65535).

apple_episode_typeoptional	String	
The episode type is “Full” by default. If an episode is a trailer or bonus content, use this tag.

publish_timestampoptional	String	
The publishing timestamp of an episode. The episode will be listed based on its publishing time, from New to Old by default. If it is not set, the "current time" will be set as its publishing time.

content_explicitoptional	String	
The episode parental advisory information. Episodes containing explicit material aren’t available in some Apple Podcasts territories.

Response JSON format
Field	Type	Description
episode	Object	
Episode Object

Success-Response:
HTTP/1.1 200 OK
{
 "episode" : {
      "id": "IWPNG2FB3F",
      "title": "Good day 8",
      "content": "Time you <b>enjoy</b> wasting, was not wasted.",
      "logo": null,
      "media_url": "https://yoursubdomain.podbean.com/mf/play/ts6tyk/2017022810121184.premium_ts6tyk.m4a",
      "player_url": "https://www.podbean.com/player-v2/?xxx=xxx",
      "permalink_url": "https://yoursubdomain.podbean.com/e/permalink",
      "publish_time": 1488276731,
      "status": "publish",
      "type": "premium",
      "season_number":1,
      "episode_number":1,
      "apple_episode_type":"full",
      "transcripts_url":"https://mcdn.podbean.com/mf/web/rtm7g2/transcript.srt",
      "content_explicit":"clean"
      "object": "Episode"
 }
}
Invalid code:
HTTP/1.1 400 Bad Request
{
     "error": "invalid_token",
     "error_description": "The access token provided is invalid"
}
Read Episode - 4. Read Episode
get
https://api.podbean.com/v1/episodes/YOUR_EPISODE_ID
Header
Field	Type	Description
User-Agent	String	
It contains the name and version number of the browser or other client application. Servers can use this string to identify the client application and version information.

User-Agent
User-Agent: MyApp/1.2.3 (Example)
Parameter
Field	Type	Description
access_token	String	
Response JSON format
Field	Type	Description
episode	Object	
Episode Object

Success-Response:
HTTP/1.1 200 OK
{
 "episode" : {
      "id": "IWPNG2FB3F",
      "title": "Good day 8",
      "content": "Time you <b>enjoy</b> wasting, was not wasted.",
      "logo": null,
      "media_url": "https://yoursubdomain.podbean.com/mf/play/ts6tyk/2017022810121184.premium_ts6tyk.m4a",
      "player_url": "https://www.podbean.com/player-v2/?xxx=xxx",
      "publish_time": 1488276731,
      "status": "publish",
      "type": "premium",
      "season_number":1,
      "episode_number":1,
      "apple_episode_type":"full",
      "transcripts_url":"https://mcdn.podbean.com/mf/web/rtm7g2/transcript.srt",
      "content_explicit":"clean",
      "object": "Episode"
 }
}
Invalid code:
HTTP/1.1 400 Bad Request
{
     "error": "invalid_token",
     "error_description": "The access token provided is invalid"
}
Delete Episode - 5. Delete Episode
To delete an episode, you should have episode_publish permission

post
https://api.podbean.com/v1/episodes/YOUR_EPISODE_ID/delete
Example usage
curl https://api.podbean.com/v1/episodes/YOUR_EPISODE_ID/delete \
-X POST \
-d 'access_token=YOUR_ACCESS_TOKEN'
Header
Field	Type	Description
User-Agent	String	
It contains the name and version number of the browser or other client application. Servers can use this string to identify the client application and version information.

User-Agent
User-Agent: MyApp/1.2.3 (Example)
Parameter
Field	Type	Description
access_token	String	
delete_media_fileoptional	String	
Default value: no

Allowed values: ['yes', 'no']

Response JSON format
Field	Type	Description
msg	String	
Success-Response:
HTTP/1.1 200 OK
{
     "msg":"Delete episode success."
}
Invalid code:
HTTP/1.1 400 Bad Request
{
     "error": "input_params_invalid",
     "error_description": "Episode not found."
}
Get Chapters - 6. Get Chapters
Get episode chapters

get
https://api.podbean.com/v1/episodes/YOUR_EPISODE_ID/chapters
Example usage
curl https://api.podbean.com/v1/episodes/YOUR_EPISODE_ID/chapters \
-G -d 'access_token=YOUR_ACCESS_TOKEN'
Header
Field	Type	Description
User-Agent	String	
It contains the name and version number of the browser or other client application. Servers can use this string to identify the client application and version information.

User-Agent
User-Agent: MyApp/1.2.3 (Example)
Parameter
Field	Type	Description
access_token	String	
Response JSON format
Field	Type	Description
chapters	Object[]	
Array of Chapter Object

Success-Response
HTTP/1.1 200 OK
{
[
{
"title": "chapter 1",
"start_time": 20,
"object": "Chapter"
},
{
"title": "chapter 2",
"start_time": 100,
"object":"Chapter"
}
],
}
Invalid code
HTTP/1.1 400 Bad Request
{
     "error": "input_params_invalid",
     "error_description": "Episode not found."
}
Save Chapters - 7. Save Chapters
To save chapter, you should have episode_publish permission

post
https://api.podbean.com/v1/episodes/YOUR_EPISODE_ID/saveChapters
Example usage
curl https://api.podbean.com/v1/episodes/YOUR_EPISODE_ID/saveChapters \
-X POST \
-d 'access_token=YOUR_ACCESS_TOKEN'
-d 'chapters[0][title]=chapter1'
-d 'chapters[0][start_time]=20'
-d 'chapters[1][title]=chapter2'
-d 'chapters[1][start_time]=100'
Header
Field	Type	Description
User-Agent	String	
It contains the name and version number of the browser or other client application. Servers can use this string to identify the client application and version information.

User-Agent
User-Agent: MyApp/1.2.3 (Example)
Parameter
Field	Type	Description
access_token	String	
chapters	Array	
Submit all chapters(Array of Chapter Object) of the episode,for example:[{title:'chapter1',start_time:20},{title:'chapter2',start_time:100}],If you want to delete all chapters, please use []

Response JSON format
Field	Type	Description
msg	String	
Success-Response:
HTTP/1.1 200 OK
{
     "msg":"Save chapters success."
}
Invalid code:
HTTP/1.1 400 Bad Request
{
     "error": "input_params_invalid",
     "error_description": "Episode not found."
}
File upload
Authorize file upload - 1. Authorize file upload
Authorize file upload

get
https://api.podbean.com/v1/files/uploadAuthorize
Example usage
curl https://api.podbean.com/v1/files/uploadAuthorize \
-G -d 'access_token=YOUR_ACCESS_TOKEN' -d 'filename=abc.mp3' -d 'filesize=1291021' -d 'content_type=audio/mpeg'
Header
Field	Type	Description
User-Agent	String	
It contains the name and version number of the browser or other client application. Servers can use this string to identify the client application and version information.

User-Agent
User-Agent: MyApp/1.2.3 (Example)
Parameter
Field	Type	Description
access_token	String	
filename	String	
content_type	String	
filesize	Int	
200
Field	Type	Description
presigned_url	url	
expire_at	int	
The lifetime of presigned url, in seconds.

file_key	string	
Use this to create/update episode

Success-Response:
HTTP/1.1 200 OK
{
    "presigned_url": "https://s3.amazonaws.com/bucket.podbean.com/tmp2/49755/abc.mp3?AWSAccessKeyId=AKIAJ47JKNDVAAHIL6SA&Expires=1488268856&Signature=4iiakzeVHgLFJ4CCu0PhQHMH2EE%3D",
    "expire_in": 600,
    "file_key" : "tmp2/49755/abc.mp3"
}
Invalid code:
{
    "error": "storage_limit_reach",
    "error_description": " You've uploaded too much this month. To provide a fair and sustainable uploading experience for all users, your uploads are temporarily restricted until the end of this month. Thank you for your understanding."
}
Embed
oEmbed - 1. oEmbed
oEmbed is an open standard to easily embed content from oEmbed providers into your site. The oEmbed endpoint will serve the widget embed code for any URL pointing to a user, set, or a playlist. To find out more about the oEmbed standard, have a look at oEmbed.com.

get
https://api.podbean.com/v1/oembed
Example usage
curl https://api.podbean.com/v1/oembed \
-d 'format=json' \
-d 'url=https://yoursubdomain.podbean.com/e/permalink'
Header
Field	Type	Description
User-Agent	String	
It contains the name and version number of the browser or other client application. Servers can use this string to identify the client application and version information.

User-Agent
User-Agent: MyApp/1.2.3 (Example)
Parameter
Field	Type	Description
formatoptional	String	
Default value: json

Allowed values: xml, json

url	String	
Response JSON format
Field	Type	Description
type	String	
Allowed values: rich

version	String	
Allowed values: 1.0

provider_name	String	
Allowed values: "Podbean"

provider_url	String	
Allowed values: "http://podbean.com"

width	Int	
The width in pixels required to display the HTML.

height	Int	
The width in pixels required to display the HTML.

html	String	
The HTML required to display the resource. The HTML should have no padding or margins.

Success-Response:
HTTP/1.1 200 OK

{
    "version": "1.0",
    "provider_name": "Podbean",
    "provider_url": "http://podbean.org",
    "width": 500,
    "height": 100,
    "type": "rich",
    "html": "&lt;iframe src='https://www.podbean.com/player-v2/?xxx=xxx' height='100' width='100%' frameborder='0' scrolling='no' data-name='pb-iframe-player' &gt;&lt;/iframe&gt;"
}
Raw Data
Raw data reports for podcast downloads - 1. Raw data reports for podcast downloads
Get podcast download analytic reports raw data file. This feature is available for business plan and above.

get
https://api.podbean.com/v1/analytics/podcastReports
Example usage
curl https://api.podbean.com/v1/analytics/podcastReports \
  -G -d 'access_token=YOUR_ACCESS_TOKEN' -d 'podcast_id=YOUR_PODCAST_ID' -d 'year=2018'
Header
Field	Type	Description
User-Agent	String	
It contains the name and version number of the browser or other client application. Servers can use this string to identify the client application and version information.

User-Agent
User-Agent: MyApp/1.2.3 (Example)
Parameter
Field	Type	Description
access_token	String	
podcast_id	String	
id of Podcast Object

year	String	
eg:2018

Response JSON format
Field	Type	Description
download_urls	String[]	
Success-Response:
HTTP/1.1 200 OK
{
   "download_urls": {
       "2018-1": "http://example.com/example.csv",
       "2018-2": "http://example.com/example.csv",
       "2018-3": "http://example.com/example.csv",
       "2018-4": "http://example.com/example.csv",
       "2018-5": "http://example.com/example.csv",
       "2018-6": false,
       "2018-7": false,
       "2018-8": false,
       "2018-9": false,
       "2018-10": false,
       "2018-11": false,
       "2018-12": false
   }
}
Invalid code:
HTTP/1.1 400 Bad Request
{
    "error": "invalid_token",
    "error_description": "The access token provided is invalid"
}
Raw data reports on podcast engagement - 2. Raw data reports on podcast engagement
Get podcast engagement analytic reports raw data file. This feature is available for business plan and above.

get
https://api.podbean.com/v1/analytics/podcastEngagementReports
Example usage
curl https://api.podbean.com/v1/analytics/podcastEngagementReports \
  -G -d 'access_token=YOUR_ACCESS_TOKEN' -d 'podcast_id=YOUR_PODCAST_ID' -d 'year=2018'
Header
Field	Type	Description
User-Agent	String	
It contains the name and version number of the browser or other client application. Servers can use this string to identify the client application and version information.

User-Agent
User-Agent: MyApp/1.2.3 (Example)
Parameter
Field	Type	Description
access_token	String	
podcast_id	String	
id of Podcast Object

year	String	
eg:2018

Response JSON format
Field	Type	Description
download_urls	String[]	
Success-Response:
HTTP/1.1 200 OK
{
   "download_urls": {
       "2018-1": "http://example.com/example.csv",
       "2018-2": "http://example.com/example.csv",
       "2018-3": "http://example.com/example.csv",
       "2018-4": "http://example.com/example.csv",
       "2018-5": "http://example.com/example.csv",
       "2018-6": false,
       "2018-7": false,
       "2018-8": false,
       "2018-9": false,
       "2018-10": false,
       "2018-11": false,
       "2018-12": false
   }
}
Invalid code:
HTTP/1.1 400 Bad Request
{
    "error": "invalid_token",
    "error_description": "The access token provided is invalid"
}
Stats
Download Stats - 1. Download Stats
Get authorized podcast stats

get
https://api.podbean.com/v1/podcastStats/stats
Example usage
curl https://api.podbean.com/v1/podcastStats/stats \
-G -d 'access_token=YOUR_ACCESS_TOKEN' -d 'episode=YOUR_EPISODE_ID' -d 'start=2023-09-10' -d 'end=2023-09-15' -d 'period=d'
Header
Field	Type	Description
User-Agent	String	
It contains the name and version number of the browser or other client application. Servers can use this string to identify the client application and version information.

User-Agent
User-Agent: MyApp/1.2.3 (Example)
Parameter
Field	Type	Description
access_token	String	
episode_idoptional	String	
your episode id.(If this field is not specified, it includes all episodes.)

start	string	
Start date for statistics.eg:2018-09-09.

endoptional	string	
End date for statistics.eg:2018-09-09.(If this field is not filled or is greater than or equal to today, it will be changed to yesterday.)

periodoptional	string	
The value of this field includes 'm' and 'd'. 'm' indicates monthly statistics, and 'd' indicates daily statistics.

Default value: d

Response JSON format
Field	Type	Description
Stats	Object	
Display download stats data within the specified range, group by month or day.

Success-Response
{
"2023-09-10": 1,
"2023-09-11": 10,
"2023-09-12": 0,
"2023-09-13": 9,
"2023-09-14": 11,
"2023-09-15": 20,
}
Invalid code
HTTP/1.1 400 Bad Request
{
     "error": "invalid_token",
     "error_description": "The access token provided is invalid"
}
User interactions stats - 2. User interactions stats
Get podcast Followers/Likes/Comments/Total episode length analytic data

get
https://api.podbean.com/v1/analytics/podcastAnalyticReports
Example usage
curl https://api.podbean.com/v1/analytics/podcastAnalyticReports \
  -G -d 'access_token=YOUR_ACCESS_TOKEN' -d 'types[]=followers' -d 'types[]=likes'
Header
Field	Type	Description
User-Agent	String	
It contains the name and version number of the browser or other client application. Servers can use this string to identify the client application and version information.

User-Agent
User-Agent: MyApp/1.2.3 (Example)
Parameter
Field	Type	Description
access_token	String	
types	Array	
one or more of values ('followers','likes','comments','total_episode_length')

podcast_idoptional	String	
id of Podcast Object if null will get network podcasts data

Default value: null

Response JSON format
Field	Type	Description
followers	Int	
Follower count of Podcast or Network

likes	Int	
Likes count of the episodes of Podcast or Network

comments	Int	
Comments count of Podcast or Network

total_episode_length	Int	
Total episode file length of Podcast or Network (unit: seconds)

Success-Response:
HTTP/1.1 200 OK
{
   "followers": 98,
   "likes": 108,
   "comments": 38,
   "total_episode_length": 1098,
}
Invalid code:
HTTP/1.1 400 Bad Request
{
    "error": "invalid_token",
    "error_description": "The access token provided is invalid"
}
Appendix
1. Episode Publishing Process
The process of publishing/editing episode media file/logo :

Invoking api presigned_url of the returning values will be obtained by connecting to Authorize file upload

Use presigned_url to upload file.

for curl example:

  curl -v -H "Content-Type: image/jpeg" -T /your/path/file.ext "PRESIGNED_URL"
for java and okhttp example method :

  boolean uploadFile(String presignedUrl,File file) throws IOException{
      RequestBody fileBody = RequestBody.create(null, file);

      Request request = new Request
              .Builder()
              .url(presignedUrl)
              .method("PUT",fileBody)
              .addHeader("Content-Type","audio/mpeg") // use your Content-Type 
              .build();

      Response response = client.newCall(request).execute();
      return response.code() == 200;
  }
for swift and Alamofire example code :

  let fileURL = Bundle.main.url(forResource: "yourfilename", withExtension: "m4a")
  
  let presignedUrl = "https://your-presigned-url"
  
  Alamofire.upload(fileURL!, to: presignedUrl, method:.put, headers:["Content-Type":"audio/mp4"])
  .responseString { response in
      print("Request: \(String(describing: response.request))")   // original url request
      print("Response: \(String(describing: response.response))") // http url response
      if(response.response?.statusCode==200){
          //success
      }else{
          //failed
      }
  }
Following a successful upload, you can use the file_key of the returning values in the first step as the logo_key (if the file is an image), or as the media_key (if the file is audio/video)


2. Permissions
Scope	Description
podcast_read	Read podcast
podcast_update	Update Podcast
episode_read	Read episode
episode_publish	Create/Update/Delete episode
private_members	Create/Read/Update/Delete private members(Only available to Business Master Account with Client Credentials Authentication.)
3. Objects
Podcast Object
Field	Description
id	String
title	String
desc	String
website	Url
status	"release" or "draft"
logo	Url
category_name	String
allow_episode_type	Array
Combination of public , premium or private
object	"Podcast"
Episode Object
Field	Description
id	String
podcast_id	String
title	String
content	String
logo	Url
media_url	Url
player_url	Url
permalink_url	Url
publish_time	Timestamp
duration	Int or null
status	Status of episode, one of: "publish", "draft"
type	Type of episode, one of: "public", "premium" or "private"
season_number	Int
episode_number	Int
apple_episode_type	Episode type used in Apple Podcasts: "full", "trailer" or "bonus"
transcripts_url	Url
content_explicit	The episode parental advisory information: "clean" or "explicit"
object	"Episode"
Private Member Object
Field	Description
email	String
object	"PrivateMember"
Chapter Object
Field	Description
title	String
start_time	Integer
object	"Chapter"
4. Pagination offset and limit
If you have 200 episodes (index starting from 0) and want to fetch the first 50 episodes, you need to specify the two parameters (offset=0 and limit=50) as in the example below.

curl https://api.podbean.com/v1/episodes \
-G -d 'access_token=YOUR_ACCRSS_TOKEN' -d 'offset=0' -d 'limit=50'
Following the example above, if you still want to fetch the next 100 episodes from 50 to 149, then do this call.

curl https://api.podbean.com/v1/episodes \
-G -d 'access_token=YOUR_ACCRSS_TOKEN' -d 'offset=50' -d 'limit=100'
Next, if you try to fetch the next 100 episodes starting from index 150, the call will be like this:

curl https://api.podbean.com/v1/episodes \
-G -d 'access_token=YOUR_ACCRSS_TOKEN' -d 'offset=150' -d 'limit=100'
However, it will only return 50 episodes since there are 200 episodes in total. The response object will have “has_more” as “false”.

"has_more": false
5. Podbean API Limit
All Podbean APIs use a leaky bucket algorithm to manage requests. This algorithm lets your app make an unlimited amount of requests in infrequent bursts over time.

The main points to understand about the leaky bucket algorithm are as follows:

Each app has access to a bucket. It can hold 60 “beans”. Each second, 2 beans are removed from the bucket (if there are any). That way there’s always more room. Each API request requires you to add a bean in the bucket. If the bucket gets full, you get an error and have to wait for room to become available in the bucket. This model ensures that apps that manage API calls responsibly will always have room in their buckets to make a burst of requests if needed. For example, if you average 2 requests (“beans”) per second but suddenly need to make 30 requests all at once, you can still do so without hitting your rate limit.

6. The Causes of 403 Forbidden Error
When encountering a 403 Forbidden error while using the API, it is important to investigate the following potential causes:

Incorrect agent configuration: Verify that the agent configuration has been set up properly. Make sure all relevant settings and permissions are configured correctly to allow proper access.
Firewall interception due to sensitive information: Review the submitted content for any sensitive data such as SQL injection attacks or HTML tags containing confidential information. The firewall may block access if it detects such sensitive information. Ensure the content is free of any sensitive data to avoid triggering firewall restrictions.