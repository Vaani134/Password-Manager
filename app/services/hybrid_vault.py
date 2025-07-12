"""Hybrid vault service combining individual passwords with vault storage."""

from .sqlite.vault_handler import VaultHandler
from ..models import User_passwords
from .. import db


class HybridVaultServices:
    def __init__(self,username:str ,key:bytes ):
        self.username=username
        self.key=key
        self.vault_handler= VaultHandler(username,key)

    def export_to_vault(self,user_id :int):
       
       """Export SQLAlchemy passwords to vault format."""
       passwords=User_passwords.query.filter_by(user_id=user_id).all()

       vault_data ={}
       for pwd in passwords:
            vault_data[pwd.website_name]={
               'username': pwd.username,
               'website_url':pwd.website_url,
               'notes':pwd.notes,
               'password_id':pwd.id
            }
       self.vault_handler.save_vault(vault_data)
       return vault_data
    
    def import_from_vault(self):
        """Load vault data."""
        return self.vault_handler.load_vault()
    
    def sync_vault_to_db(self,user_id:int,master_password:str, user_salt:str):
        """Sync vault data back to individual password entries."""
        vault_data = self.import_from_vault()

        for website,data in vault_data.items():
            # Check if password entry exists
            existing =User_passwords.query.filter_by(
                user_id=user_id,
                website_name=website
            ).first()

            if not existing:
                # Create new password entry
                new_pwd = User_passwords(
                    user_id=user_id,
                    website_name=website,
                    website_url=data.get('website_url', ''),
                    username=data.get('username', ''),
                    notes=data.get('notes', '')
                )

                db.session.add(new_pwd)
            
        db.session.commit()
           

