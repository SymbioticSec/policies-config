# Static data generation

This script generates static data for some rules. To use it:

1. Download the AVD docs from the [trivy-checks](https://github.com/aquasecurity/trivy-checks/tree/main/avd_docs) repository.
2. Run `poetry run python -m scripts.main generate-static-data <path-to-avd-docs>`.

This will generate a JSON file for each AVD rule, containing the description and remediation snippet.
Trivy rules with no description or remediation snippet will not be generated.
