.PHONY: test bootstrap-tests validate-manifest data-guard bootstrap-check scope-check local-diagnostics

test:
	PYTHONPATH=src python -m unittest discover -s tests -v

bootstrap-tests:
	PYTHONPATH=src /usr/bin/python3 -B -m unittest -v \
		tests/test_repository_data_guard.py \
		tests/test_local_bootstrap.py \
		tests/test_local_environment.py

validate-manifest:
	PYTHONPATH=src python -m snbi_fragmentation.custody validate configs/sources/source_manifest.json

scope-check:
	PYTHONPATH=src python scripts/check_ti1_scope.py

data-guard:
	/usr/bin/python3 -B scripts/check_repository_data.py

bootstrap-check:
	/usr/bin/python3 -B scripts/check_local_bootstrap.py

local-diagnostics:
	/usr/bin/python3 -B scripts/check_local_environment.py
