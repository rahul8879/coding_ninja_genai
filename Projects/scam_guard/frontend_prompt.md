You are an expert frontend developer.

Build a single-file interactive dashboard (HTML + CSS + JS only — no frameworks, no CDN libraries) that calls a local FastAPI batch endpoint and displays the results.

## API Details

Base URL: http://localhost:8000
Endpoint: POST /batch/
Content-Type: multipart/form-data

Form fields:
- file (optional): CSV file upload with columns message_text and label
- prompt_version (optional): one of v1_zero_shot, v2_few_shot, v3_cot
- sample_size (optional): integer, number of rows to process

Response JSON shape:
{
  "summary": {
    "total_processed": int,
    "correct_predictions": int,
    "accuracy": float (0.0 to 1.0),
    "scam_detected": int,
    "not_scam_detected": int,
    "uncertain_detected": int,
    "prompt_version_used": str
  },
  "results": [
    {
      "message": str,
      "actual_label": str,
      "predicted_label": str,
      "is_correct": bool,
      "intent_type": str,
      "confidence_score": float,
      "reasoning": str,
      "prompt_version_used": str
    }
  ]
}

## UI Requirements

Control Panel:
- Prompt version dropdown (v1_zero_shot, v2_few_shot, v3_cot, default)
- Sample size input (number)
- Optional CSV file upload
- Run Analysis button

After API responds, display:

Stats Cards:
- Total processed
- Accuracy %
- Scams detected
- Not Scam + Uncertain count

Charts:
- Label distribution (Scam / Not Scam / Uncertain) — donut or bar
- Intent type breakdown — horizontal bar chart

Results Table:
- message, actual_label, predicted_label, is_correct, intent_type, confidence_score, reasoning

Extra:
- API connection status indicator (poll GET /versions every 15s)
- Progress indicator during API call
- Error message if API call fails (no word "unreachable")
- Save output file name as home.html

## Design
- Light theme
- Clean, professional, minimal
- Use a good Google Font (not Inter or Roboto)
- CSS variables for colors
- Smooth animations on stats and charts after data loads