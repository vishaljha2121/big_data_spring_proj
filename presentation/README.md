# Presentation Index

Use `CourtIQ_Final_Presentation_v2.pptx` for the final presentation. The older `CourtIQ_Final_Presentation.pptx` is preserved as a historical first version.

## Recommended Final Files

| File | Use |
| --- | --- |
| `CourtIQ_Final_Presentation_v2.pptx` | Recommended final 18-slide deck |
| `speaker_notes_v2.md` | Recommended slide-by-slide speaker script |
| `assets_v2/diagrams/` | Final architecture, data lake, feature, streaming, model, and API/frontend diagrams |
| `assets_v2/screenshots/` | Final dashboard/API screenshots and capture checklist |

## Historical Files

| File | Status |
| --- | --- |
| `CourtIQ_Final_Presentation.pptx` | Historical first deck |
| `speaker_notes.md` | Historical first speaker script |
| `assets/` | Historical first-version diagrams and screenshot checklist |
| `README_v2.md` | Older short index kept for traceability |

## Screenshots

Included screenshots under `assets_v2/screenshots/`:

- `dashboard_overview.png`
- `fastapi_docs.png`
- `match_browser.png`
- `model_performance.png`
- `pipeline_monitor.png`
- `point_timeline.png`
- `prediction_center.png`
- `replay_center.png`
- `validation.png`
- `capture_results.json`
- `screenshot_checklist_v2.md`

The screenshot set covers the recommended demo path. If new screenshots are needed, start the local demo and rerun the capture scripts from the repo root.

## Regenerate

```bash
.venv/bin/python presentation/build_presentation_v2.py
```

The builder reads validation reports under `data/results/`, generated diagrams under `presentation/assets_v2/`, and writes `presentation/CourtIQ_Final_Presentation_v2.pptx`.

## Optional Screenshot Capture

Start the product:

```bash
bash scripts/run_full_demo.sh
```

Then use the capture helper that matches your local browser setup:

```bash
node presentation/capture_spa.js
```

If browser automation is unavailable, use `assets_v2/screenshots/screenshot_checklist_v2.md` as the manual capture list.

## What To Present

Present `CourtIQ_Final_Presentation_v2.pptx` with `speaker_notes_v2.md`. The strongest live evidence path is:

1. `bash scripts/run_full_demo.sh`
2. Dashboard
3. Match Browser
4. Replay Center
5. Point Timeline
6. Prediction Center
7. Model Performance
8. Validation
9. Pipeline Monitor
10. FastAPI `/docs`

State the limitations clearly: point probabilities are not betting odds, risk scores are not misconduct proof, official rankings/surface analytics are not claimed, and the local demo is not production deployment.
