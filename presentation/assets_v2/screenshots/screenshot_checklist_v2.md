# Screenshot Checklist v2

Automated Selenium capture was able to capture the main Dashboard Overview and FastAPI docs correctly. Because the frontend relies on complex client-side state, inner-page views (like the Replay Center or Model Performance) may need to be captured manually.

Run:

```bash
bash scripts/run_full_demo.sh
```

Capture manually:

1. Match Browser with selected match detail.
2. Replay Center with playback controls.
3. Point Timeline.
4. Model Performance.
5. Validation page.
6. Pipeline Monitor.
7. Reports page.
