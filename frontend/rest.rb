require 'rest_client'
require 'json'

response = RestClient.get 'http://localhost:8082'

users = JSON.parse(response.to_str)

users.each do |user|
  print "#{user['username']}\n"
end
