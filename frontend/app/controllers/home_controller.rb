require 'rubygems'
require 'httpclient'
require 'json'
require 'net/http'
require 'uri'


class HomeController < ApplicationController
  def index
    current_user = User.find_by_id(session[:user_id])
    redirect_to :action => 'reminders' if current_user
  end

  def about
  end

  def register
  end

  def signin
    # Continue the Foursquare dance!
    code = params[:code]
    if code
      auth_token = retrieve_access_token(code)
      if !auth_token
        flash[:notice] = "Error authenticating with Foursquare!"
        flash[:level] = :error
        redirect_to :action => "index"
      end
      session[:auth_token] = auth_token # Save it off in case the user chooses a username that is already in use. 
    else
      auth_token = session[:auth_token] # The user must have chosen a user name that was already in use and we've lost the code
                                        # Never fear though.  We saved off the auth token when we first got it.
    end
    
    user_info = get_fsqr_user_info(auth_token)
    if !user_info
      flash[:notice] = "Error getting Foursquare information!"
      flash[:level] = :error
      redirect_to :action => "index"
    end

    # Now get the user's Information
    # See if this user is already registered
    user = User.find(:first, :conditions => "fsqr_id='#{user_info[:fsqr_id]}'")
    if user
      # This user is already registered, just sign him in.
      session[:user_id] = user.id
      flash[:notice] = "Welcome back #{user.first_name}!"
      flash[:level] = :success
      redirect_to :action => 'reminders'
    end
    
    # This is a new user, we need to ask for a user name.
    # Save off what we have in a session variable
    session[:new_user_info] = user_info
    
  end
  
  def create_new_user
    if request.post?
      # See if the user's chosen user name is already in use
      username = params[:username]
      user = User.find(:first, :conditions => "username='#{username}'")
      if user
        flash[:notice] = "The user name #{username} is already in use.  Please choose another username."
        flash[:level] = :error
        redirect_to :action => 'signin'
        return
      end
      
      # Great, now we can create the user
      session[:new_user_info][:username] = username
      user = User.new(session[:new_user_info])
      if user.save
        # Log the user in.
        session[:user_id] = user.id
        
        flash[:notice] = "Your RemindMe account has now been created!"
        flash[:level] = :success
        redirect_to :action => 'reminders'
      else
        flash[:notice] = "There was an error creating your RemindMe account"
        flash[:level] = :error
        redirect_to :action => 'signin'
      end
    else
      redirect_to :action => 'index'
    end
  end

  def signout
    session[:user_id] = nil
    redirect_to :action => 'index'
  end

  def reminders
    current_user = User.find_by_id(session[:user_id])
    @reminders = current_user.reminders
  end
  
  def new_reminder
    if !request.post?
      redirect_to :action => 'index'
    end
    
    current_user = User.find_by_id(session[:user_id])

    event_hash = {:reminder_text => params[:reminder_text],
                  :user_name => current_user.username}
                  
    if HomeController.send_event("localhost", "/event", "user", "new_reminder", event_hash, 8080)
      flash[:notice] = "Your reminder was successfully sent"
      flash[:level] = :success
    else
      flash[:notice] = "There was an error sending your reminder"
      flash[:level] = :error
    end
    
    redirect_to :action => 'index'
  end

  def checkins
  end

  def settings
    @user = User.find_by_id(session[:user_id])
  end
  
  def update_settings
    @user = User.find_by_id(session[:user_id])

    respond_to do |format|
      if @user.update_attributes(params[:user])
        flash[:notice] = 'User was successfully updated.'
        flash[:level] = :success
        format.html { redirect_to :action => "settings" }
        format.xml  { head :ok }
      else
        format.html { render :action => "settings" }
        format.xml  { render :xml => @user.errors, :status => :unprocessable_entity }
      end
    end
  end

private

  def self.send_event(esl_host, esl_path, domain, name, event_hash, port)
    begin
      
      event_hash["_domain"] = domain
      event_hash["_name"] = name
      
      if esl_host != "consumer.eventedapi.org"
        if esl_path[-1,1] != '/'
          esl_path = esl_path + '/'
        end
      
        esl_path = esl_path + domain + '/' + name
      end
      
      req = Net::HTTP::Post.new(esl_path)
      req.set_form_data(event_hash)
      response = Net::HTTP.start(esl_host, port) do |http|
        http.request(req)
      end 
           
      case response
      when Net::HTTPSuccess
        text = response.body
        logger.info("Sent event.  Response:")
        logger.info(text)
        return true if text == 'OK'
      end # case
      
      return false
  
    rescue StandardError => connection_error
      return false
    end # begin
  end

  def retrieve_access_token(fsqr_code)
    begin
      logger.info("In retrieve access token!!!")
      #2. Get the token from foursquare
      uri = "https://foursquare.com/oauth2/access_token?client_id=#{FSQR_CLIENT_ID}&client_secret=#{FSQR_CLIENT_SECRET}&grant_type=authorization_code&redirect_uri=#{FSQR_REDIRECT_URI}&code=#{fsqr_code}"
      logger.info("Using URI #{uri} to get access token")

      http_response = http_get(uri)
      if !http_response
        nil
      end
      
      logger.info("Got response")   

      # 3. Parse out the user's token.
      response_hash = JSON.parse(http_response)
      logger.info("Created hash")   
      fsqr_token = response_hash["access_token"]
      logger.info("Got token: #{fsqr_token}")
      
      return fsqr_token   
  
    rescue
      logger.error("Error: retrieving access token")
      return nil
    end
  end
  
  def get_fsqr_user_info(fsqr_token)
    uri = "https://api.foursquare.com/v2/users/self?oauth_token=#{fsqr_token}&v=20120405"
    http_response = http_get(uri)
    if !http_response
      nil
    end

   response_hash = JSON.parse(http_response)

    # Return a hash of the user's Foursquare settings    
    {
     :fsqr_oauth_token => fsqr_token,
     :fsqr_id => response_hash['response']['user']['id'],
     :first_name => response_hash['response']['user']['firstName'],
     :last_name => response_hash['response']['user']['lastName'],
     :phone_number => response_hash['response']['user']['contact']['phone'],
     :email_address => response_hash['response']['user']['contact']['email']
    }
    
  end

  def http_get(uri)
    begin
      client = HTTPClient.new
      client.get_content(uri)
    rescue
      nil
    end
  end  

protected
  def action_is_public
    ["index", "about", "signin", "create_new_user"].include? params[:action]
  end
  
  def controller_authorize
    unless action_is_public || is_user_logged_in 
      super
    end
  end

end
