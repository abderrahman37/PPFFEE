import hvac

def check_credentials_with_vault(username, password):
    # Connexion au Vault
    client = hvac.Client(url='http://127.0.0.1:8200')
    
    # Vérifie que Vault est accessible
    if not client.is_authenticated():
        print("Vault is not authenticated")
        return False

    try:
        # Récupérer les données pour cet utilisateur
        secret_path = f'secret/data/users/{username}'
        result = client.secrets.kv.v2.read_secret_version(path=f'users/{username}')

        vault_data = result['data']['data']
        stored_username = vault_data['username']
        stored_password = vault_data['password']

        return username == stored_username and password == stored_password

    except Exception as e:
        print("Erreur Vault:", e)
        return False
