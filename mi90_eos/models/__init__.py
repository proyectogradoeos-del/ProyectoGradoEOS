from . import eos_rock
from . import eos_key_result
from . import eos_todo

# Additional models for L10 and scorecard
from . import eos_issue
from . import eos_meeting
from . import eos_kpi

# Note: eos_dashboard.py does not exist in this addon. Importing it
# caused an ImportError at module load time which prevented the
# ORM models from being registered and their tables created. If you
# later add eos_dashboard.py re-add the import here.

# Compatibility patches (executed on registry load)
from . import compat_patches
