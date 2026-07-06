from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

def autenticar_drive():
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("credentials/mycreds.json")  # tenta carregar o token salvo

    if gauth.credentials is None:
        gauth.LocalWebserverAuth()  # abre o navegador para login
    elif gauth.access_token_expired:
        gauth.Refresh()  # renova o token se estiver expirado
    else:
        gauth.Authorize()  # usa o token existente

    gauth.SaveCredentialsFile("credentials/mycreds.json")  # salva o token para reutilizar
    return GoogleDrive(gauth)

def upload_to_drive(file_path, folder_id):
    drive = autenticar_drive()
    file = drive.CreateFile({
        'title': file_path.split('/')[-1],
        'parents': [{'id': folder_id}]
    })
    file.SetContentFile(file_path)
    file.Upload()
    print(f"✅ Arquivo enviado para Google Drive: {file['title']}")
