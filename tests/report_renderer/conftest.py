import pytest

from infra.report_renderer import analysis_checkpoint, diagnostics, incremental, adaptive_groups


@pytest.fixture(autouse=True)
def diagnostics_root(tmp_path, monkeypatch):
    directory = tmp_path / "diagnosticos-privados"
    monkeypatch.setattr(diagnostics, "DIAGNOSTICS_DIR", directory)
    monkeypatch.setattr(analysis_checkpoint, "CHECKPOINTS_DIR", tmp_path / "checkpoints-privados")
    return directory


@pytest.fixture(autouse=True)
def sequential_regressions(monkeypatch):
    # Os testes antigos verificam a ordem sequencial. Casos concorrentes
    # habilitam explicitamente dois lotes e verificam também a interlevação.
    monkeypatch.setattr(incremental, "MAX_PARALLEL_BATCHES", 1)
    # Regressões anteriores fixam oito; novos casos ativam a adaptação.
    monkeypatch.setattr(adaptive_groups, "ENABLED", False)
