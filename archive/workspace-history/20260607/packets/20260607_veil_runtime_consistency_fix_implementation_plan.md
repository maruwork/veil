# VEIL Runtime Consistency Fix Implementation Plan

## 1. Files

### Update

- `app.py`
- `veil-sync.py`
- `veil-lint.py`
- `veil-normalize.py`
- `ui/js/api.js`
- `ui/js/render.js`
- `ui/js/ui.js`
- `docs/veil-design.md`

## 2. Order

1. harden migration
2. fix UI re-render path
3. align lint / normalize
4. surface rule conflicts
5. harden sync target loading
6. verify and reflect docs

## 3. Acceptance Mapping

- migration bug -> `app.py`
- stale UI -> `ui/js/api.js`, `ui/js/render.js`, `ui/js/ui.js`
- helper alignment -> `veil-lint.py`, `veil-normalize.py`
- sync hardening -> `veil-sync.py`
- canonical reflection -> `docs/veil-design.md`

## 4. Verification

- `python -m py_compile app.py veil-sync.py veil-lint.py veil-normalize.py install-startup.py`
- direct Python smoke for migration helper path
- direct Python smoke for lint / normalize conflict and plural behavior
