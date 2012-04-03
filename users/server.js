var rsnbl = require("rsnbl"),
    connect = require("connect");

var db = require("./db"),
    settings = require("../conf/settings");

UserRestHandler = rsnbl.RequestHandler.extend({
    helpers: [connect.bodyParser(), connect.query()],
    /*
     * get/search for a user
     */
    get: function(user) {
        var self = this;
        var search = self.request.query || {};
        if (user) search.username = user;

        db.User.find(search, {}, function(err, users) {
            var code = 200;
            var response;
            if (err) response = JSON.stringify({error: err});
            else response = JSON.stringify(users);
            self.response.writeHead(code, {
                'Content-Type': 'application/json'
            });
            self.response.end(response);
        });
    },

    /*
     * create a new user
     */
    post: function() {
        var self = this;
        var user = new db.User(this.request.body);
        user.save(function(err, saved) {
            var code = 200, response;
            if (err) {
                code = 500;
                response = JSON.stringify({error: err});
            } else {
                response = JSON.stringify(saved);
            }
            self.response.writeHead(code, {
                "Content-Type": "application/json"
            });
            self.response.end(response);
        });
    },

    /*
     * updates the user
     */
    put: function(user) {
        var self = this,
            search = {username: user};
        console.log("Looking up user:", search);
        db.User.findOne(search, {}, function(err, user) {
            var end = function(err, results) {
                var code = 200, response;
                if (err) {
                    code = 500;
                    response = JSON.stringify({error: err});
                } else {
                    response = JSON.stringify(results);
                }
                self.response.writeHead(code, {
                    "Content-Type": "application/json"
                });
                self.response.end(response);
            };

            if (err || !user) return end(err || "No user found.");

            for (var k in self.request.body) {
                user.set(k, self.request.body[k]);
            }
            user.save(end);
        });
    }
});

var ReminderRestHandler = rsnbl.RequestHandler.extend({
    helpers: [connect.bodyParser(), connect.query()],
    get: function(username) {
        var self = this,
            search = {username: username};
        db.User.findOne(search, {}, function(err, user) {
            if (user) {
                reminderSearch = {user: user.get('username')};
                db.Reminder.find(reminderSearch, {}, function(err, reminders) {
                    var code = 200, response;
                    if (err) response = JSON.stringify({error: err});
                    else response = JSON.stringify(reminders);
                    self.response.writeHead(code, {
                        'Content-Type': 'application/json'
                    });
                    self.response.end(response);
                });
            } else {
                this.notfound();
            }
        });
    },

    post: function(username) {
        var self = this,
            data = this.request.body;
        data.user = username;
        var reminder = new db.Reminder(data);
        reminder.save(function(err, saved) {
            var code = 200, response;
            if (err) {
                code = 500;
                response = JSON.stringify({error: err});
            }
            else {
                response = JSON.stringify(saved);
            }
            self.response.writeHead(code, {
                "Content-Type": "application/json"
            });
            self.response.end(response);
        });
    },

    put: function(username, reminderid) {
        var self = this,
            id = db.mongo.ObjectID.createFromHexString(reminderid);
        db.Reminder.findOne(id, {}, function(err, reminder) {
            var end = function(err, results) {
                var code = 200, response;
                if (err) {
                    code = 500;
                    response = JSON.stringify({error: err});
                }
                else {
                    response = JSON.stringify(results);
                }
                self.response.writeHead(code, {
                    "Content-Type": "application/json"
                });
                self.response.end(response);
            };

            if (err || !reminder) return end(err || "Reminder not found");
            for (var k in self.request.body) {
                reminder.set(k, self.request.body[k]);
            }
            reminder.save(end);
        });
    }
});

UserService = new rsnbl.Application([
    [/^\/([a-z0-9]+)\/reminders\/?([a-f0-9]+)?/i, ReminderRestHandler],
    [/^\/([a-z0-9]*)/i, UserRestHandler]
]);

db.open(function() {
    UserService.listen(settings.users.port, function() {
        console.log("User service listening:", this.address());
    });
});
