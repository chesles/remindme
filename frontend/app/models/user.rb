require 'rest_client'
require 'rubygems'
require 'httpclient'
require 'json'

class User < ActiveRecord::Base
  validates_presence_of :username, :first_name, :last_name, :phone_number, :email_address, :fsqr_id, :user_type, :fsqr_oauth_token
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

  def checkins
    begin
      client = HTTPClient.new
      uri = "https://api.foursquare.com/v2/users/self/checkins?oauth_token=#{self.fsqr_oauth_token}&v=20120125"
      logger.info("Using URI #{uri} to get checkin list")
      http_response = client.get_content(uri)
      response_hash = JSON.parse(http_response)
      checkin_list = response_hash["response"]["checkins"]["items"]
      logger.info("Returning checkin list.")
      return checkin_list
    rescue
      logger.error("Got exception getting checkin list.")
      return nil
    end
  end
  
  def last_checkin
    begin
      client = HTTPClient.new
      uri = "https://api.foursquare.com/v2/users/self/checkins?oauth_token=#{self.fsqr_oauth_token}&limit=1&v=20120125"
      logger.info("Using URI #{uri} to get checkin list")
      http_response = client.get_content(uri)
      response_hash = JSON.parse(http_response)
      checkin_list = response_hash["response"]["checkins"]["items"]
      logger.info("Returning checkin list.")
      return checkin_list[0]
    rescue
      logger.error("Got exception getting checkin list.")
      return nil
    end
  end

end
