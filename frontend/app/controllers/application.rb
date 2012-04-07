# Filters added to this controller apply to all controllers in the application.
# Likewise, all the methods added will be available for all controllers.

class ApplicationController < ActionController::Base
  before_filter :authorize 
  helper :all # include all helpers, all the time
  
  layout "home"

  # See ActionController::RequestForgeryProtection for details
  # Uncomment the :secret if you're not using the cookie session store
  protect_from_forgery :secret => 'c68fb955cee6becaab6eb8620619fb60'
  
  # See ActionController::Base for details 
  # Uncomment this to filter the contents of submitted sensitive data parameters
  # from your application log (in this case, all fields with names like "password"). 
  # filter_parameter_logging :password
  
protected
  def authorize
    controller_authorize
  end
  
  def controller_authorize
    flash[:notice] = 'You do not have access to view this page!'
    flash[:level] = :error
    redirect_to :controller => 'home', :action => 'index'
  end
  
  def is_user_logged_in()
    User.find_by_id(session[:user_id]) != nil
  end
  
  def is_admin_logged_in()
    user = User.find_by_id(session[:user_id]) 
    user != nil && user.is_admin
  end
end
