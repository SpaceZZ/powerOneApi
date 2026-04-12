import datetime
import logging

logger = logging.getLogger(__name__)

# Human-readable Polish labels for API measurement keys
_LABELS = {
    "now": "Aktualna moc",
    "today": "Produkcja dziś",
    "start-of-1-days-ago": "Wczoraj",
    "start-of-2-days-ago": "Przedwczoraj",
    "week": "Ten tydzień",
    "month": "Ten miesiąc",
    "lifetime": "Łącznie (od początku)",
}


def render(data, max_time=None, max_power=None, image_link=""):
    """
    Renders a styled HTML email report for daily PV production.
    :return: HTML string
    :rtype: str
    """
    today_val = data.get("today", {}).get("value", "—")
    today_unit = data.get("today", {}).get("unit", "kWh")
    yesterday_val = data.get("start-of-1-days-ago", {}).get("value", "—")
    yesterday_unit = data.get("start-of-1-days-ago", {}).get("unit", "kWh")
    lifetime_val = data.get("lifetime", {}).get("value", "—")
    lifetime_unit = data.get("lifetime", {}).get("unit", "kWh")

    # Day-over-day comparison badge
    comparison_html = ""
    try:
        t = float(today_val)
        y = float(yesterday_val)
        if y > 0:
            pct = (t - y) / y * 100
            sign = "+" if pct >= 0 else ""
            color = "#27ae60" if pct >= 0 else "#e74c3c"
            comparison_html = (
                f'<span style="font-size:13px;color:{color};font-weight:bold;">'
                f"{sign}{pct:.1f}% vs wczoraj</span>"
            )
    except (TypeError, ValueError, ZeroDivisionError):
        pass

    # Format peak time as HH:MM (strip date prefix if present)
    peak_time_display = max_time.split(" ")[-1][:5] if max_time else "—"
    peak_power_display = f"{max_power:.0f}" if max_power else "—"
    has_peak = bool(max_time and max_power)

    peak_html = ""
    if has_peak:
        peak_html = (
            f'<p style="margin:0;font-size:14px;color:#555;">'
            f'Szczyt: <strong>{peak_time_display}</strong> &mdash; '
            f'<strong style="color:#e67e22;">{peak_power_display} W</strong></p>'
        )

    chart_html = ""
    if image_link:
        chart_html = (
            f'<div style="margin-top:20px;">'
            f'<p style="margin:0 0 8px;font-size:13px;color:#888;text-transform:uppercase;letter-spacing:1px;">Krzywa produkcji</p>'
            f'<img src="{image_link}" style="width:100%;max-width:990px;border-radius:6px;" alt="Wykres produkcji PV"/>'
            f'</div>'
        )

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html = f"""<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
</head>
<body style="margin:0;padding:0;background:#f0f4f8;font-family:Arial,Helvetica,sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f4f8;padding:24px 0;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:10px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08);">

  <!-- HEADER -->
  <tr>
    <td style="background:linear-gradient(135deg,#1a1a2e 0%,#16213e 100%);padding:28px 32px;">
      <p style="margin:0;font-size:22px;color:#f39c12;font-weight:bold;">&#9728; Kapalkowo &mdash; PV</p>
      <p style="margin:6px 0 0;font-size:14px;color:#aab4be;">Raport dzienny &mdash; {datetime.datetime.now().strftime("%d.%m.%Y")}</p>
    </td>
  </tr>

  <!-- SUMMARY CARDS -->
  <tr>
    <td style="padding:24px 32px 0;">
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <!-- Today -->
          <td width="33%" style="padding-right:8px;">
            <table width="100%" cellpadding="16" cellspacing="0" style="background:#fffbf2;border:1px solid #fdebd0;border-radius:8px;">
              <tr><td>
                <p style="margin:0;font-size:11px;color:#888;text-transform:uppercase;letter-spacing:1px;">Produkcja dziś</p>
                <p style="margin:6px 0 0;font-size:28px;font-weight:bold;color:#e67e22;">{today_val} <span style="font-size:14px;color:#aaa;">{today_unit}</span></p>
                <p style="margin:6px 0 0;">{comparison_html}</p>
              </td></tr>
            </table>
          </td>
          <!-- Peak -->
          <td width="33%" style="padding:0 4px;">
            <table width="100%" cellpadding="16" cellspacing="0" style="background:#f2f9ff;border:1px solid #d6eaf8;border-radius:8px;">
              <tr><td>
                <p style="margin:0;font-size:11px;color:#888;text-transform:uppercase;letter-spacing:1px;">Szczyt mocy</p>
                <p style="margin:6px 0 0;font-size:28px;font-weight:bold;color:#2980b9;">{peak_power_display} <span style="font-size:14px;color:#aaa;">W</span></p>
                <p style="margin:6px 0 0;font-size:13px;color:#555;">o {peak_time_display}</p>
              </td></tr>
            </table>
          </td>
          <!-- Lifetime -->
          <td width="33%" style="padding-left:8px;">
            <table width="100%" cellpadding="16" cellspacing="0" style="background:#f2fff5;border:1px solid #d5f5e3;border-radius:8px;">
              <tr><td>
                <p style="margin:0;font-size:11px;color:#888;text-transform:uppercase;letter-spacing:1px;">Łącznie</p>
                <p style="margin:6px 0 0;font-size:28px;font-weight:bold;color:#27ae60;">{lifetime_val} <span style="font-size:14px;color:#aaa;">{lifetime_unit}</span></p>
                <p style="margin:6px 0 0;font-size:12px;color:#aaa;">od początku instalacji</p>
              </td></tr>
            </table>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- CHART -->
  <tr>
    <td style="padding:20px 32px 0;">
      {chart_html}
    </td>
  </tr>

  <!-- DETAIL TABLE -->
  <tr>
    <td style="padding:24px 32px 0;">
      <p style="margin:0 0 10px;font-size:13px;color:#888;text-transform:uppercase;letter-spacing:1px;">Szczegóły</p>
      <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;font-size:14px;">
        <tr style="background:#f8f9fa;">
          <th style="text-align:left;padding:10px 12px;color:#555;border-bottom:2px solid #dee2e6;font-weight:600;">Okres</th>
          <th style="text-align:right;padding:10px 12px;color:#555;border-bottom:2px solid #dee2e6;font-weight:600;">Wartość</th>
          <th style="text-align:left;padding:10px 12px;color:#555;border-bottom:2px solid #dee2e6;font-weight:600;">Jednostka</th>
        </tr>
        {_render_rows(data)}
      </table>
    </td>
  </tr>

  <!-- FOOTER -->
  <tr>
    <td style="padding:24px 32px 28px;border-top:1px solid #eee;margin-top:20px;">
      <p style="margin:20px 0 0;font-size:12px;color:#aaa;">Dane pobrane: {now_str}</p>
    </td>
  </tr>

</table>
</td></tr>
</table>

</body>
</html>"""
    return html


def _render_rows(data):
    """Renders table rows for each measurement with human-readable labels."""
    rows = ""
    for i, (key, value) in enumerate(data.items()):
        label = _LABELS.get(key, key)
        display_value = str(value["value"]) if value["value"] is not None else "—"
        display_unit = value.get("unit", "")
        bg = "background:#ffffff;" if i % 2 == 0 else "background:#f8f9fa;"
        rows += (
            f'<tr style="{bg}">'
            f'<td style="padding:10px 12px;color:#333;border-bottom:1px solid #eee;">{label}</td>'
            f'<td style="padding:10px 12px;color:#222;font-weight:600;text-align:right;border-bottom:1px solid #eee;">{display_value}</td>'
            f'<td style="padding:10px 12px;color:#888;border-bottom:1px solid #eee;">{display_unit}</td>'
            f'</tr>'
        )
    return rows
