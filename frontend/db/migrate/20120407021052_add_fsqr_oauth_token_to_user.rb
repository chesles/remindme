class AddFsqrOauthTokenToUser < ActiveRecord::Migration
  def self.up
    add_column :users, :fsqr_oauth_token, :string, :null => false
  end

  def self.down
    remove_column :users, :fsqr_oauth_token
  end
end
