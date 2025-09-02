# NPA How to Pay App - Just Commands

# Prepare and deploy the Shiny app to RStudio Connect
publish:
    # Update the project environment
    uv sync
    # Generate the requirements.txt file
    uv export --no-hashes -o requirements.txt
    # Generate the manifest.json file with correct entrypoint
    uvx --from rsconnect-python --python .venv/bin/python rsconnect write-manifest shiny . --entrypoint npa_howtopay_app.app:app --overwrite
    # Deploy to RStudio Connect
    rsconnect deploy shiny . --name switchbox --title "NPA How to Pay App"

# Just sync the environment
sync:
    uv sync

# Generate requirements.txt
requirements:
    uv export --no-hashes -o requirements.txt

# Generate manifest.json
manifest:
    uvx --from rsconnect-python --python .venv/bin/python rsconnect write-manifest shiny . --entrypoint npa_howtopay_app.app:app --overwrite
