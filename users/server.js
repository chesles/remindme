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

        console.log(search);
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
        console.log("creating user:", user);
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
        console.log("PUTting", search);
        db.User.findOne(search, {}, function(err, user) {
            console.log("Found user:", arguments);
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
            console.log("Updated:", user);
            user.save(end);
        });
    }
});

UserService = new rsnbl.Application([
        [/\/([a-z0-9]*)/i, UserRestHandler]
    ]);

db.open(function() {
    UserService.listen(settings.users.port, function() {
        console.log("User service listening:", this.address());
    });
});
