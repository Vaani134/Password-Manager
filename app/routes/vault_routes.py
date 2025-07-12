"""Vault management routes using hybrid vault system."""
from flask import Blueprint,request , jsonify , session
from ..services.hybrid_auth import verify_master_password_hybrid , get_current_user
from ..services.hybrid_vault import HybridVaultServices

vault_bp=Blueprint("vault", __name__)

@vault_bp.route('/export', methods=['POST'])
def export_to_vault():
    """Export all user passwords to encrypted vault"""
    current_user=get_current_user()
    if not current_user:
        return jsonify({'error': 'User not authenticated'}), 401
    
    data=request.get_json()
    if 'master_password' not in data:
        return jsonify({'error': 'Master password required'}), 400

    # Verify master password and get key
    user,key =verify_master_password_hybrid(current_user.id,data['master_password'])
    if not user or not key:
        return jsonify({'error': 'Invalid master password'}), 401
    
    try:
        # Create vault service and export
        vault_service=HybridVaultServices(user.username,key)
        vault_data =vault_service.export_to_vault(user.id)

        return jsonify({
            'message': 'Passwords exported to vault successfully',
            'exported_count': len(vault_data)
        }), 200
    
    except Exception as e:
        return jsonify({'error': 'Failed to export to vault'}), 500
    

    
@vault_bp.route('/import', methods=['POST'])
def import_from_vault():
    """Import vault data and display it."""
    current_user=get_current_user()
    if not current_user:
        return jsonify({'error': 'User not authenticated'}), 401
        
    data=request.get_json()
    if 'master_password' not in data:
        return jsonify({'error': 'Master password required'}), 400

    # Verify master password and get key
    user,key =verify_master_password_hybrid(current_user.id,data['master_password'])
    if not user or not key:
        return jsonify({'error': 'Invalid master password'}), 401
        
    try:
        # Create vault service and export
        vault_service=HybridVaultServices(user.username,key)
        vault_data =vault_service.import_from_vault()

        return jsonify({
        'message': 'Vault data retrieved successfully',
        'vault_data': vault_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to import from vault'}), 500
    
@vault_bp.route('/sync', methods=['POST'])
def sync_vault_to_db():
    """Sync vault data back to database."""
    current_user=get_current_user()
    if not current_user:
        return jsonify({'error': 'User not authenticated'}), 401
        
    data=request.get_json()
    if 'master_password' not in data:
        return jsonify({'error': 'Master password required'}), 400

    # Verify master password and get key
    user,key =verify_master_password_hybrid(current_user.id,data['master_password'])
    if not user or not key:
        return jsonify({'error': 'Invalid master password'}), 401
        
    try:
        # Create vault service and export
        vault_service=HybridVaultServices(user.username,key)
        vault_service.sync_vault_to_db(user.id,data['master_password'], user.Salted_masterkey)  

        return jsonify({'message': 'Vault synced to database successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to sync vault to database'}), 500

    

