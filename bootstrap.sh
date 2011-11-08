APP=`grep 'application: ' app.yaml | cut -d':' -f2`

# Read username and password
printf 'Username: '
read EMAIL 
printf 'Password: '
stty -echo
read PASSWD 
stty echo
echo

AUTH=`curl -s -f \
  -d Email="$EMAIL" \
  -d Passwd="$PASSWD" \
  -d accountType=GOOGLE \
  -d service=ah \
  -d source=$APP \
  https://www.google.com/accounts/ClientLogin`
AUTH=`echo "$AUTH" | grep -E '^Auth='`
AUTH=${AUTH##Auth=}

COOKIE=`curl -s -f --head "http://feudbot.appspot.com/_ah/login?auth=$AUTH"`
COOKIE=`echo "$COOKIE" | grep -E '^Set-Cookie: ' | sed 's/^Set-Cookie: \([^;]*\).*/\1/'`

# Do empty POST to /update to trigger an update
curl -X POST -d "" -H "Cookie: $COOKIE" http://feudbot.appspot.com/update 
