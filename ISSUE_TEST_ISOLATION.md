# Issue: Test Isolation Problem - Global State Contamination

## Problem Description

After successful refactoring from monolithic BlenderVSEConfigurator to modular architecture, we reduced test failures from 67 to 10 (85% improvement, 97.5% success rate). However, **10 tests fail only when run in full test suite** but **pass perfectly in isolation**.

## Affected Tests

### Metadata Tests (5 failures)
- `test_determine_source_capabilities_*` - OBS API capability detection
- `test_metadata_*` - Integration with has_audio/has_video flags

### OBS Script Tests (5 failures)  
- `test_on_event_*` - Recording start/stop event handlers
- `test_save_metadata_*` - Metadata file saving
- `test_collect_and_save_metadata_*` - Scene metadata collection

## Root Cause Analysis

### Global State Contamination
1. **`src/core/metadata.py`**: Global `obs = None` set during import
2. **`src/obs_integration/obs_script.py`**: Global variables `script_enabled`, `current_scene_data`, `recording_output_path`
3. **Module imports**: Once imported, modules retain state between tests

### Why Tests Pass in Isolation
- Fresh module imports with default values
- Proper mock isolation
- No cross-test contamination

### Why Tests Fail in Full Suite
- Previous tests modify global state
- Mocks don't reset module-level variables
- Shared state persists across test runs

## Evidence

```bash
# ✅ Individual modules pass 100%
uv run pytest tests/test_metadata.py -v      # 23/23 PASSED
uv run pytest tests/test_obs_script.py -v   # 10/10 PASSED

# ❌ Full suite has 10 failures
uv run pytest --tb=short                    # 395/405 PASSED (97.5%)
```

## Current Workarounds Attempted

1. **Module reloading** (`importlib.reload`) - Failed due to import ordering
2. **Mock improvements** - Partially successful but not complete
3. **Setup/teardown methods** - Limited effectiveness with global state

## Proposed Solutions

### Option 1: Enhanced Test Isolation ⭐ **Recommended**
```python
# Add to conftest.py
@pytest.fixture(autouse=True)
def isolate_obs_modules():
    """Reset OBS-related module state before each test."""
    # Store original state
    original_states = {}
    
    # Reset modules if imported
    if 'src.core.metadata' in sys.modules:
        original_states['metadata_obs'] = sys.modules['src.core.metadata'].obs
    if 'src.obs_integration.obs_script' in sys.modules:
        script_module = sys.modules['src.obs_integration.obs_script']
        original_states['script_state'] = {
            'script_enabled': script_module.script_enabled,
            'current_scene_data': script_module.current_scene_data.copy(),
            'recording_output_path': script_module.recording_output_path
        }
    
    yield
    
    # Restore original state (if needed)
```

### Option 2: Process Isolation with pytest-xdist
```bash
# Run tests in separate processes
uv run pytest --dist=loadscope --tx=popen//python
```

### Option 3: Split Project Architecture 🏗️ **Long-term**

Split into two packages to reduce coupling:

#### Package 1: `obs-canvas-core`
- **Purpose**: Core functionality without OBS dependencies
- **Contents**: 
  - `src/core/` (metadata, file_structure, extractor, audio_analyzer, blender_project)
  - `src/cli/` (command-line tools)
  - VSE animation system
- **Dependencies**: No OBS, standard Python libraries
- **Testing**: Clean, no global state issues

#### Package 2: `obs-canvas-integration`  
- **Purpose**: OBS Studio integration
- **Contents**:
  - `src/obs_integration/` (obs_script, real-time collection)
  - OBS-specific fallbacks and globals
- **Dependencies**: obs-canvas-core + obspython
- **Testing**: Isolated OBS mocking

#### Benefits of Split:
- **Clean separation of concerns**
- **Independent testing** - core tests never affected by OBS state
- **Easier deployment** - users can install only what they need
- **Reduced complexity** - each package has focused responsibility
- **Better CI/CD** - can test core package in any environment

## Impact Assessment

### Current Status: ✅ **ACCEPTABLE**
- **97.5% test success rate**
- **All production code works correctly**
- **Fallbacks function as designed**
- **Only test isolation affected**

### Priority: **Medium** 
- Tests verify correct behavior
- Issue doesn't affect end users
- Mainly affects development workflow

## Implementation Plan

### Phase 1: Quick Fix (1-2 hours)
- Implement enhanced test isolation fixture
- Add module state reset mechanisms
- Document known flaky tests

### Phase 2: Process Isolation (2-4 hours)  
- Configure pytest-xdist properly
- Optimize test execution with parallel processes
- Update CI/CD configuration

### Phase 3: Architecture Split (1-2 weeks)
- Design package boundaries
- Split dependencies in pyproject.toml
- Refactor imports and structure
- Update documentation and deployment

## Acceptance Criteria

- [ ] All 405 tests pass in full suite (100% success rate)
- [ ] No test execution time regression
- [ ] Proper isolation between OBS and core functionality
- [ ] Clear documentation of test isolation strategy
- [ ] Optional: Split architecture for long-term maintainability

## Related Files

- `src/core/metadata.py` - Global obs variable
- `src/obs_integration/obs_script.py` - Global script state
- `tests/test_metadata.py` - Failing capability tests
- `tests/test_obs_script.py` - Failing event handler tests
- `tests/conftest.py` - Test fixtures and mocking

## Notes

This is a **quality-of-life improvement** for development, not a production bug. The code works correctly, fallbacks are properly implemented, and all functionality is verified through isolated tests.

The 85% improvement in test reliability (67→10 failures) represents successful refactoring. These remaining issues are architectural test concerns, not code defects.