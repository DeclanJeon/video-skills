"""Actual existing programs run tiny private synthetic E3 smoke; this is not a vendor-installation or real-media test."""
from pathlib import Path
import pytest
from conftest import require
from test_install_consent import plan


@pytest.mark.parametrize('tool',['filmcraft','effectcraft','soundcraft'])
def test_installer_smoke_when_actual_existing_cli_has_native_output_and_network_denial(tmp_path,tool):
    p=plan(tool=tool)
    runner=require('environment.native_smoke','NativeSmoke')(tmp_path/'owned-smoke')
    result=runner.run(p,(Path('/usr/bin')/(tool+'-cli'),))
    assert result.passed is True
    assert result.network_denied is True
    assert 'synthetic' in result.evidence
