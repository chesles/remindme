require 'rest_client'
require 'json'

class User < ActiveRecord::Base
  validates_presence_of :username, :first_name, :last_name, :phone_number, :email_address, :fsqr_id, :user_type
  validates_uniqueness_of :username
  
  def is_admin
    self.user_type == 0
  end
  
  def reminders
    response = RestClient.get "http://localhost:8082/#{self.username}/reminders" 
    reminders = JSON.parse(response.to_str)   
  end
  
  def save
    # Update the information on the users server
    
    phone = self.phone_number
    if phone[1,2] != '+1'
      phone = '+1' + phone
    end

    user_hash = {:username => self.username,
                 :phone => phone,
                 :fsqid => self.fsqr_id,
                 :email => self.email_address
                }
    
    # First see if the user exists
    response = RestClient.get "http://localhost:8082/#{self.username}"
    user_list =  JSON.parse(response.to_str)
    if user_list.empty?
      response = RestClient.post "http://localhost:8082/#{self.username}", user_hash.to_json, :content_type => :json, :accept => :json 
    else
      response = RestClient.put "http://localhost:8082/#{self.username}", user_hash.to_json, :content_type => :json, :accept => :json
    end
    
    super
  end
end
