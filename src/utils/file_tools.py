import os

def list_files(directory: str, ext: str = None):
    """Liste les fichiers d’un dossier, filtrés par extension."""
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and (not ext or f.endswith(ext))]
