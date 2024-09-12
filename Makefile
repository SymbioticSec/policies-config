all: help

clone-trivy-checks: # Clone trivy checks repository
	poetry run python -m scripts.main clone-trivy-checks

generate-config: # Generate configuration
	poetry run python -m scripts.main generate-config > config.json

download-scanners: # Download scanners
	poetry run python -m scripts.main download-scanners

generate-ide-static-data: clone-trivy-checks # Generate static data for ide plugin
	poetry run python -m scripts.main generate-static-data trivy-checks/avd_docs
	zip -j iac_rule_remediations.zip output/static-data/*

download-rules: clone-trivy-checks # Download rules
	mkdir -p output
	./bin/download-rules trivy-checks/checks/cloud > output/rules.json

run-all: generate-config download-scanners generate-ide-static-data download-rules # Run all the scripts

release: run-all # Run all the scripts and upload the assets
	gh release upload --clobber $(GITHUB_TAG) config.json output/scanners/* iac_rule_remediations.zip output/rules.json

.SILENT: all clone-trivy-checks generate-config download-scanners generate-ide-static-data download-rules run-all release
.PHONY: all clone-trivy-checks generate-config download-scanners generate-ide-static-data download-rules run-all release
