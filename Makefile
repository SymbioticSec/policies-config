all: help

run-all: # Run all the scripts
	echo "Generate configuration"
	poetry run python -m scripts.main generate-config > config.json
	echo "Download scanners"
	poetry run python -m scripts.main download-scanners
	echo "Create static data"
	git clone https://github.com/aquasecurity/trivy-checks.git
	poetry run python -m scripts.main generate-static-data trivy-checks/avd_docs
	zip -j iac_rules_remediations.zip output/static-data/*


relase: run-all # Run all the scripts and upload the assets
	gh release upload --clobber $(GITHUB_TAG) config.json output/scanners/* iac_rules_remediations.zip	

.SILENT: all run-all release
.PHONY: all run-all release
