"""
HTML Rapor Üretici

Tek e-posta veya toplu analiz sonuçlarından insan okunabilir HTML rapor üretir.

Kullanım:
    from src.report_generator import generate_single_report, generate_batch_report

    html = generate_single_report(result_dict)
    generate_batch_report(results_list, "rapor.html")
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

_STYLE = """
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Segoe UI', Arial, sans-serif; background: #0f0f1a; color: #cdd6f4; padding: 24px; }
  h1 { font-size: 22px; color: #89b4fa; margin-bottom: 4px; }
  h2 { font-size: 16px; color: #89b4fa; margin: 20px 0 8px; border-bottom: 1px solid #313244; padding-bottom: 4px; }
  h3 { font-size: 14px; color: #a6adc8; margin: 14px 0 6px; }
  .header { display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; }
  .subtitle { font-size:12px; color:#6c7086; }
  .badge { display:inline-block; border-radius:20px; padding:4px 14px; font-size:13px; font-weight:700; }
  .badge-phishing { background:#3b1219; color:#f38ba8; border:1px solid #f38ba8; }
  .badge-safe     { background:#0d2b1e; color:#a6e3a1; border:1px solid #a6e3a1; }
  .badge-type     { background:#1e1e2e; color:#cba6f7; border:1px solid #cba6f7; margin-left:8px; }
  .verdict-box { border-radius:10px; padding:16px 20px; margin:12px 0; font-size:20px; font-weight:700; text-align:center; letter-spacing:1px; }
  .verdict-phishing { background:linear-gradient(135deg,#3b1219,#1e1e2e); border:2px solid #f38ba8; color:#f38ba8; }
  .verdict-safe     { background:linear-gradient(135deg,#0d2b1e,#1e1e2e); border:2px solid #a6e3a1; color:#a6e3a1; }
  .metric-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(160px,1fr)); gap:10px; margin:10px 0; }
  .metric-card { background:#1e1e2e; border:1px solid #313244; border-radius:8px; padding:12px 16px; }
  .metric-label { font-size:10px; color:#6c7086; text-transform:uppercase; letter-spacing:1px; }
  .metric-value { font-size:20px; font-weight:700; margin-top:4px; color:#cdd6f4; }
  .bar-row { display:flex; align-items:center; gap:8px; margin:4px 0; font-size:12px; font-family:monospace; }
  .bar-label { width:140px; color:#a6adc8; }
  .bar-bg { flex:1; background:#313244; border-radius:4px; height:10px; overflow:hidden; }
  .bar-fill { height:100%; border-radius:4px; background:#f38ba8; }
  .bar-val { width:60px; text-align:right; color:#6c7086; }
  .flag { background:#2a1f10; border-left:3px solid #f9e2af; border-radius:4px; padding:6px 12px; margin:4px 0; font-size:12px; color:#f9e2af; }
  .action { background:#1e1e2e; border-left:3px solid #89b4fa; border-radius:4px; padding:8px 12px; margin:4px 0; font-size:13px; color:#cdd6f4; }
  .action.phishing { border-left-color:#f38ba8; }
  .url-row { background:#1e1e2e; border-left:3px solid #313244; border-radius:4px; padding:6px 12px; margin:4px 0; font-size:12px; }
  .url-row.suspicious { border-left-color:#f38ba8; }
  .url-text { color:#89b4fa; font-family:monospace; word-break:break-all; }
  .url-flags { color:#6c7086; margin-top:2px; }
  .kw-tag { display:inline-block; background:#3b1219; color:#f38ba8; border:1px solid #f38ba844; border-radius:12px; padding:2px 10px; font-size:11px; font-family:monospace; margin:2px; }
  table { width:100%; border-collapse:collapse; font-size:13px; margin:12px 0; }
  th { background:#1e1e2e; color:#89b4fa; padding:8px 12px; text-align:left; border-bottom:1px solid #313244; }
  td { padding:7px 12px; border-bottom:1px solid #1e1e2e; }
  tr.phishing-row { background:#2a1219; }
  tr.safe-row { background:#0e2018; }
  .summary-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin:12px 0; }
  .summary-card { background:#1e1e2e; border:1px solid #313244; border-radius:8px; padding:14px; text-align:center; }
  .summary-val { font-size:28px; font-weight:700; }
  .summary-lbl { font-size:11px; color:#6c7086; text-transform:uppercase; letter-spacing:1px; margin-top:4px; }
  footer { margin-top:30px; font-size:11px; color:#6c7086; text-align:center; border-top:1px solid #313244; padding-top:12px; }
</style>
"""


def _score_bar(label: str, value: float, max_val: float = 100.0) -> str:
    pct = min(100, value / max_val * 100) if max_val else 0
    return (
        f'<div class="bar-row">'
        f'<span class="bar-label">{label}</span>'
        f'<div class="bar-bg"><div class="bar-fill" style="width:{pct:.0f}%"></div></div>'
        f'<span class="bar-val">{value:.1f}</span>'
        f'</div>'
    )


def generate_single_report(result: dict, email_preview: str = "") -> str:
    """Tek e-posta analiz sonucundan HTML string üretir."""
    label = result.get("label", "NO")
    risk  = result.get("risk_score", 0)
    conf  = result.get("confidence", 0)
    prob  = result.get("phishing_probability", 0)
    kw_sc = result.get("keyword_score", 0)
    ptype = result.get("phishing_type", "")
    kws   = result.get("matched_keywords", [])
    urls  = result.get("url_analysis", {})
    anom  = result.get("anomaly", {})
    hdr   = result.get("header_analysis", {})
    acts  = result.get("actions", [])
    bd    = result.get("score_breakdown", {})
    sigs  = bd.get("signals", {})

    is_phishing  = label == "YES"
    verdict_cls  = "verdict-phishing" if is_phishing else "verdict-safe"
    verdict_text = "🚨 PHİSHİNG" if is_phishing else "✅ GÜVENLİ"
    badge_cls    = "badge-phishing" if is_phishing else "badge-safe"

    preview_html = ""
    if email_preview:
        safe_preview = email_preview[:300].replace("<", "&lt;").replace(">", "&gt;")
        preview_html = f'<h2>E-posta Önizleme</h2><p style="font-size:13px;color:#a6adc8;background:#1e1e2e;padding:10px;border-radius:6px;">{safe_preview}...</p>'

    # sinyal çubukları
    signal_bars = ""
    for key, lbl in [("model","Model"), ("keyword","Keyword"), ("url","URL"), ("header","Header"), ("anomaly","Anomali")]:
        sig = sigs.get(key, {})
        if sig.get("available", True):
            signal_bars += _score_bar(f"{lbl} ({sig.get('weight_pct',0):.0f}%)", sig.get("contribution", 0), 100)

    # keyword tags
    kw_html = "".join(f'<span class="kw-tag">{k}</span>' for k in kws) or '<span style="color:#6c7086;font-size:12px;">Bulunamadı</span>'

    # URL listesi
    url_rows = ""
    for u in urls.get("urls", []):
        cls = "url-row suspicious" if u.get("is_suspicious") else "url-row"
        flags = " · ".join(u.get("flags", []))
        url_rows += f'<div class="{cls}"><div class="url-text">{u["url"]}</div><div class="url-flags">{flags}</div></div>'
    if not url_rows:
        url_rows = '<span style="color:#6c7086;font-size:12px;">URL bulunamadı</span>'

    # header flags
    hdr_flags = "".join(f'<div class="flag">⚠️ {f}</div>' for f in hdr.get("flags", []))
    if not hdr_flags:
        hdr_flags = '<span style="color:#6c7086;font-size:12px;">Başlık bilgisi girilmedi</span>'

    # aksiyon önerileri
    action_cls = "action phishing" if is_phishing else "action"
    action_html = "".join(f'<div class="{action_cls}">{"🚨" if is_phishing else "✅"} {a}</div>' for a in acts)

    type_badge = f'<span class="badge badge-type">{ptype}</span>' if ptype else ""

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html = f"""<!DOCTYPE html>
<html lang="tr">
<head><meta charset="UTF-8"><title>Phishing Analiz Raporu</title>{_STYLE}</head>
<body>
  <div class="header">
    <div>
      <h1>🛡️ Phishing E-posta Analiz Raporu</h1>
      <span class="subtitle">Oluşturulma: {now}</span>
    </div>
    <div>
      <span class="badge {badge_cls}">{label}</span>{type_badge}
    </div>
  </div>

  <div class="verdict-box {verdict_cls}">{verdict_text}</div>

  {preview_html}

  <h2>Metrik Özeti</h2>
  <div class="metric-grid">
    <div class="metric-card"><div class="metric-label">Risk Skoru</div><div class="metric-value" style="color:{'#f38ba8' if is_phishing else '#a6e3a1'}">{risk:.1f}/100</div></div>
    <div class="metric-card"><div class="metric-label">Güven Skoru</div><div class="metric-value">%{conf:.1f}</div></div>
    <div class="metric-card"><div class="metric-label">Model Olasılığı</div><div class="metric-value">%{prob:.1f}</div></div>
    <div class="metric-card"><div class="metric-label">Keyword Skoru</div><div class="metric-value">%{kw_sc:.1f}</div></div>
    <div class="metric-card"><div class="metric-label">Anomali Skoru</div><div class="metric-value">{anom.get('score',0):.0f}/100</div></div>
    <div class="metric-card"><div class="metric-label">Başlık Skoru</div><div class="metric-value">{hdr.get('score',0)}/100</div></div>
  </div>

  <h2>5 Katmanlı Sinyal Dağılımı</h2>
  {signal_bars}

  <h2>Şüpheli Anahtar Kelimeler</h2>
  {kw_html}

  <h2>URL Analizi</h2>
  {url_rows}

  <h2>Başlık Uyarıları</h2>
  {hdr_flags}

  <h2>Önerilen Aksiyonlar</h2>
  {action_html}

  <footer>Phishing E-posta Tespit Sistemi &nbsp;·&nbsp; {now}</footer>
</body>
</html>"""
    return html


def generate_batch_report(results: list[dict], output_path: str, email_previews: list[str] | None = None) -> None:
    """Toplu analiz sonuçlarından HTML rapor dosyası üretir."""
    previews = email_previews or [""] * len(results)
    phishing_count = sum(1 for r in results if r.get("label") == "YES")
    safe_count     = len(results) - phishing_count
    critical_count = sum(1 for r in results if r.get("risk_score", 0) >= 80)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    rows_html = ""
    for i, (r, preview) in enumerate(zip(results, previews), 1):
        is_p = r.get("label") == "YES"
        row_cls = "phishing-row" if is_p else "safe-row"
        badge = f'<span class="badge {"badge-phishing" if is_p else "badge-safe"}" style="font-size:11px;padding:2px 8px;">{"PHISHİNG" if is_p else "GÜVENLİ"}</span>'
        safe_prev = (preview[:60] + "...").replace("<","&lt;").replace(">","&gt;") if preview else "—"
        rows_html += f"""<tr class="{row_cls}">
          <td>{i}</td>
          <td>{safe_prev}</td>
          <td>{badge}</td>
          <td style="color:{'#f38ba8' if is_p else '#a6e3a1'}">{r.get('risk_score',0):.1f}</td>
          <td>{r.get('phishing_type','')}</td>
          <td>{r.get('url_analysis',{}).get('suspicious_count',0)} / {r.get('url_analysis',{}).get('total_count',0)}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="tr">
<head><meta charset="UTF-8"><title>Toplu Phishing Analiz Raporu</title>{_STYLE}</head>
<body>
  <div class="header">
    <div>
      <h1>🛡️ Toplu Phishing E-posta Analiz Raporu</h1>
      <span class="subtitle">Oluşturulma: {now}</span>
    </div>
  </div>

  <h2>Özet</h2>
  <div class="summary-grid">
    <div class="summary-card"><div class="summary-val" style="color:#cdd6f4">{len(results)}</div><div class="summary-lbl">Toplam E-posta</div></div>
    <div class="summary-card"><div class="summary-val" style="color:#f38ba8">{phishing_count}</div><div class="summary-lbl">Phishing</div></div>
    <div class="summary-card"><div class="summary-val" style="color:#a6e3a1">{safe_count}</div><div class="summary-lbl">Güvenli</div></div>
  </div>
  <div class="metric-grid" style="margin-top:0">
    <div class="metric-card"><div class="metric-label">Kritik (≥80)</div><div class="metric-value" style="color:#f38ba8">{critical_count}</div></div>
    <div class="metric-card"><div class="metric-label">Phishing Oranı</div><div class="metric-value">%{phishing_count/len(results)*100:.1f}</div></div>
  </div>

  <h2>Sonuç Tablosu (Risk Skoruna Göre)</h2>
  <table>
    <thead><tr><th>#</th><th>Önizleme</th><th>Karar</th><th>Risk Skoru</th><th>Tür</th><th>Şüpheli URL</th></tr></thead>
    <tbody>{rows_html}</tbody>
  </table>

  <footer>Phishing E-posta Tespit Sistemi &nbsp;·&nbsp; {now}</footer>
</body>
</html>"""

    Path(output_path).write_text(html, encoding="utf-8")
    print(f"✅ HTML rapor kaydedildi: {output_path}")
