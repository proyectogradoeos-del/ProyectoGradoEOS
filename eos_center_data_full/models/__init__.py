# -*- coding: utf-8 -*-
# Importación de todos los modelos del módulo EOS Center Data
# Orden: de menos dependencias a más dependencias entre modelos.
#
# Componente 1 — Visión (base de todo EOS)
from . import eos_vision         # EosVision, EosVisionRock
from . import eos_vision_score   # EosVisionScore
# Componente 2 — Personas
from . import eos_people         # EosSeat, EosPeopleEvaluation
# Componente 3 — Datos
from . import eos_data           # EosScorecard, EosKpi, EosKpiRecord, EosOkr, EosOkrKeyResult
# Componente 4 — Problemas
from . import eos_issues         # EosIssue
# Componente 5 — Procesos
from . import eos_processes      # EosProcess, EosProcessStep
# Componente 6 — Tracción (depende de todos los anteriores)
from . import eos_traction       # EosMeeting, EosMeetingAttendee, EosTodo
