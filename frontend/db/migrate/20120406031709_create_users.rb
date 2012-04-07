class CreateUsers < ActiveRecord::Migration
  def self.up
    create_table :users do |t|
      t.string :username, :null => false, :unique => true
      t.string :first_name, :null => false
      t.string :last_name, :null => false
      t.string :phone_number, :null => false
      t.string :email_address, :null => false
      t.string :fsqr_id, :null => false
      t.integer :user_type, :null => false, :default => 1

      t.timestamps
    end
  end

  def self.down
    drop_table :users
  end
end
