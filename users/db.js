var Step = require("step"),
    _ = require("underscore"),
    conf = require("../conf/settings.js"),
    mongo = require("mongodb"),
    client = new mongo.Db(conf.mongo.database,
        new mongo.Server(conf.mongo.host, conf.mongo.port, conf.mongo.options));

exports.open = function(callback) {
    client.open(callback);
};

exports.close = function() {
    client.close();
};

var User = module.exports.User = function(attributes) {
    this.attributes = attributes || {};
    this.changes = {};
};

User.collection = "users";

/*
 * find user(s)
 *
 * @param object filter
 * @param object options
 * @param function callback
 *
 * callback gets called with an array of matching User obects
 * as the second parameter if the call succeeds. if there is an
 * error, callback is called with the error as the first parameter
 */
User.find = function(filter, options, callback) {
    Step(
        function() {
            client.collection(User.collection, this);
        },
        function(err, collection) {
            if (err) return callback.call(null, err);
            collection.find(filter, options, this);
        },
        function(err, cursor) {
            if (err) return callback.call(null, err);
            cursor.toArray(this);
        },
        function(err, arr) {
            if (err) return callback.call(null, err);
            var users = _.map(arr, function(data) {
                    var u = new User(data);
                    u._saved = true; // tells save() to findandmodify instead of insert
                    return u;
                });
            callback.apply(null, [err, users]);
        }
    );
};

/*
 * find the first user matching filter, if any
 *
 * callback gets called with a User object as the second parameter
 * or with an error as the first parameter
 */
User.findOne = function(filter, options, callback) {
    options = options || {};
    options.limit = 1;

    User.find(filter, options, function(err, users) {
        if (err) return callback.call(null, err);
        users = users || [];
        if (users.length < 1) return callback.call(null, null, null);
        else callback.call(null, null, users[0]);
    });
};

User.prototype.set = function(key, val) {
    // keep track of changes for when we do an update()
    if (this.attributes.hasOwnProperty(key)) {
        if (this.attributes[key] !== val)
            this.changes[key] = val;
    }
    this.attributes[key] = val;
};

User.prototype.get = function(key) {
    if (this.attributes.hasOwnProperty(key))
        return this.attributes[key];
    return null;
};

User.prototype.toJSON = function() {
    return this.attributes;
};

User.prototype.save = function(callback) {
    if (this._saved || this.attributes._id)
        this.update(callback);
    else
        this.insert(callback);
};

User.prototype.update = function(callback) {
    var self = this;
    Step(
        function() {
            client.collection(User.collection, this);
        },
        function(err, collection) {
            if (err) return callback.call(null, err);
            collection.update({_id: self.get('_id')}, {$set: self.changes}, {safe:true}, this);
        },
        function(err, result) {
            if (err) callback.call(null, err);
            else if (result) callback.call(null, null, self.changes);
            else callback.call(null, 'Update failed');
        }
    );
};

User.prototype.insert = function(callback) {
    var self = this;
    Step(
        function() {
            client.collection(User.collection, this);
        },
        function(err, collection) {
            if (err) return callback.call(null, err);
            collection.insert(self.attributes, {safe:true}, this);
        },
        function(err, result) {
            callback.apply(null, arguments);
        }
    );

};
