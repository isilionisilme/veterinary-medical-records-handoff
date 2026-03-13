"""Legacy compatibility shim for processing subsystem."""

# Legacy shim — imports moved to backend.app.application.processing/
from backend.app.application.processing import candidate_mining as _candidate_mining
from backend.app.application.processing import confidence_scoring as _confidence_scoring
from backend.app.application.processing import constants as _constants
from backend.app.application.processing import interpretation as _interpretation
from backend.app.application.processing import orchestrator as _orchestrator
from backend.app.application.processing import pdf_extraction as _pdf_extraction
from backend.app.application.processing import scheduler as _scheduler


def _reexport_all(module: object) -> None:
    namespace = getattr(module, "__dict__", {})
    public_names = getattr(module, "__all__", None)
    if public_names is None:
        public_names = [name for name in namespace if not name.startswith("__")]
    for name in public_names:
        globals().setdefault(name, namespace[name])


for _module in (
    _scheduler,
    _orchestrator,
    _interpretation,
    _pdf_extraction,
    _candidate_mining,
    _confidence_scoring,
    _constants,
):
    _reexport_all(_module)

del _module
del _reexport_all
del _scheduler
del _orchestrator
del _interpretation
del _pdf_extraction
del _candidate_mining
del _confidence_scoring
del _constants
