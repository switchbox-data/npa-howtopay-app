# NPA How to Pay App - Just Commands

# Prepare and deploy the Shiny app to shinyapps.io
publish:
    # Update the project environment
    uv sync
    # Generate the requirements.txt file
    uv export --no-hashes -o requirements.txt
    # Generate the manifest.json file with correct entrypoint (from root, pointing to subdirectory)
    uvx --from rsconnect-python --python .venv/bin/python rsconnect write-manifest shiny . --entrypoint npa_howtopay_app.app:app --overwrite
    # Deploy to shinyapps.io (from root directory)
    rsconnect deploy shiny $(pwd)/npa_howtopay_app --name switchbox --title "NPA How to Pay App"

# Just sync the environment
sync:
    uv sync

# Generate requirements.txt
requirements:
    uv export --no-hashes -o requirements.txt

# Generate manifest.json
manifest:
    uvx --from rsconnect-python --python .venv/bin/python rsconnect write-manifest shiny . --entrypoint npa_howtopay_app.app:app --overwrite

tmp:
    rsconnect deploy shiny /Users/alexsmith/Documents/switchbox/npa-howtopay-app/npa_howtopay_app --name switchbox --title "NPA How to Pay App"