# CLI Package Separation Plan

## Current State

The Highflame CLI is currently bundled with the SDK:
- SDK package: `highflame` (contains client, services, models)
- CLI code: `highflame_cli/` (in same repo)
- Single PyPI package: `highflame` (includes both)

## Problem

Users who only need the SDK don't need:
- `argparse` and CLI dependencies
- CLI command implementations
- Authentication management
- Cache management

This adds ~200KB+ of unnecessary dependencies for SDK-only users.

---

## Proposed Solution

**Separate into two packages:**

### 1. Core SDK Package
**Package Name:** `highflame`
**Contents:**
- `highflame/` - SDK code
- Dependencies: `httpx`, `pydantic`, `opentelemetry-*`, `jmespath`, `jsonpath-ng`
- Size: Minimal, focused on SDK functionality

**Installation:**
```bash
pip install highflame
```

**Usage:**
```python
from highflame import Highflame, Config

config = Config(api_key="...")
client = Highflame(config)
response = client.query_route(...)
```

---

### 2. CLI Package
**Package Name:** `highflame-cli`
**Contents:**
- `highflame_cli/` - CLI code
- Depends on: `highflame` (SDK package)
- Additional dependencies: argparse, authentication, caching

**Installation:**
```bash
pip install highflame-cli
```

**Usage:**
```bash
highflame auth
highflame routes list
highflame routes create --name my_route --file route.json
```

---

## Implementation Steps

### Phase 1: Setup (Current State - v2/)
✅ Already done:
- SDK code in `highflame/`
- CLI code in `highflame_cli/`
- Both in same repo under `v2/`

### Phase 2: Create CLI Package Structure
Create separate `pyproject.toml` for CLI:

```toml
[project]
name = "highflame-cli"
version = "2.0.0"
dependencies = [
    "highflame>=2.0.0",
    "requests>=2.32.3",
]

[project.scripts]
highflame = "highflame_cli.cli:main"
```

### Phase 3: Package Separation in Repository
**Option A: Separate Directories (Recommended)**
```
v2/
├── sdk/                    # SDK code (will become highflame package)
│   ├── highflame/
│   ├── pyproject.toml     # SDK package config
│   └── README.md
│
├── cli/                    # CLI code (will become highflame-cli package)
│   ├── highflame_cli/
│   ├── pyproject.toml     # CLI package config
│   ├── README.md
│   └── setup.py
│
└── SHARED_DOCS/
    ├── MIGRATION_GUIDE.md
    ├── LOGGING.md
    └── CLI_SEPARATION_PLAN.md
```

**Option B: Keep in Single Directory (Short-term)**
```
v2/
├── highflame/             # SDK
├── highflame_cli/         # CLI
├── pyproject.toml         # SDK package (main)
└── cli-pyproject.toml     # CLI package (for reference)
```

### Phase 4: Update Dependencies
**SDK `pyproject.toml`:**
```toml
[project]
name = "highflame"
version = "2.0.0"
dependencies = [
    "httpx>=0.27.2",
    "pydantic>=2.9.2",
    "opentelemetry-api>=1.32.1",
    "opentelemetry-sdk>=1.32.1",
    ...
]
```

**CLI `pyproject.toml`:**
```toml
[project]
name = "highflame-cli"
version = "2.0.0"
dependencies = [
    "highflame>=2.0.0",
    "requests>=2.32.3",
]

[project.scripts]
highflame = "highflame_cli.cli:main"
```

### Phase 5: Update Imports
CLI package imports from SDK:
```python
# In highflame_cli/_internal/commands.py
from highflame import Highflame, Config  # Import from SDK
```

### Phase 6: Distribution

**On PyPI:**
```
PyPI Package: highflame
├── Available for: SDK only users
├── Size: ~1-2MB
└── Dependencies: httpx, pydantic, opentelemetry

PyPI Package: highflame-cli
├── Available for: Users who want CLI
├── Size: ~500KB
└── Dependencies: highflame SDK
```

---

## Migration Path for Users

### Current (v1) Users:
```bash
# v1 - Everything in one package
pip install javelin-sdk
from javelin_sdk import JavelinClient
```

### v2 Users - SDK Only:
```bash
# Just the SDK
pip install highflame
from highflame import Highflame, Config
```

### v2 Users - SDK + CLI:
```bash
# SDK + CLI
pip install highflame highflame-cli
# Or (with extras)
pip install highflame[cli]

# Then use both
from highflame import Highflame, Config  # In Python
$ highflame auth                         # In terminal
```

---

## Benefits

| Aspect | Current | After Separation |
|--------|---------|------------------|
| **SDK Size** | ~2.5MB | ~1-2MB ↓ |
| **SDK Dependencies** | 15+ | 8 ↓ |
| **CLI Size** | N/A | ~500KB |
| **User Choice** | Must install both | Choose what you need |
| **Maintenance** | Coupled | Separated |
| **Testing** | Combined | Independent |

---

## Timeline

- **Phase 1-2:** 1-2 hours - Create separate package configs
- **Phase 3:** 30 mins - Reorganize directory structure
- **Phase 4-5:** 30 mins - Update pyproject.toml files and imports
- **Phase 6:** 1 hour - Test both packages independently
- **Documentation:** 1 hour - Update migration guides

**Total:** ~4-5 hours

---

## Rollout Strategy

### Step 1: Test Separation (Internal)
- Publish to test PyPI
- Test installing both packages separately
- Verify SDK works without CLI
- Verify CLI works with SDK dependency

### Step 2: Release to PyPI
- Release `highflame` 2.0.0 (SDK)
- Release `highflame-cli` 2.0.0 (CLI)
- Publish migration guides

### Step 3: User Communication
- Update README with installation options
- Document benefits of separation
- Provide upgrade instructions

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| **Users expect single package** | Document both are available separately & together |
| **CLI depends on SDK updates** | Pin SDK version, use semantic versioning |
| **Breaking changes in SDK** | CLI version also bumped; dependency updated |
| **Installation confusion** | Clear docs: "For SDK only, install `highflame`" |

---

## Future Considerations

1. **Separate repositories** (if teams grow)
   - `highflame-python-sdk` repo
   - `highflame-python-cli` repo

2. **More plugins/tools** could become separate packages:
   - `highflame-monitoring` (observability)
   - `highflame-testing` (testing utilities)
   - `highflame-integrations` (framework integrations)

3. **SDK evolution** stays independent of CLI features

---

## Recommendation

**Implement Phase 1-6** to separate packages:
- Start with current v2/ structure
- Create separate `pyproject.toml` for CLI
- Publish both to PyPI
- Update documentation

This provides:
- ✅ Smaller SDK for users who don't need CLI
- ✅ Independent versioning
- ✅ Cleaner dependency graph
- ✅ Better separation of concerns
- ✅ Flexibility for future growth
