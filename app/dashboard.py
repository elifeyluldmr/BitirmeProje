import sys
from pathlib import Path

# Projenin kök dizinini Python yoluna ekliyoruz, src modüllerini bulsun diye
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pickle
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from sklearn.metrics import (
    confusion_matrix, roc_curve, auc,
    accuracy_score, precision_score, recall_score, f1_score,
)
from sklearn.model_selection import train_test_split

from src.predict import predict_details, PHISHING_THRESHOLD
from src.text_utils import advanced_preprocessing, build_email_text

# Tarayıcı sekmesi başlığı ve ikon burada ayarlanıyor
st.set_page_config(
    page_title="Phishing E-posta Tespiti",
    page_icon="🛡️",
    layout="wide",
)

# Koyu tema CSS, JetBrains Mono ve Inter fontlarıyla karanlık arayüz oluşturuyoruz
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@300;400;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.metric-card {
    background: #1e1e2e;
    border: 1px solid #313244;
    border-radius: 10px;
    padding: 14px 20px;
    margin: 6px 0;
    font-family: 'JetBrains Mono', monospace;
}
.metric-label { font-size: 11px; color: #6c7086; text-transform: uppercase; letter-spacing: 1px; }
.metric-value { font-size: 22px; font-weight: 700; margin-top: 2px; }
.phishing-yes { color: #f38ba8; }
.phishing-no  { color: #a6e3a1; }
.neutral      { color: #cdd6f4; }

.verdict-banner {
    border-radius: 12px;
    padding: 20px 28px;
    margin: 16px 0;
    font-family: 'JetBrains Mono', monospace;
    font-size: 28px;
    font-weight: 700;
    text-align: center;
    letter-spacing: 2px;
}
.verdict-phishing {
    background: linear-gradient(135deg, #3b1219, #1e1e2e);
    border: 2px solid #f38ba8;
    color: #f38ba8;
}
.verdict-safe {
    background: linear-gradient(135deg, #0d2b1e, #1e1e2e);
    border: 2px solid #a6e3a1;
    color: #a6e3a1;
}
.low-confidence-warning {
    background: #2a2a1a;
    border-left: 4px solid #f9e2af;
    border-radius: 6px;
    padding: 12px 16px;
    color: #f9e2af;
    font-size: 13px;
    margin: 8px 0;
}
.keyword-tag {
    display: inline-block;
    background: #3b1219;
    color: #f38ba8;
    border: 1px solid #f38ba844;
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 12px;
    font-family: 'JetBrains Mono', monospace;
    margin: 3px;
}
.perf-card {
    background: #1e1e2e;
    border: 1px solid #313244;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    font-family: 'JetBrains Mono', monospace;
}
.perf-value { font-size: 32px; font-weight: 700; color: #89b4fa; }
.perf-label { font-size: 12px; color: #6c7086; margin-top: 4px; text-transform: uppercase; letter-spacing: 1px; }
</style>
""", unsafe_allow_html=True)


# ── Yardımcı render fonksiyonları ────────────────────────────────────────────

def _render_explanation_chart(
    words: list[tuple[str, float]],
    x_title: str,
    color_pos: str,
    color_neg: str,
    subtitle: str,
) -> None:
    # SHAP, LIME ve Transformer LIME için aynı grafik şablonunu kullanıyoruz
    if not words:
        return
    # Küçük değerler altta, büyükler üstte görünsün
    sorted_words = sorted(words, key=lambda x: x[1])
    labels = [w for w, _ in sorted_words]
    scores = [s for _, s in sorted_words]
    # Pozitif değer phishing yönünde, negatif değer normal yönünde etkili
    colors = [color_pos if s > 0 else color_neg for s in scores]
    fig = go.Figure(go.Bar(
        x=scores, y=labels, orientation="h",
        marker_color=colors,
        hovertemplate="%{y}: %{x:.4f}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="#1e1e2e", plot_bgcolor="#1e1e2e",
        font=dict(color="#cdd6f4", family="JetBrains Mono"),
        xaxis=dict(title=x_title, gridcolor="#313244", color="#6c7086", zeroline=True, zerolinecolor="#6c7086"),
        yaxis=dict(gridcolor="#313244", color="#cdd6f4"),
        margin=dict(l=10, r=10, t=10, b=10),
        height=340,
    )
    st.plotly_chart(fig, use_container_width=True)
    # Grafiğin altına kısa açıklama yazıyoruz
    st.markdown(
        f"<div style='font-size:12px; color:#6c7086; font-family:JetBrains Mono;'>{subtitle}</div>",
        unsafe_allow_html=True,
    )


def _render_signal_breakdown(bd: dict) -> None:
    # 5 katmanlı sinyal bar grafiği ve transformer durum satırı
    sigs = bd.get("signals", {})
    if not sigs:
        return
    st.markdown("<div style='margin-top:20px;'>", unsafe_allow_html=True)
    st.markdown("### 🎛️ Sinyal Dağılımı — 5 Katmanlı Risk Skoru")

    # Transformer aktifse oranları gösteriyoruz, değilse uyarı veriyoruz
    if bd.get("transformer_used"):
        tr_prob = bd.get("transformer_probability", 0)
        lr_prob = bd.get("lr_probability", 0)
        st.markdown(
            f"<div style='background:#1a1a2e; border-left:3px solid #89b4fa; border-radius:6px; "
            f"padding:8px 14px; margin-bottom:8px; font-family:JetBrains Mono; font-size:12px; color:#89b4fa;'>"
            f"🤖 <strong>Transformer aktif</strong> — DistilBERT: %{tr_prob:.1f} &nbsp;·&nbsp; "
            f"TF-IDF LR: %{lr_prob:.1f} &nbsp;·&nbsp; Blend: %60 / %40</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<div style='background:#1e1e2e; border-left:3px solid #6c7086; border-radius:6px; "
            "padding:8px 14px; margin-bottom:8px; font-family:JetBrains Mono; font-size:12px; color:#6c7086;'>"
            "⚠️ Transformer modeli eğitilmemiş — yalnızca TF-IDF LR kullanılıyor. "
            "<code>python src/train_transformer.py</code></div>",
            unsafe_allow_html=True,
        )

    # Her sinyale emoji ve Türkçe etiket ekliyoruz
    sig_labels = {
        "model":   "🤖 Model",
        "keyword": "🔑 Keyword",
        "url":     "🔗 URL",
        "header":  "📧 Header",
        "anomaly": "🧬 Anomali",
    }
    bar_names, bar_values, bar_colors, bar_texts = [], [], [], []
    for key in ["model", "keyword", "url", "header", "anomaly"]:
        sig     = sigs.get(key, {})
        avail   = sig.get("available", True)
        contrib = sig.get("contribution", 0.0)
        score   = sig.get("score", 0.0)
        w_pct   = sig.get("weight_pct", 0.0)
        # Mevcut olmayan sinyaller gri, katkısı olanlar kırmızı gösteriliyor
        bar_names.append(
            f"{sig_labels[key]} (mevcut değil)" if not avail else f"{sig_labels[key]}  (%{w_pct:.0f})"
        )
        bar_values.append(round(contrib, 1))
        bar_colors.append("#313244" if not avail or contrib == 0 else "#f38ba8")
        bar_texts.append(f"{score:.0f}/100 → +{contrib:.1f} pt")

    fig = go.Figure(go.Bar(
        x=bar_values, y=bar_names, orientation="h",
        marker_color=bar_colors, text=bar_texts, textposition="outside",
        textfont={"size": 11, "color": "#6c7086", "family": "JetBrains Mono"},
        hovertemplate="%{y}: %{x:.1f} puan<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="#1e1e2e", plot_bgcolor="#1e1e2e",
        font=dict(color="#cdd6f4", family="JetBrains Mono"),
        xaxis=dict(
            title="Risk Skoruna Katkı (puan)", gridcolor="#313244", color="#6c7086",
            range=[0, max(bar_values) * 1.5 + 5 if max(bar_values) > 0 else 20],
        ),
        yaxis=dict(gridcolor="#313244", color="#cdd6f4"),
        margin=dict(l=10, r=120, t=10, b=10), height=250,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(
        "<div style='font-size:12px; color:#6c7086; font-family:JetBrains Mono;'>"
        "Her çubuk, o sinyalin nihai risk skoruna katkısını gösterir (puan). Toplam = Risk Skoru.</div>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Üç ana sekme: analiz, performans, toplu
tab1, tab2, tab3 = st.tabs(["🔍 E-posta Analizi", "📊 Model Performansı", "📂 Toplu Analiz"])

# ══════════════════════════════════════════════════════════
# SEKME 1 — E-posta Analizi
# ══════════════════════════════════════════════════════════
with tab1:
    st.markdown("## 🛡️ Phishing E-posta Tespiti")
    st.markdown(
        "<p style='color:#6c7086; font-size:14px;'>E-postanın konu ve içeriğini girerek phishing analizi yapın.</p>",
        unsafe_allow_html=True,
    )
    st.divider()

    # Konu ayrı alınıyor, header analizinde de kullanılıyor
    subject = st.text_input("📌 Konu (Subject)", placeholder="Örn: Hesabınız askıya alındı")
    body    = st.text_area("📄 İçerik (Body)", height=200, placeholder="Örn: Hesabınıza şüpheli giriş yapıldı. Hemen doğrulayın...")

    # Başlık analizi isteğe bağlı, sağlanırsa daha hassas sonuç veriyor
    with st.expander("📧 Başlık Analizi (opsiyonel) — From / Reply-To"):
        hcol1, hcol2 = st.columns(2)
        with hcol1:
            from_addr = st.text_input("Gönderici (From)", placeholder="ornek@banka-guvenli.tk")
        with hcol2:
            reply_to = st.text_input("Yanıt Adresi (Reply-To)", placeholder="saldirgan@gmail.com")

    analyze_clicked = st.button("🔍 Analiz Et", use_container_width=True, type="primary")

    if analyze_clicked:
        # İkisi de boşsa uyarı ver, analiz etmeye gerek yok
        if not body.strip() and not subject.strip():
            st.warning("⚠️ Lütfen en az bir alan doldurun.")
        else:
            try:
                from src.predict import predict_details_with_headers
                text   = build_email_text(subject, body)
                result = predict_details_with_headers(text, from_addr, reply_to, subject)

                # Sonuçları değişkenlere açıyoruz, her şeyin üstünde tutmak okunmayı kolaylaştırıyor
                label           = result["label"]
                confidence      = result["confidence"]
                risk_score      = result["risk_score"]
                phish_prob      = result["phishing_probability"]
                keyword_score   = result["keyword_score"]
                keywords        = result["matched_keywords"]
                phishing_type   = result.get("phishing_type", "")
                url_analysis    = result.get("url_analysis", {"urls": [], "max_score": 0, "suspicious_count": 0, "total_count": 0})
                anomaly         = result.get("anomaly",        {"score": 0, "is_anomaly": False, "available": False})
                header_analysis = result.get("header_analysis", {"score": 0, "flags": [], "is_suspicious": False})
                actions         = result.get("actions", [])

                is_phishing   = label == "YES"
                verdict_class = "verdict-phishing" if is_phishing else "verdict-safe"
                verdict_text  = "🚨 PHİSHİNG"     if is_phishing else "✅ GÜVENLİ"

                st.divider()
                st.markdown("### Analiz Sonucu")
                st.markdown(f'<div class="verdict-banner {verdict_class}">{verdict_text}</div>', unsafe_allow_html=True)

                # Güven skoru düşükse modelin kararsız olduğunu kullanıcıya söylüyoruz
                if confidence < 30:
                    st.markdown(
                        '<div class="low-confidence-warning">⚠️ <strong>Düşük güven skoru</strong> — '
                        'Model bu e-posta hakkında emin değil. Sonucu dikkatli değerlendirin.</div>',
                        unsafe_allow_html=True,
                    )

                # Temel metrik kartları
                col1, col2 = st.columns(2)
                with col1:
                    val_class = "phishing-yes" if is_phishing else "phishing-no"
                    st.markdown(f'<div class="metric-card"><div class="metric-label">Karar</div><div class="metric-value {val_class}">{label}</div></div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="metric-card"><div class="metric-label">Model Olasılığı</div><div class="metric-value neutral">%{phish_prob:.1f}</div></div>', unsafe_allow_html=True)
                with col2:
                    st.markdown(f'<div class="metric-card"><div class="metric-label">Güven Skoru</div><div class="metric-value neutral">%{confidence:.1f}</div></div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="metric-card"><div class="metric-label">Anahtar Kelime Skoru</div><div class="metric-value neutral">%{keyword_score:.1f}</div></div>', unsafe_allow_html=True)

                # Gauge grafiği, sarı çizgiyi geçerse phishing
                gauge_color = "#f38ba8" if is_phishing else "#a6e3a1"
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=risk_score,
                    title={"text": "Risk Skoru", "font": {"size": 16, "color": "#cdd6f4", "family": "JetBrains Mono"}},
                    number={"font": {"size": 36, "color": gauge_color, "family": "JetBrains Mono"}, "suffix": "/100"},
                    gauge={
                        "axis": {
                            "range": [0, 100],
                            "tickcolor": "#6c7086",
                            "tickfont": {"color": "#6c7086", "size": 11},
                        },
                        "bar":         {"color": gauge_color, "thickness": 0.25},
                        "bgcolor":     "#1e1e2e",
                        "bordercolor": "#313244",
                        # Yeşil alan güvenli, kırmızı alan phishing bölgesi
                        "steps": [
                            {"range": [0, PHISHING_THRESHOLD], "color": "#0d2b1e"},
                            {"range": [PHISHING_THRESHOLD, 100], "color": "#3b1219"},
                        ],
                        "threshold": {
                            "line":      {"color": "#f9e2af", "width": 3},
                            "thickness": 0.75,
                            "value":     PHISHING_THRESHOLD,
                        },
                    },
                ))
                fig_gauge.update_layout(
                    paper_bgcolor="#1e1e2e",
                    font={"color": "#cdd6f4", "family": "JetBrains Mono"},
                    margin={"t": 60, "b": 10, "l": 30, "r": 30},
                    height=220,
                )
                st.plotly_chart(fig_gauge, use_container_width=True)
                st.markdown(
                    f"<div style='text-align:center; font-family:JetBrains Mono; font-size:12px; color:#6c7086;'>"
                    f"Eşik: <strong style='color:#f9e2af'>{PHISHING_THRESHOLD:.0f}</strong> &nbsp;·&nbsp; "
                    f"Sarı çizgiyi geçerse PHİSHİNG</div>",
                    unsafe_allow_html=True,
                )

                # 5 katmanlı sinyal grafiği
                bd = result.get("score_breakdown", {})
                _render_signal_breakdown(bd)

                # Eşleşen şüpheli kelimeler tag olarak gösteriliyor
                st.markdown("<div style='margin-top:20px;'>", unsafe_allow_html=True)
                if keywords:
                    st.markdown("<div class='metric-label' style='margin-bottom:6px;'>🔑 Tespit Edilen Şüpheli Kelimeler</div>", unsafe_allow_html=True)
                    tags_html = "".join(f'<span class="keyword-tag">{kw}</span>' for kw in keywords)
                    st.markdown(tags_html, unsafe_allow_html=True)
                else:
                    st.markdown("<div style='color:#6c7086; font-size:13px;'>Belirgin şüpheli kelime bulunamadı.</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

                # Anomali ve başlık skoru yan yana
                a_col1, a_col2 = st.columns(2)
                with a_col1:
                    if anomaly["available"]:
                        a_score = anomaly["score"]
                        a_color = "#f38ba8" if anomaly["is_anomaly"] else "#a6e3a1"
                        a_label = "ANOMALİ" if anomaly["is_anomaly"] else "Normal Kalıp"
                        st.markdown(
                            f'<div class="metric-card"><div class="metric-label">🧬 Anomali Skoru</div>'
                            f'<div class="metric-value" style="color:{a_color}">{a_score:.0f}/100</div>'
                            f'<div style="font-size:11px; color:{a_color}; margin-top:2px;">{a_label}</div></div>',
                            unsafe_allow_html=True,
                        )
                    else:
                        # Anomali modeli henüz eğitilmemişse bunu karta yazıyoruz
                        st.markdown(
                            '<div class="metric-card"><div class="metric-label">🧬 Anomali Skoru</div>'
                            '<div style="font-size:12px; color:#6c7086; margin-top:6px;">Model eğitilmedi —<br>train_model.py çalıştırın</div></div>',
                            unsafe_allow_html=True,
                        )
                with a_col2:
                    h_score = header_analysis.get("score", 0)
                    h_color = "#f38ba8" if header_analysis.get("is_suspicious") else "#a6e3a1"
                    h_flags = header_analysis.get("flags", [])
                    st.markdown(
                        f'<div class="metric-card"><div class="metric-label">📧 Başlık Risk Skoru</div>'
                        f'<div class="metric-value" style="color:{h_color}">{h_score}/100</div>'
                        f'<div style="font-size:11px; color:#6c7086; margin-top:2px;">{len(h_flags)} uyarı</div></div>',
                        unsafe_allow_html=True,
                    )
                # Header uyarıları varsa her birini kart olarak listeliyoruz
                if h_flags:
                    for flag in h_flags:
                        st.markdown(
                            f"<div style='background:#1e1e2e; border-left:3px solid #f9e2af; border-radius:6px; "
                            f"padding:6px 14px; margin:3px 0; font-family:JetBrains Mono; font-size:12px; color:#f9e2af;'>"
                            f"⚠️ {flag}</div>",
                            unsafe_allow_html=True,
                        )

                # Phishing türü rozeti, saldırı kategorisini renk kodla gösteriyor
                if is_phishing and phishing_type:
                    type_colors = {
                        "Finansal Dolandırıcılık": "#f9e2af",
                        "Kimlik Hırsızlığı":       "#cba6f7",
                        "Kötü Amaçlı Link":        "#f38ba8",
                        "Sahte Ödül/Çekiliş":      "#fab387",
                        "Sahte Kargo/Teslimat":    "#89dceb",
                        "Marka Taklidi":           "#a6e3a1",
                        "Genel Phishing":          "#6c7086",
                    }
                    badge_color = type_colors.get(phishing_type, "#6c7086")
                    st.markdown(
                        f"<div style='margin-top:16px;'>"
                        f"<span class='metric-label'>🏷️ Saldırı Türü</span><br>"
                        f"<span style='display:inline-block; margin-top:6px; background:#1e1e2e; border:1px solid {badge_color}; "
                        f"color:{badge_color}; border-radius:20px; padding:4px 16px; font-family:JetBrains Mono; font-size:13px; font-weight:700;'>"
                        f"{phishing_type}</span></div>",
                        unsafe_allow_html=True,
                    )

                # URL analizi, sadece URL varsa gösteriliyor
                if url_analysis["total_count"] > 0:
                    st.markdown("<div style='margin-top:20px;'>", unsafe_allow_html=True)
                    st.markdown("### 🔗 URL Analizi")
                    url_col1, url_col2 = st.columns(2)
                    with url_col1:
                        susp  = url_analysis["suspicious_count"]
                        total = url_analysis["total_count"]
                        label_color = "#f38ba8" if susp > 0 else "#a6e3a1"
                        st.markdown(
                            f'<div class="metric-card"><div class="metric-label">Şüpheli URL</div>'
                            f'<div class="metric-value" style="color:{label_color}">{susp} / {total}</div></div>',
                            unsafe_allow_html=True,
                        )
                    with url_col2:
                        mx       = url_analysis["max_score"]
                        mx_color = "#f38ba8" if mx >= 40 else "#f9e2af" if mx >= 20 else "#a6e3a1"
                        st.markdown(
                            f'<div class="metric-card"><div class="metric-label">Maks URL Risk Skoru</div>'
                            f'<div class="metric-value" style="color:{mx_color}">{mx}/100</div></div>',
                            unsafe_allow_html=True,
                        )
                    # Her URL için bayrakları göster, temiz URL'leri atlıyoruz
                    for url_item in url_analysis["urls"]:
                        if url_item["flags"]:
                            flags_html = " &nbsp;·&nbsp; ".join(url_item["flags"])
                            border     = "#f38ba8" if url_item["is_suspicious"] else "#313244"
                            st.markdown(
                                f"<div style='background:#1e1e2e; border-left:3px solid {border}; "
                                f"border-radius:6px; padding:8px 14px; margin:4px 0; font-family:JetBrains Mono; font-size:12px;'>"
                                f"<span style='color:#cdd6f4'>{url_item['url']}</span><br>"
                                f"<span style='color:#6c7086'>{flags_html}</span></div>",
                                unsafe_allow_html=True,
                            )
                    st.markdown("</div>", unsafe_allow_html=True)

                # SHAP açıklaması, model hangi kelimeler için nasıl karar verdi
                st.markdown("<div style='margin-top:20px;'>", unsafe_allow_html=True)
                st.markdown("### 🧠 Model Kararı — SHAP Açıklaması")
                try:
                    from src.explain_model import get_shap_explanation
                    from src.predict import load_model_objects as _load_models
                    _model, _vectorizer = _load_models()
                    shap_words = get_shap_explanation(text, _model, _vectorizer, top_n=12)
                    _render_explanation_chart(
                        shap_words, "SHAP Değeri", "#f38ba8", "#a6e3a1",
                        "<span style='color:#f38ba8'>■</span> Phishing yönünde etkili &nbsp;·&nbsp; "
                        "<span style='color:#a6e3a1'>■</span> Normal yönünde etkili",
                    )
                except Exception as shap_err:
                    st.info(f"SHAP hesaplanamadı: {shap_err}")
                st.markdown("</div>", unsafe_allow_html=True)

                # LIME açıklaması, kelimeleri tek tek çıkararak kararın değişip değişmediğine bakıyor
                st.markdown("<div style='margin-top:20px;'>", unsafe_allow_html=True)
                st.markdown("### 🔬 Model Kararı — LIME Açıklaması")
                try:
                    from src.explain_model import get_lime_explanation
                    from src.predict import load_model_objects as _load_models2
                    _model2, _vectorizer2 = _load_models2()
                    with st.spinner("LIME hesaplanıyor..."):
                        lime_words = get_lime_explanation(text, _model2, _vectorizer2, top_n=12)
                    _render_explanation_chart(
                        lime_words, "LIME Etkisi", "#f38ba8", "#a6e3a1",
                        "LIME, metni bozarak hangi kelimelerin kararı değiştirdiğini ölçer.",
                    )
                except Exception as lime_err:
                    st.info(f"LIME hesaplanamadı: {lime_err}")
                st.markdown("</div>", unsafe_allow_html=True)

                # Transformer LIME, sadece model eğitildiyse çalıştırılıyor
                st.markdown("<div style='margin-top:20px;'>", unsafe_allow_html=True)
                st.markdown("### 🤖 Transformer Kararı — LIME Açıklaması")
                try:
                    from src.explain_model import get_transformer_lime_explanation
                    import src.transformer_predictor as _tr_check
                    if _tr_check.is_available():
                        with st.spinner("Transformer LIME hesaplanıyor..."):
                            tr_lime_words = get_transformer_lime_explanation(text, top_n=12)
                        if tr_lime_words:
                            _render_explanation_chart(
                                tr_lime_words, "Transformer LIME Etkisi", "#cba6f7", "#89dceb",
                                "<span style='color:#cba6f7'>■</span> Phishing yönünde etkili &nbsp;·&nbsp; "
                                "<span style='color:#89dceb'>■</span> Normal yönünde etkili &nbsp;·&nbsp; "
                                "DistilBERT modeli üzerinde LIME black-box analizi.",
                            )
                        else:
                            st.info("Transformer LIME sonuç üretemedi.")
                    else:
                        st.markdown(
                            "<div style='background:#1e1e2e; border-left:3px solid #6c7086; border-radius:6px; "
                            "padding:8px 14px; font-family:JetBrains Mono; font-size:12px; color:#6c7086;'>"
                            "⚠️ Transformer modeli eğitilmemiş — <code>python src/train_transformer.py</code></div>",
                            unsafe_allow_html=True,
                        )
                except Exception as tr_lime_err:
                    st.info(f"Transformer LIME hesaplanamadı: {tr_lime_err}")
                st.markdown("</div>", unsafe_allow_html=True)

                # Aksiyon önerileri, phishing türüne göre değişiyor
                st.markdown("<div style='margin-top:20px;'>", unsafe_allow_html=True)
                st.markdown("### 📋 Önerilen Aksiyonlar")
                action_border = "#f38ba8" if is_phishing else "#a6e3a1"
                action_icon   = "🚨"       if is_phishing else "✅"
                for action in actions:
                    st.markdown(
                        f"<div style='background:#1e1e2e; border-left:3px solid {action_border}; "
                        f"border-radius:6px; padding:10px 16px; margin:4px 0; "
                        f"font-family:JetBrains Mono; font-size:13px; color:#cdd6f4;'>"
                        f"{action_icon} {action}</div>",
                        unsafe_allow_html=True,
                    )
                st.markdown("</div>", unsafe_allow_html=True)

                # HTML rapor indirme butonu
                st.markdown("<div style='margin-top:24px;'>", unsafe_allow_html=True)
                st.markdown("### 📄 Rapor")
                try:
                    from src.report_generator import generate_single_report
                    _preview     = f"{subject} {body}"[:300] if (subject or body) else text[:300]
                    _html_report = generate_single_report(result, email_preview=_preview)
                    st.download_button(
                        label="⬇️ HTML Raporu İndir",
                        data=_html_report.encode("utf-8"),
                        file_name="phishing_analiz_raporu.html",
                        mime="text/html",
                        use_container_width=True,
                    )
                except Exception as rep_err:
                    st.info(f"Rapor oluşturulamadı: {rep_err}")
                st.markdown("</div>", unsafe_allow_html=True)

            except FileNotFoundError as error:
                st.error(f"❌ {error}")

# ══════════════════════════════════════════════════════════
# SEKME 2 — Model Performansı
# ══════════════════════════════════════════════════════════
with tab2:
    st.markdown("## 📊 Model Performans Raporu")
    st.markdown(
        "<p style='color:#6c7086; font-size:14px;'>Eğitim sırasında kaydedilen test verisi metrikleri.</p>",
        unsafe_allow_html=True,
    )
    st.divider()

    def load_performance_data():
        # Test sonuçları train_model.py çalıştırıldıktan sonra oluşuyor
        project_root = Path(__file__).resolve().parents[1]
        results_path = project_root / "models" / "test_results.pkl"

        if not results_path.exists():
            raise FileNotFoundError(
                "Test sonuçları bulunamadı. Önce `python src/train_model.py` çalıştırın."
            )

        with open(results_path, "rb") as f:
            r = pickle.load(f)

        return (
            r["y_test"], r["y_pred"], r["y_prob"],
            r.get("dataset_size", 0), r.get("test_size", 0),
            r.get("roc_auc", None), r.get("cv_metrics", {}),
        )

    try:
        y_test, y_pred, y_prob, dataset_size, test_size, stored_roc_auc, cv_metrics = load_performance_data()

        cm = confusion_matrix(y_test, y_pred, labels=[0, 1])
        tn, fp, fn, tp = cm.ravel()

        # Temel sınıflandırma metrikleri
        accuracy  = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall    = recall_score(y_test, y_pred, zero_division=0)
        f1        = f1_score(y_test, y_pred, zero_division=0)

        # ROC hesaplamaları
        fpr_rate         = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        fpr_arr, tpr_arr, _ = roc_curve(y_test, y_prob)
        roc_auc_val      = auc(fpr_arr, tpr_arr)

        # Altı metriği yan yana kart olarak gösteriyoruz
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        for col, lbl, value, highlight in [
            (c1, "Accuracy",           accuracy,    False),
            (c2, "Precision",          precision,   False),
            (c3, "Recall",             recall,      False),
            (c4, "F1 Score",           f1,          False),
            (c5, "ROC AUC",            roc_auc_val, False),
            (c6, "Yanlış Alarm Oranı", fpr_rate,    True),   # yüksekse kötü, kırmızı
        ]:
            with col:
                val_color = "#f38ba8" if (highlight and value > 0.05) else "#89b4fa"
                st.markdown(f"""
                <div class="perf-card">
                    <div class="perf-value" style="color:{val_color}">%{value*100:.1f}</div>
                    <div class="perf-label">{lbl}</div>
                </div>
                """, unsafe_allow_html=True)

        # Dataset boyutunu göster
        if dataset_size:
            st.markdown(
                f"<div style='font-family:JetBrains Mono; font-size:12px; color:#6c7086; margin:8px 0 16px;'>"
                f"Toplam dataset: <strong style='color:#cdd6f4'>{dataset_size:,}</strong> e-posta &nbsp;·&nbsp; "
                f"Grafikler: <strong style='color:#cdd6f4'>{test_size:,}</strong> e-posta"
                f"</div>",
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # Confusion matrix ve ROC eğrisi yan yana
        col_cm, col_roc = st.columns(2)

        with col_cm:
            st.markdown("### 🔲 Confusion Matrix")
            fig_cm = go.Figure(data=go.Heatmap(
                z=[[tn, fp], [fn, tp]],
                x=["Tahmin: Normal", "Tahmin: Phishing"],
                y=["Gerçek: Normal", "Gerçek: Phishing"],
                text=[[str(tn), str(fp)], [str(fn), str(tp)]],
                texttemplate="%{text}",
                textfont={"size": 24, "color": "white"},
                colorscale=[[0, "#1e1e2e"], [0.5, "#313244"], [1, "#89b4fa"]],
                showscale=False,
            ))
            fig_cm.update_layout(
                paper_bgcolor="#1e1e2e",
                plot_bgcolor="#1e1e2e",
                font=dict(color="#cdd6f4", family="JetBrains Mono"),
                margin=dict(l=10, r=10, t=10, b=10),
                height=300,
                xaxis=dict(side="bottom"),
            )
            st.plotly_chart(fig_cm, use_container_width=True)
            # TN, TP, FP, FN değerlerini renk kodlu metin olarak göster
            st.markdown(f"""
            <div style="font-family: JetBrains Mono; font-size:13px; color:#6c7086; margin-top:8px;">
                ✅ Doğru Normal (TN): <span style="color:#a6e3a1">{tn}</span> &nbsp;|&nbsp;
                ✅ Doğru Phishing (TP): <span style="color:#a6e3a1">{tp}</span><br>
                ❌ Yanlış Alarm (FP): <span style="color:#f38ba8">{fp}</span> &nbsp;|&nbsp;
                ❌ Kaçırılan (FN): <span style="color:#f38ba8">{fn}</span>
            </div>
            """, unsafe_allow_html=True)

        with col_roc:
            st.markdown("### 📈 ROC Eğrisi")
            fig_roc = go.Figure()
            fig_roc.add_trace(go.Scatter(
                x=fpr_arr, y=tpr_arr,
                mode="lines",
                name=f"ROC (AUC = {roc_auc_val:.3f})",
                line=dict(color="#89b4fa", width=2),
                fill="tozeroy",
                fillcolor="rgba(137,180,250,0.1)",
            ))
            # Rastgele tahmin çizgisi karşılaştırma için ekleniyor
            fig_roc.add_trace(go.Scatter(
                x=[0, 1], y=[0, 1],
                mode="lines",
                name="Rastgele tahmin",
                line=dict(color="#6c7086", width=1, dash="dash"),
            ))
            fig_roc.update_layout(
                paper_bgcolor="#1e1e2e",
                plot_bgcolor="#1e1e2e",
                font=dict(color="#cdd6f4", family="JetBrains Mono"),
                xaxis=dict(title="False Positive Rate", gridcolor="#313244", color="#6c7086"),
                yaxis=dict(title="True Positive Rate",  gridcolor="#313244", color="#6c7086"),
                legend=dict(bgcolor="#1e1e2e", bordercolor="#313244"),
                margin=dict(l=10, r=10, t=10, b=10),
                height=300,
            )
            st.plotly_chart(fig_roc, use_container_width=True)
            st.markdown(f"""
            <div style="font-family: JetBrains Mono; font-size:13px; color:#6c7086; margin-top:8px;">
                AUC = <span style="color:#89b4fa">{roc_auc_val:.4f}</span> &nbsp;·&nbsp;
                1.0'e ne kadar yakınsa model o kadar iyi.
            </div>
            """, unsafe_allow_html=True)

        # Phishing ve normal e-postaların olasılık dağılımını gösteriyor
        st.markdown("### 🎯 Phishing Olasılığı Dağılımı")

        phish_probs  = y_prob[y_test == 1]
        normal_probs = y_prob[y_test == 0]

        fig_dist = go.Figure()
        fig_dist.add_trace(go.Histogram(
            x=phish_probs,  name="Phishing",
            marker_color="#f38ba8", opacity=0.7, nbinsx=40,
        ))
        fig_dist.add_trace(go.Histogram(
            x=normal_probs, name="Normal",
            marker_color="#a6e3a1", opacity=0.7, nbinsx=40,
        ))
        # Eşik çizgisi, iki dağılımın örtüşmediği bir yerde olmalı
        fig_dist.add_vline(
            x=PHISHING_THRESHOLD / 100,
            line_dash="dash", line_color="#f9e2af",
            annotation_text=f"Eşik: {PHISHING_THRESHOLD:.0f}",
            annotation_font_color="#f9e2af",
        )
        fig_dist.update_layout(
            barmode="overlay",
            paper_bgcolor="#1e1e2e",
            plot_bgcolor="#1e1e2e",
            font=dict(color="#cdd6f4", family="JetBrains Mono"),
            xaxis=dict(title="Phishing Olasılığı", gridcolor="#313244", color="#6c7086"),
            yaxis=dict(title="E-posta Sayısı",      gridcolor="#313244", color="#6c7086"),
            legend=dict(bgcolor="#1e1e2e", bordercolor="#313244"),
            margin=dict(l=10, r=10, t=10, b=10),
            height=300,
        )
        st.plotly_chart(fig_dist, use_container_width=True)

        # En yüksek olasılıklı k e-postadan kaçının gerçekten phishing olduğunu gösteriyor
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 🎯 Precision@k")
        k_values   = [10, 50, 100, 500]
        sorted_idx = np.argsort(y_prob)[::-1]
        pk_cols    = st.columns(len(k_values))
        for col, k in zip(pk_cols, k_values):
            if k <= len(y_test):
                top_k_labels = y_test[sorted_idx[:k]]
                pk = top_k_labels.sum() / k
                with col:
                    st.markdown(f"""
                    <div class="perf-card">
                        <div class="perf-value">%{pk*100:.1f}</div>
                        <div class="perf-label">P@{k}</div>
                    </div>
                    """, unsafe_allow_html=True)

        # Cross-validation sonuçları modelin genelleme gücünü gösteriyor
        if cv_metrics:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### 🔁 5-Fold Cross-Validation")
            st.markdown(
                "<div style='font-family:JetBrains Mono; font-size:12px; color:#6c7086; margin-bottom:12px;'>"
                "Modelin genelleme gücü — farklı veri bölümlerinde tutarlı performans</div>",
                unsafe_allow_html=True,
            )
            cv_cols = st.columns(3)
            for col, lbl, mean_key, std_key in [
                (cv_cols[0], "CV Accuracy",  "accuracy_mean", "accuracy_std"),
                (cv_cols[1], "CV F1 Score",  "f1_mean",       "f1_std"),
                (cv_cols[2], "CV ROC AUC",   "roc_auc_mean",  "roc_auc_std"),
            ]:
                mean = cv_metrics.get(mean_key, 0)
                std  = cv_metrics.get(std_key, 0)
                with col:
                    st.markdown(f"""
                    <div class="perf-card">
                        <div class="perf-value" style="color:#a6e3a1">%{mean*100:.2f}</div>
                        <div class="perf-label">{lbl}</div>
                        <div style="font-size:11px; color:#6c7086; margin-top:4px;">± %{std*100:.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)

            # Her fold için F1 ve ROC AUC grafiği, tutarsız fold varsa gözükür
            fold_f1  = cv_metrics.get("fold_f1", [])
            fold_roc = cv_metrics.get("fold_roc_auc", [])
            if fold_f1:
                fig_cv = go.Figure()
                fig_cv.add_trace(go.Bar(
                    x=[f"Fold {i+1}" for i in range(len(fold_f1))],
                    y=[v * 100 for v in fold_f1],
                    name="F1 Score",
                    marker_color="#a6e3a1",
                ))
                if fold_roc:
                    fig_cv.add_trace(go.Bar(
                        x=[f"Fold {i+1}" for i in range(len(fold_roc))],
                        y=[v * 100 for v in fold_roc],
                        name="ROC AUC",
                        marker_color="#89b4fa",
                    ))
                fig_cv.update_layout(
                    barmode="group",
                    paper_bgcolor="#1e1e2e", plot_bgcolor="#1e1e2e",
                    font=dict(color="#cdd6f4", family="JetBrains Mono"),
                    xaxis=dict(gridcolor="#313244", color="#6c7086"),
                    yaxis=dict(title="%", gridcolor="#313244", color="#6c7086", range=[95, 101]),
                    legend=dict(bgcolor="#1e1e2e", bordercolor="#313244"),
                    margin=dict(l=10, r=10, t=10, b=10),
                    height=250,
                )
                st.plotly_chart(fig_cv, use_container_width=True)

        # Transformer eğitildiyse TF-IDF LR ile karşılaştırma tablosu gösteriliyor
        transformer_path = Path(__file__).resolve().parents[1] / "models" / "transformer_test_results.pkl"
        if transformer_path.exists():
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### 🤖 Model Karşılaştırması: TF-IDF + LR vs Transformer")
            with open(transformer_path, "rb") as f:
                tr = pickle.load(f)

            comp_cols = st.columns(4)
            metrics = [
                ("Accuracy",  accuracy,  tr.get("accuracy",  0)),
                ("Precision", precision, tr.get("precision", 0)),
                ("Recall",    recall,    tr.get("recall",    0)),
                ("F1 Score",  f1,        tr.get("f1",        0)),
            ]
            for col, (label_m, lr_val, tr_val) in zip(comp_cols, metrics):
                # Transformer daha iyiyse yeşil, değilse kırmızı göster
                better   = tr_val >= lr_val
                tr_color = "#a6e3a1" if better else "#f38ba8"
                with col:
                    st.markdown(f"""
                    <div class="perf-card">
                        <div class="perf-label">{label_m}</div>
                        <div style="margin-top:8px; font-family:JetBrains Mono; font-size:13px; color:#6c7086;">TF-IDF+LR</div>
                        <div style="font-size:22px; font-weight:700; color:#89b4fa;">%{lr_val*100:.1f}</div>
                        <div style="margin-top:6px; font-family:JetBrains Mono; font-size:13px; color:#6c7086;">Transformer</div>
                        <div style="font-size:22px; font-weight:700; color:{tr_color};">%{tr_val*100:.1f}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown("<br>", unsafe_allow_html=True)
            st.info("🤖 Transformer modeli henüz eğitilmedi. `python src/train_transformer.py` çalıştırın.")

    except FileNotFoundError:
        st.error("❌ Model bulunamadı. Önce `python src/train_model.py` çalıştırın.")
    except Exception as e:
        st.error(f"❌ Hata: {e}")

# ══════════════════════════════════════════════════════════
# SEKME 3 — Toplu Analiz
# ══════════════════════════════════════════════════════════
with tab3:
    st.markdown("## 📂 Toplu E-posta Analizi")
    st.markdown(
        "<p style='color:#6c7086; font-size:14px;'>Birden fazla e-postayı aynı anda analiz edin, risk skoruna göre önceliklendirilmiş liste alın.</p>",
        unsafe_allow_html=True,
    )
    st.divider()

    # İki giriş yöntemi: metin kutusu ya da CSV dosyası
    batch_mode = st.radio("Giriş yöntemi", ["📝 Metin Girişi", "📁 CSV Yükle"], horizontal=True)
    emails_to_analyze: list[str] = []

    if batch_mode == "📝 Metin Girişi":
        st.markdown("Her satıra bir e-posta içeriği yazın:")
        batch_text = st.text_area(
            "E-postalar (her satır = bir e-posta)", height=200,
            placeholder="1. e-posta metni\n2. e-posta metni\n3. e-posta metni",
        )
        if batch_text.strip():
            # Boş satırları atlıyoruz
            emails_to_analyze = [line.strip() for line in batch_text.strip().splitlines() if line.strip()]
    else:
        uploaded = st.file_uploader("CSV yükle (body sütunu gerekli)", type=["csv"])
        if uploaded:
            try:
                batch_df = pd.read_csv(uploaded)
                # body sütunu yoksa ilk sütunu kullanıyoruz
                col_name          = "body" if "body" in batch_df.columns else batch_df.columns[0]
                emails_to_analyze = batch_df[col_name].dropna().astype(str).tolist()
                st.success(f"✅ {len(emails_to_analyze)} e-posta yüklendi ('{col_name}' sütunu)")
            except Exception as ex:
                st.error(f"CSV okunamadı: {ex}")

    # E-posta yoksa butonu devre dışı bırakıyoruz
    batch_clicked = st.button(
        "🔍 Toplu Analiz Başlat", use_container_width=True, type="primary",
        disabled=len(emails_to_analyze) == 0,
    )

    if batch_clicked and emails_to_analyze:
        # Çok fazla e-posta gelirse sadece ilk 200'ünü alıyoruz
        max_batch = 200
        if len(emails_to_analyze) > max_batch:
            st.warning(f"⚠️ İlk {max_batch} e-posta analiz edildi (toplam: {len(emails_to_analyze)})")
            emails_to_analyze = emails_to_analyze[:max_batch]

        results_list = []
        progress     = st.progress(0, text="Analiz ediliyor...")
        for i, email_text in enumerate(emails_to_analyze):
            try:
                res = predict_details(email_text)
                results_list.append({
                    "No":             i + 1,
                    "Önizleme":       email_text[:60] + "..." if len(email_text) > 60 else email_text,
                    "Karar":          res["label"],
                    "Risk Skoru":     round(res["risk_score"], 1),
                    "Model Olasılık": round(res["phishing_probability"], 1),
                    "Phishing Türü":  res.get("phishing_type", ""),
                    "URL Sayısı":     res["url_analysis"]["total_count"],
                    "Şüpheli URL":    res["url_analysis"]["suspicious_count"],
                })
            except Exception:
                results_list.append({
                    "No": i + 1, "Önizleme": email_text[:60], "Karar": "HATA",
                    "Risk Skoru": 0, "Model Olasılık": 0, "Phishing Türü": "",
                    "URL Sayısı": 0, "Şüpheli URL": 0,
                })
            progress.progress(
                (i + 1) / len(emails_to_analyze),
                text=f"Analiz ediliyor... {i+1}/{len(emails_to_analyze)}",
            )

        progress.empty()
        # Risk skoruna göre sırala, en tehlikeliler üste
        results_df    = pd.DataFrame(results_list).sort_values("Risk Skoru", ascending=False).reset_index(drop=True)
        phishing_count = (results_df["Karar"] == "YES").sum()
        normal_count   = (results_df["Karar"] == "NO").sum()

        # Özet sayaçlar
        sc1, sc2, sc3 = st.columns(3)
        sc1.metric("Toplam E-posta", len(results_df))
        sc2.metric("🚨 Phishing",    phishing_count)
        sc3.metric("✅ Güvenli",     normal_count)

        st.markdown("### 📋 Önceliklendirilmiş Liste (Risk Skoruna Göre)")

        def color_row(row):
            # Phishing satırları kırmızı, güvenli satırlar yeşil zemine
            color = "background-color: #3b1219;" if row["Karar"] == "YES" else "background-color: #0d2b1e;"
            return [color] * len(row)

        st.dataframe(
            results_df.style.apply(color_row, axis=1),
            use_container_width=True,
            height=400,
        )

        # CSV ve HTML rapor indirme
        dl_col1, dl_col2 = st.columns(2)
        csv_out = results_df.to_csv(index=False).encode("utf-8")
        with dl_col1:
            st.download_button(
                "⬇️ CSV İndir", csv_out,
                "phishing_analiz_sonuclari.csv", "text/csv",
                use_container_width=True,
            )
        with dl_col2:
            try:
                from src.report_generator import generate_batch_report as _gen_batch
                import tempfile, os as _os
                _batch_results  = []
                _batch_previews = []
                for _, row in results_df.iterrows():
                    _batch_results.append({
                        "label":       row["Karar"],
                        "risk_score":  row["Risk Skoru"],
                        "phishing_type": row.get("Phishing Türü", ""),
                        "url_analysis": {
                            "suspicious_count": row.get("Şüpheli URL", 0),
                            "total_count":       row.get("URL Sayısı", 0),
                            "urls": [],
                        },
                        "score_breakdown": {"signals": {}},
                    })
                    _batch_previews.append(str(row.get("Önizleme", "")))
                # Geçici dosyaya yazıp okuyoruz, generate_batch_report dosya yolu istiyor
                _tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
                _tmp.close()
                _gen_batch(_batch_results, _tmp.name, _batch_previews)
                with open(_tmp.name, "rb") as _f:
                    _html_batch = _f.read()
                _os.unlink(_tmp.name)
                st.download_button(
                    "⬇️ HTML Raporu İndir", _html_batch,
                    "phishing_toplu_rapor.html", "text/html",
                    use_container_width=True,
                )
            except Exception as _batch_err:
                st.info(f"HTML rapor: {_batch_err}")
