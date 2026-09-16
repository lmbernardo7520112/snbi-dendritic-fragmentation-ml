.PHONY: test validate-manifest scope-check

test:
	PYTHONPATH=src python -m unittest discover -s tests -v

validate-manifest:
	PYTHONPATH=src python -m snbi_fragmentation.custody validate configs/sources/source_manifest.json

scope-check:
	PYTHONPATH=src python scripts/check_ti0_scope.py

