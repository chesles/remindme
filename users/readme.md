# the users service

This is the users service. GET, POST, or PUT to it to search, create, or update users.

# dependencies

The users service is written for node.js. There are a few dependencies:

  - node, obviously
  - mongodb

And a few node modules (install npm, the node package manager, to get most of these):

  - connect
  - node-mongodb-native (mongodb)
  - underscore
  - rsnbl (included as submodule)

Use `npm install underscore connect mongodb step` inside of the users directory (i.e. this one) to get these. To get the `rsnbl` submodule to install, run `git submodule init` and then `git submodule update`, and it should check out the right version for you into the right place.

# running it

Configuration lives in ../conf/settings.js. The users service defaults to port 8082, and connects to mongo using the cs462 database on localhost, default port (27017).

Run the server by saying `node users/server.js` from the base of the repository.

# usage

The service provides a simple interface using GET, POST, and PUT HTTP calls. You can use `curl` to play around with it:

    # -d options to curl generate a POST with the given data,
    # so this command creates a user with username bob, etc
    curl localhost:8082 -d username=bob -d phone=1234567890 -d fsqid=12345

    # search for a user:
    curl localhost:8082/?username=bob
    curl localhost:8082/bob # ^ equivalent to above
    curl localhost:8082/?phone=1234567890

    # update a user
    curl -X PUT localhost:8082/bob -d phone=555-555-5555

I haven't tested, but it should work the same to POST or PUT json data to these URLs too. A POST will return a JSON string of the created user, a PUT will return a JSON object containing the updated fields.

# integrating with backbone.js

This should integrate directly with backbone.js. Set your model's `_idAttribute` to "username", as dealing with mongo's `_id` objects isn't implemented here.

# reminders

You can get a list of reminders for a user, add a reminder to the database, or make changes to a reminder in a similar manner:

    # get a user's reminders:
    curl localhost:8082/bob/reminders

    # add a reminder, with two fields: text and location
    # note that the schema is flexible and you can specify any field name/value
    # the server automatically assigns an id in the _id field
    curl localhost:8082/bob/reminders -d text=remindertext -d location=somelocation

    # update a reminder:
    curl localhost:8082/bob/reminders/[reminder's _id field] -X PUT text=updatedtext
