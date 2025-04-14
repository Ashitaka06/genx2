#!/bin/bash

# Variables
REPO_URL="https://github.com/open-webui/open-webui"
OPENWEBUI_DIR="/root/open-webui"
GENX_DIR="/root/genx2"

# Clone du repository
cd /root/
git clone "$REPO_URL"

cd "$OPENWEBUI_DIR"

# Modification du Dockerfile
sed -i 's/FROM --platform=\$BUILDPLATFORM node:22-alpine3.20 AS build/FROM --platform="linux\/arm64" node:22-alpine3.20 AS build/g' Dockerfile

# Modifications dans translation.json
sed -i 's/"New Chat": "Nouvelle conversation"/"New Chat": "Nouveau Chat"/g' src/lib/i18n/locales/fr-CA/translation.json
sed -i 's/"New Chat": "Nouvelle conversation"/"New Chat": "Nouveau Chat"/g' src/lib/i18n/locales/fr-FR/translation.json

# Modifications dans run.sh
sed -i 's/image_name="open-webui"/image_name="genx"/g' run.sh
sed -i 's/container_name="open-webui"/container_name="genx"/g' run.sh

# Remplacements globaux
grep -rlZ 'Open WebUI' . | xargs -0 sed -i 's/Open WebUI/genX/g'
grep -rlZ 'WebUI' . | xargs -0 sed -i 's/WebUI/genX/g'
grep -rlZE "(tim@openwebui.com|hello@openwebui.com|sales@openwebui.com)" . | xargs -0 sed -Ei 's/(tim|hello|sales)@openwebui.com/datax@iliad.fr/g'
grep -rlZ '@openwebui.com' . | xargs -0 sed -i 's/@openwebui.com/@iliad.fr/g'
grep -rlZ 'https://github.com/tjbck' . | xargs -0 sed -i 's|https://github.com/tjbck|https://datax.iliad.fr|g'
grep -rlZE "Timothy J. Baek|Timothy Jaeryang Baek" . | xargs -0 sed -Ei 's/Timothy (J\.|Jaeryang) Baek/DataX LLM/g'
grep -rlZE "https://docs.openwebui.com/features/plugin/functions/filter|https://docs.openwebui.com/?(features/plugin/)?" . | xargs -0 sed -Ei 's|https://docs.openwebui.com[^\"]*|https://iliad-datax.notion.site/GenX-e28c8f263a2b4876b3606c20051ea992|g'
grep -rlZ 'https://github.com/open-webui/' . | xargs -0 sed -Ei 's|https://github.com/open-webui/[^\"]*|https://iliad-datax.notion.site/GenX-e28c8f263a2b4876b3606c20051ea992|g'
grep -rlZ 'https://openwebui.com/' . | xargs -0 sed -Ei 's|https://openwebui.com/[^\"]*|https://datax.iliad.fr|g'
grep -rlZ 'OpenWebUI' src/lib | xargs -0 sed -i 's/OpenWebUI/genX/g'

# Copie des assets et icônes
cp -r "$GENX_DIR/static/assets/datax" "$OPENWEBUI_DIR/static/assets/"
cp "$GENX_DIR/static/assets/datax/icons/favicon.png" "$OPENWEBUI_DIR/static/favicon.png"

ICONS=(apple-touch-icon.png favicon-96x96.png favicon-dark.png favicon.ico favicon.png favicon.svg splash-dark.png splash.png web-app-manifest-192x192.png web-app-manifest-512x512.png)
for ICON in "${ICONS[@]}"; do
  cp "$GENX_DIR/static/assets/datax/icons/$ICON" "$OPENWEBUI_DIR/static/$ICON"
  cp "$GENX_DIR/static/assets/datax/icons/$ICON" "$OPENWEBUI_DIR/backend/open_webui/static/$ICON"
done

# Remplacement contenu About.svelte
cp "$GENX_DIR/src/lib/components/chat/Settings/About.svelte" "$OPENWEBUI_DIR/src/lib/components/chat/Settings/About.svelte"

# Suppressions spécifiques (license et références discord/github/twitter/ollama)
find . -type f -exec sed -i '/Redistribution and use in source and binary forms/,/EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE\./d' {} \;

sed -i '/{#if ollamaVersion}/,/{\/if}/d' "$OPENWEBUI_DIR/src/lib/components/chat/Settings/About.svelte"
sed -i '/<div class="mt-1">/,/<\/div>/d' "$OPENWEBUI_DIR/src/lib/components/admin/Settings/General.svelte"
sed -i '/<div class="mb-2.5">/,/<\/div>/d' "$OPENWEBUI_DIR/src/lib/components/admin/Settings/General.svelte"

# Copie fichiers supplémentaires
cp "$GENX_DIR/DataX.txt" "$OPENWEBUI_DIR/"
cp "$GENX_DIR/run_update.sh" "$OPENWEBUI_DIR/"

# Donner les droits d'exécution
chmod +x run_update.sh
chmod +x run.sh

# Lancement du script run.sh
./run.sh