#!/usr/bin/env python3
import os
import shutil
import subprocess
import re

def run_command(cmd, cwd=None):
    """Exécute une commande shell en mode blocking."""
    print(f"Exécution de: {cmd} (dans {cwd if cwd else os.getcwd()})")
    subprocess.run(cmd, shell=True, check=True, cwd=cwd)

def update_file(filepath, replacements=[], regex_replacements=[]):
    """
    Lit un fichier texte, applique une série de remplacements simples (liste de tuples (old, new))
    et de remplacements par expressions régulières (liste de tuples (pattern, new)).
    Si le contenu a changé, le fichier est réécrit.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Impossible de lire {filepath} : {e}")
        return

    original = content
    for old, new in replacements:
        content = content.replace(old, new)
    for pattern, new in regex_replacements:
        content = re.sub(pattern, new, content)
    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Mise à jour du fichier: {filepath}")

def update_file_remove_block(filepath, block):
    """
    Supprime une occurrence exacte d'un bloc de texte dans le fichier.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Impossible de lire {filepath} : {e}")
        return

    if block in content:
        new_content = content.replace(block, "")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Bloc supprimé dans le fichier: {filepath}")

def recursive_update(directory, replacements=[], regex_replacements=[]):
    """
    Parcourt récursivement un dossier et effectue des remplacements dans tous les fichiers texte.
    En cas d’erreur (fichier binaire ou non lisible en utf-8) le fichier est ignoré.
    """
    for root, dirs, files in os.walk(directory):
        for file in files:
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                continue
            original = content
            for old, new in replacements:
                content = content.replace(old, new)
            for pattern, new in regex_replacements:
                content = re.sub(pattern, new, content)
            if content != original:
                try:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"Fichier mis à jour: {path}")
                except Exception as e:
                    print(f"Erreur lors de l'écriture du fichier {path} : {e}")

def remove_block_in_files(directory, block_text):
    """
    Parcourt un dossier et supprime d'éventuelles occurrences d’un bloc donné dans chaque fichier texte.
    """
    for root, dirs, files in os.walk(directory):
        for file in files:
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                continue
            if block_text in content:
                new_content = content.replace(block_text, "")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"Bloc supprimé dans: {path}")

def main():
    # 1. Se placer dans /root et cloner le dépôt s'il n'existe pas déjà
    root_dir = "/root"
    os.chdir(root_dir)
    if not os.path.exists("open-webui"):
        run_command("git clone https://github.com/open-webui/open-webui")
    
    open_webui_dir = os.path.join(root_dir, "open-webui")
    os.chdir(open_webui_dir)

    # 2. Modifier le Dockerfile
    dockerfile_path = os.path.join(open_webui_dir, "Dockerfile")
    update_file(
        dockerfile_path,
        replacements=[
            ('FROM --platform=$BUILDPLATFORM node:22-alpine3.20 AS build',
             'FROM --platform="linux/arm64" node:22-alpine3.20 AS build')
        ]
    )

    # 3. Modifier translation.json pour fr-CA
    frca_path = os.path.join(open_webui_dir, "src", "lib", "i18n", "locales", "fr-CA", "translation.json")
    update_file(
        frca_path,
        replacements=[
            ('"New Chat": "Nouvelle conversation",', '"New Chat": "Nouveau Chat",')
        ]
    )

    # 4. Modifier translation.json pour fr-FR
    frfr_path = os.path.join(open_webui_dir, "src", "lib", "i18n", "locales", "fr-FR", "translation.json")
    update_file(
        frfr_path,
        replacements=[
            ('"New Chat": "Nouvelle conversation",', '"New Chat": "Nouveau Chat",')
        ]
    )

    # 5. Modifier run.sh : image_name et container_name
    run_sh_path = os.path.join(open_webui_dir, "run.sh")
    update_file(
        run_sh_path,
        replacements=[
            ('image_name="open-webui"', 'image_name="genx"'),
            ('container_name="open-webui"', 'container_name="genx"')
        ]
    )

    # 6. Remplacements globaux dans tous les fichiers de /root/open-webui
    global_replacements = [
        ("Open WebUI", "genX"),
        ("WebUI", "genX"),
        ("tim@openwebui.com", "datax@iliad.fr"),
        ("hello@openwebui.com", "datax@iliad.fr"),
        ("sales@openwebui.com", "datax@iliad.fr"),
        ("@openwebui.com", "@iliad.fr"),
        ("https://github.com/tjbck", "https://datax.iliad.fr"),
        ("Timothy J. Baek", "DataX LLM"),
        ("Timothy Jaeryang Baek", "DataX LLM"),
        ("https://docs.openwebui.com/features/plugin/functions/filter", "https://iliad-datax.notion.site/GenX-e28c8f263a2b4876b3606c20051ea992"),
        ("https://docs.openwebui.com/", "https://iliad-datax.notion.site/GenX-e28c8f263a2b4876b3606c20051ea992"),
        ("https://docs.openwebui.com", "https://iliad-datax.notion.site/GenX-e28c8f263a2b4876b3606c20051ea992"),
        ("https://docs.openwebui.com/features/plugin/", "https://iliad-datax.notion.site/GenX-e28c8f263a2b4876b3606c20051ea992")
    ]
    global_regex_replacements = [
        # Cas général pour les autres URLs commençant par "https://github.com/open-webui/"
        (r'https://github\.com/open-webui/[^"]*', "https://iliad-datax.notion.site/GenX-e28c8f263a2b4876b3606c20051ea992"),
        # Traitement des URLs commençant par "https://openwebui.com/"
        (r'https://openwebui\.com/[^"]*', "https://datax.iliad.fr")
    ]

    recursive_update(open_webui_dir, replacements=global_replacements, regex_replacements=global_regex_replacements)

    # 7. Dans /root/open-webui/src/lib, remplacer "OpenWebUI" par "genX"
    src_lib_dir = os.path.join(open_webui_dir, "src", "lib")
    recursive_update(src_lib_dir, replacements=[("OpenWebUI", "genX")])

    # 8. Copier le dossier /root/genx2/static/assets/datax dans /root/open-webui/static/assets/
    src_datax_dir = os.path.join(root_dir, "genx2", "static", "assets", "datax")
    dest_assets_dir = os.path.join(open_webui_dir, "static", "assets", "datax")
    if os.path.exists(dest_assets_dir):
        shutil.rmtree(dest_assets_dir)
    shutil.copytree(src_datax_dir, dest_assets_dir)
    print(f"Dossier copié: {src_datax_dir} -> {dest_assets_dir}")

    # 9. Remplacer le fichier favicon.png
    src_favicon = os.path.join(root_dir, "genx2", "static", "assets", "datax", "icons", "favicon.png")
    dest_favicon = os.path.join(open_webui_dir, "static", "favicon.png")
    if os.path.exists(src_favicon):
        shutil.copy2(src_favicon, dest_favicon)
        print(f"Favicon copié: {src_favicon} -> {dest_favicon}")

    # 10. Remplacer les icônes dans /root/open-webui/static et /root/open-webui/backend/open_webui/static
    icon_files = [
        "apple-touch-icon.png", "favicon-96x96.png", "favicon-dark.png", "favicon.ico",
        "favicon.png", "favicon.svg", "logo.png", "splash-dark.png", "splash.png",
        "web-app-manifest-192x192.png", "web-app-manifest-512x512.png"
    ]
    src_icons_dir = os.path.join(root_dir, "genx2", "static", "assets", "datax", "icons")
    dest_dirs = [
        os.path.join(open_webui_dir, "static"),
        os.path.join(open_webui_dir, "backend", "open_webui", "static")
    ]
    for d in dest_dirs:
        for f_icon in icon_files:
            src_icon_file = os.path.join(src_icons_dir, f_icon)
            dest_icon_file = os.path.join(d, f_icon)
            if os.path.exists(src_icon_file):
                shutil.copy2(src_icon_file, dest_icon_file)
                print(f"Icône '{f_icon}' mise à jour dans: {d}")

    # 11. Remplacer le contenu de /root/genx2/src/lib/components/chat/Settings/About.svelte
    src_about = os.path.join(open_webui_dir, "src", "lib", "components", "chat", "Settings", "About.svelte")
    dest_about = os.path.join(root_dir, "genx2", "src", "lib", "components", "chat", "Settings", "About.svelte")
    if os.path.exists(src_about):
        shutil.copy2(src_about, dest_about)
        print(f"Fichier About.svelte mis à jour: {src_about} -> {dest_about}")

    # 12. Supprimer le bloc de redistribution dans tous les fichiers de /root/open-webui
    redistribution_block = """Redistribution and use in source and binary forms, with or without
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
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."""
    remove_block_in_files(open_webui_dir, redistribution_block)

    # 13. Supprimer le bloc dans About.svelte (Settings)
    about_block ="""
		{#if ollamaVersion}
			<hr class=" border-gray-100 dark:border-gray-850" />

			<div>
				<div class=" mb-2.5 text-sm font-medium">{$i18n.t('Ollama Version')}</div>
				<div class="flex w-full">
					<div class="flex-1 text-xs text-gray-700 dark:text-gray-200">
						{ollamaVersion ?? 'N/A'}
					</div>
				</div>
			</div>
		{/if}

		<hr class=" border-gray-100 dark:border-gray-850" />

		{#if $config?.license_metadata}
			<div class="mb-2 text-xs">
				{#if !$WEBUI_NAME.includes('genX')}
					<span class=" text-gray-500 dark:text-gray-300 font-medium">{$WEBUI_NAME}</span> -
				{/if}

				<span class=" capitalize">{$config?.license_metadata?.type}</span> license purchased by
				<span class=" capitalize">{$config?.license_metadata?.organization_name}</span>
			</div>
		{:else}
			<div class="flex space-x-1">
				<a href="https://discord.gg/5rJgQTnV4s" target="_blank">
					<img
						alt="Discord"
						src="https://img.shields.io/badge/Discord-Open_genX-blue?logo=discord&logoColor=white"
					/>
				</a>

				<a href="https://twitter.com/OpengenX" target="_blank">
					<img
						alt="X (formerly Twitter) Follow"
						src="https://img.shields.io/twitter/follow/OpengenX"
					/>
				</a>

				<a href="https://iliad-datax.notion.site/GenX-e28c8f263a2b4876b3606c20051ea992" target="_blank">
					<img
						alt="Github Repo"
						src="https://img.shields.io/github/stars/open-webui/open-webui?style=social&label=Star us on Github"
					/>
				</a>
			</div>
		{/if}"""
    update_file_remove_block(
        os.path.join(open_webui_dir, "src", "lib", "components", "chat", "Settings", "About.svelte"),
        about_block
    )

    # 14. Supprimer le bloc dans General.svelte (Settings Admin)
    general_block = """	
						<div class="mt-1">
							<div class="flex space-x-1">
								<a href="https://discord.gg/5rJgQTnV4s" target="_blank">
									<img
										alt="Discord"
										src="https://img.shields.io/badge/Discord-Open_genX-blue?logo=discord&logoColor=white"
									/>
								</a>

								<a href="https://twitter.com/OpengenX" target="_blank">
									<img
										alt="X (formerly Twitter) Follow"
										src="https://img.shields.io/twitter/follow/OpengenX"
									/>
								</a>

								<a href="https://iliad-datax.notion.site/GenX-e28c8f263a2b4876b3606c20051ea992" target="_blank">
									<img
										alt="Github Repo"
										src="https://img.shields.io/github/stars/open-webui/open-webui?style=social&label=Star us on Github"
									/>
								</a>
							</div>
						</div>"""
    update_file_remove_block(
        os.path.join(open_webui_dir, "src", "lib", "components", "admin", "Settings", "General.svelte"),
        general_block
    )

    # 15. Copier le fichier datax.txt dans /root/open-webui/
    src_datax_txt = os.path.join(root_dir, "genx2", "datax.txt")
    dest_datax_txt = os.path.join(open_webui_dir, "datax.txt")
    if os.path.exists(src_datax_txt):
        shutil.copy2(src_datax_txt, dest_datax_txt)
        print(f"datax.txt copié vers {dest_datax_txt}")

    # 16. Copier le fichier run_update.py dans /root/open-webui/
    src_run_update = os.path.join(root_dir, "genx2", "run_update.py")
    dest_run_update = os.path.join(open_webui_dir, "run_update.py")
    if os.path.exists(src_run_update):
        shutil.copy2(src_run_update, dest_run_update)
        print(f"run_update.py copié vers {dest_run_update}")

    # 17. Remplacer le run.sh de /root/open-webui par celui de /root/genx2
    src_run_sh = os.path.join(root_dir, "genx2", "run.sh")
    dest_run_sh = os.path.join(open_webui_dir, "run.sh")
    if os.path.exists(src_run_sh):
        shutil.copy2(src_run_sh, dest_run_sh)
        print(f"Fichier run.sh remplacé : {src_run_sh} -> {dest_run_sh}")
    else:
        print(f"Le fichier source {src_run_sh} n'existe pas, impossible de remplacer run.sh.")

    # 18. Rendre run.sh exécutable
    run_command("chmod +x run.sh", cwd=open_webui_dir)

    # 19. Exécuter run.sh
    run_command("./run.sh", cwd=open_webui_dir)
    
if __name__ == "__main__":
    main()
