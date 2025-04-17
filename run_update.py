import logging
import os
import shutil
import subprocess
import re
import json
from pathlib import Path

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def run_command(cmd: str, cwd: Path = None):
    """Exécute une commande shell en mode bloquant et journalise chaque étape."""
    cwd_display = cwd or Path.cwd()
    logger.info(f"Exécution de la commande: {cmd} (dans {cwd_display})")
    cwd_arg = str(cwd) if cwd else None
    try:
        subprocess.run(cmd, shell=True, check=True, cwd=cwd_arg)
        logger.info(f"Commande terminée avec succès: {cmd}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Échec de la commande `{cmd}`: {e}")
        raise


def update_file(filepath: Path, replacements: list[tuple[str, str]]):
    """
    Lit un fichier texte, applique des remplacements de mots entiers.
    Si le contenu change, réécrit le fichier et journalise l'opération.
    """
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        logger.debug(f"Impossible de lire {filepath}: {e}")
        return

    original = content
    for old, new in replacements:
        pattern = rf"\b{re.escape(old)}\b"
        content = re.sub(pattern, new, content)

    if content != original:
        try:
            filepath.write_text(content, encoding='utf-8')
            logger.info(f"Fichier mis à jour: {filepath}")
        except Exception as e:
            logger.error(f"Erreur lors de l'écriture de {filepath}: {e}")


def update_translation_file(filepath: Path, mapping: dict[str, str]):
    """
    Met à jour un fichier translation.json en remplaçant les valeurs des clés spécifiées.
    """
    try:
        content = filepath.read_text(encoding='utf-8')
        data = json.loads(content)
    except Exception as e:
        logger.debug(f"Impossible de lire ou parser JSON {filepath}: {e}")
        return

    original = dict(data)
    for key, new_val in mapping.items():
        if key in data and data[key] != new_val:
            data[key] = new_val

    if data != original:
        try:
            filepath.write_text(
                json.dumps(data, ensure_ascii=False, indent=4), encoding='utf-8'
            )
            logger.info(f"Fichier de traduction mis à jour: {filepath}")
        except Exception as e:
            logger.error(f"Erreur écriture JSON {filepath}: {e}")


def remove_block_in_file(filepath: Path, block_text: str):
    """
    Supprime une occurrence exacte d'un bloc de texte dans un fichier.
    """
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        logger.debug(f"Impossible de lire {filepath}: {e}")
        return
    if block_text in content:
        new_content = content.replace(block_text, '')
        try:
            filepath.write_text(new_content, encoding='utf-8')
            logger.info(f"Bloc supprimé dans {filepath}")
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du bloc dans {filepath}: {e}")
    else:
        logger.debug(f"Bloc non trouvé dans {filepath}")


def remove_regex_in_file(filepath: Path, regex_pattern: str):
    """
    Supprime les occurrences correspondant à une regex (DOTALL) dans un fichier.
    """
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        logger.debug(f"Impossible de lire {filepath}: {e}")
        return
    new_content = re.sub(regex_pattern, '', content, flags=re.DOTALL)
    if new_content != content:
        try:
            filepath.write_text(new_content, encoding='utf-8')
            logger.info(f"Regex supprimé dans {filepath}")
        except Exception as e:
            logger.error(f"Erreur suppression regex dans {filepath}: {e}")


def remove_block_in_files(directory: Path, block_text: str):
    """
    Parcourt un dossier et supprime un bloc fixe dans chaque fichier.
    """
    for path in directory.rglob('*'):
        if path.is_file():
            remove_block_in_file(path, block_text)


def recursive_replace(directory: Path, replacements: list[tuple[str, str]]):
    """
    Parcourt récursivement un dossier et effectue des remplacements sur mots entiers.
    """
    for path in directory.rglob('*'):
        if not path.is_file():
            continue
        try:
            content = path.read_text(encoding='utf-8')
        except Exception:
            continue
        new_content = content
        for old, new in replacements:
            pattern = rf"\b{re.escape(old)}\b"
            new_content = re.sub(pattern, new, new_content)
        if new_content != content:
            try:
                path.write_text(new_content, encoding='utf-8')
                logger.info(f"Remplacements globaux appliqués à {path}")
            except Exception as e:
                logger.error(f"Erreur écriture {path}: {e}")


def copy_directory(src: Path, dst: Path, overwrite: bool = False):
    """Copie un dossier en remplaçant l'existant si nécessaire."""
    if dst.exists() and overwrite:
        shutil.rmtree(dst)
        logger.info(f"Suppression du dossier existant: {dst}")
    shutil.copytree(src, dst)
    logger.info(f"Dossier copié: {src} -> {dst}")


def copy_file(src: Path, dst: Path):
    """Copie un fichier si la source existe."""
    if src.exists():
        shutil.copy2(src, dst)
        logger.info(f"Fichier copié: {src} -> {dst}")
    else:
        logger.debug(f"Fichier introuvable, non copié: {src}")

def replace_regex_in_file(filepath: Path, pattern: str, repl: str):
    try:
        text = filepath.read_text(encoding='utf-8')
    except (UnicodeDecodeError, Exception) as e:
        logger.debug(f"Impossible de lire {filepath} en UTF-8, on l'ignore : {e}")
        return

    new = re.sub(pattern, repl, text, flags=re.MULTILINE)
    if new != text:
        try:
            filepath.write_text(new, encoding='utf-8')
            logger.info(f"Applied regex replace in {filepath}")
        except Exception as e:
            logger.error(f"Impossible d’écrire {filepath} après regex replace : {e}")

def recursive_regex_replace(directory: Path, pattern: str, repl: str):
    for path in directory.rglob('*'):
        if not path.is_file():
            continue
        replace_regex_in_file(path, pattern, repl)

def main():
    root_dir = Path('/root')
    repo_dir = root_dir / 'open-webui'
    docker_container = 'open-webui'

    # Étape 1: Cloner le dépôt
    logger.info('Étape 1: Clonage du dépôt')
    os.chdir(root_dir)
    if not repo_dir.exists():
        run_command('git clone https://github.com/open-webui/open-webui')

    # Étape 2: Export de la base de données
    logger.info('Étape 2: Export de la base de données depuis Docker')
    os.chdir(repo_dir)
    run_command(f'docker cp {docker_container}:/app/backend/data/webui.db {repo_dir}/webui.db')

    # Étape 3: Mise à jour du Dockerfile
    logger.info('Étape 3: Mise à jour du Dockerfile')
    dockerfile = repo_dir / 'Dockerfile'
    update_file(
        dockerfile,
        [('FROM --platform=$BUILDPLATFORM node:22-alpine3.20 AS build',
          'FROM --platform="linux/arm64" node:22-alpine3.20 AS build')]
    )

    # Étape 4: Traductions FR
    logger.info('Étape 4: Mise à jour des fichiers de traduction pour le français')
    translation_mapping = {
        "New Chat": "Nouveau Chat",
        "Upload files": "Importer un fichier",
        "Upload Files": "Importer un fichier",
        "Capture": "Capture de l'écran"
    }
    for loc in ['fr-CA', 'fr-FR']:
        path = repo_dir / 'src' / 'lib' / 'i18n' / 'locales' / loc / 'translation.json'
        update_translation_file(path, translation_mapping)

    # Étape 4b: Suppression du bloc ollamaVersion + license dans About.svelte
    logger.info('Étape 4b: Suppression du bloc ollamaVersion + license dans About.svelte')
    about_file = repo_dir / 'src' / 'lib' / 'components' / 'chat' / 'Settings' / 'About.svelte'
    remove_regex_in_file(
        about_file,
        r"\{#if ollamaVersion\}[\s\S]*\{/if\}"
    )

    # Étape 4c: Suppression du bloc des badges Help (Discord, Twitter, GitHub) dans General.svelte
    logger.info('Étape 4c: Suppression du bloc des badges Help dans General.svelte')
    general_file = repo_dir / 'src' / 'lib' / 'components' / 'admin' / 'Settings' / 'General.svelte'
    remove_regex_in_file(
        general_file,
        r'<div class="mt-1">\s*<div class="flex space-x-1">[\s\S]*?<\/div>\s*<\/div>'
    )

    # Étape 4d: Suppression du bloc License dans General.svelte
    logger.info('Étape 4d: Suppression du bloc License dans General.svelte')
    remove_regex_in_file(
        general_file,
        r'<div class="mb-2\.5">\s*<div class="flex w-full justify-between items-center">[\s\S]*?\{\$i18n\.t\(\'License\'\)\}[\s\S]*?<\/div>\s*<\/div>'
    )

    # Étape 5: Remplacements globaux
    logger.info('Étape 5: Remplacements globaux dans tout le projet')
    global_replacements = [
        ('Open WebUI', 'genX'),
        ('WebUI',      'genX'),
        ('https://openwebui.com',        'https://genx.datax.iliad.fr'),
        ('https://github.com/tjbck',     'https://datax.iliad.fr'),
        ('Timothy J. Baek',              'DataX LLM'),
        ('Timothy Jaeryang Baek',        'DataX LLM'),
    ]
    recursive_replace(repo_dir, global_replacements)

    # Étape 5b: Remplacement **exact** de la racine docs.openwebui.com
    logger.info('Étape 5b: Remplacement exact du domaine docs.openwebui.com')
    # negative lookahead (?!/) : n’affecte pas les URLs qui continuent par un slash
    docs_pattern = r'https://docs\.openwebui\.com(?!/)'
    docs_repl    = 'https://iliad-datax.notion.site/GenX-e28c8f263a2b4876b3606c20051ea992'
    recursive_regex_replace(repo_dir, docs_pattern, docs_repl)

    # Étape 6: Copie des assets DataX
    logger.info('Étape 6: Copie des assets DataX')
    copy_directory(root_dir / 'genx2' / 'static' / 'assets' / 'datax',
                   repo_dir / 'static' / 'assets' / 'datax', overwrite=True)

    # Étape 7: Mise à jour des icônes
    logger.info('Étape 7: Mise à jour des icônes')
    icons = [
        'apple-touch-icon.png', 'favicon-96x96.png', 'favicon-dark.png', 'favicon.ico',
        'favicon.png', 'favicon.svg', 'logo.png', 'splash-dark.png', 'splash.png',
        'web-app-manifest-192x192.png', 'web-app-manifest-512x512.png'
    ]
    src_icons = root_dir / 'genx2' / 'static' / 'assets' / 'datax' / 'icons'
    for dest in [repo_dir / 'static' / 'static', repo_dir / 'backend' / 'open_webui' / 'static']:
        for icon in icons:
            copy_file(src_icons / icon, dest / icon)

    # Étape 8: Suppression du bloc de redistribution
    logger.info('Étape 8: Suppression du bloc de redistribution')
    redistribution_block = ("""Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.""")
    remove_block_in_files(repo_dir, redistribution_block)

    # Étape 9: Copie de fichiers additionnels
    logger.info('Étape 9: Copie de datax.txt et run_update.py')
    copy_file(root_dir / 'genx2' / 'datax.txt', repo_dir / 'datax.txt')
    copy_file(root_dir / 'genx2' / 'run_update.py', repo_dir / 'run_update.py')

    # Étape 10: Permissions et exécution de run.sh
    logger.info("Étape 10: Rendre run.sh exécutable et l'exécuter")
    run_command('chmod +x run.sh', cwd=repo_dir)
    run_command('./run.sh', cwd=repo_dir)

    # Étape 11: Mise à jour du conteneur Docker
    logger.info('Étape 11: Import de la base de données et redémarrage du conteneur')
    run_command(f'docker stop {docker_container}')
    run_command(f'docker cp {repo_dir}/webui.db {docker_container}:/app/backend/data/webui.db')
    run_command(f'docker start {docker_container}')


if __name__ == '__main__':
    main()