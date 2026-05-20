import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pickle
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from sklearn.metrics import confusion_matrix, roc_curve, auc, accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split

from src.predict import predict_details, PHISHING_THRESHOLD
from src.text_utils import advanced_preprocessing, build_email_text

st.set_page_config(
    page_title="Phishing E-posta Tespiti",
    page_icon="🛡️",
    layout="wide",
)

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

tab1, tab2 = st.tabs(["🔍 E-posta Analizi", "📊 Model Performansı"])

# ══════════════════════════════════════════════════════════
# SEKME 1 — E-posta Analizi
# ══════════════════════════════════════════════════════════
with tab1:
    st.markdown("## 🛡️ Phishing E-posta Tespiti")
    st.markdown("<p style='color:#6c7086; font-size:14px;'>E-postanın konu ve içeriğini girerek phishing analizi yapın.</p>", unsafe_allow_html=True)
    st.divider()

    subject = st.text_input("📌 Konu (Subject)", placeholder="Örn: Hesabınız askıya alındı")
    body = st.text_area("📄 İçerik (Body)", height=200, placeholder="Örn: Hesabınıza şüpheli giriş yapıldı. Hemen doğrulayın...")
    analyze_clicked = st.button("🔍 Analiz Et", use_container_width=True, type="primary")

    if analyze_clicked:
        if not body.strip() and not subject.strip():
            st.warning("⚠️ Lütfen en az bir alan doldurun.")
        else:
            try:
                text = build_email_text(subject, body)
                result = predict_details(text)

                label         = result["label"]
                confidence    = result["confidence"]
                risk_score    = result["risk_score"]
                phish_prob    = result["phishing_probability"]
                keyword_score = result["keyword_score"]
                keywords      = result["matched_keywords"]

                is_phishing   = label == "YES"
                verdict_class = "verdict-phishing" if is_phishing else "verdict-safe"
                verdict_text  = "🚨 PHİSHİNG" if is_phishing else "✅ GÜVENLİ"

                st.divider()
                st.markdown("### Analiz Sonucu")
                st.markdown(f'<div class="verdict-banner {verdict_class}">{verdict_text}</div>', unsafe_allow_html=True)

                if confidence < 30:
                    st.markdown(
                        '<div class="low-confidence-warning">⚠️ <strong>Düşük güven skoru</strong> — Model bu e-posta hakkında emin değil. Sonucu dikkatli değerlendirin.</div>',
                        unsafe_allow_html=True,
                    )

                col1, col2 = st.columns(2)
                with col1:
                    val_class = "phishing-yes" if is_phishing else "phishing-no"
                    st.markdown(f'<div class="metric-card"><div class="metric-label">Karar</div><div class="metric-value {val_class}">{label}</div></div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="metric-card"><div class="metric-label">Model Olasılığı</div><div class="metric-value neutral">%{phish_prob:.1f}</div></div>', unsafe_allow_html=True)
                with col2:
                    st.markdown(f'<div class="metric-card"><div class="metric-label">Güven Skoru</div><div class="metric-value neutral">%{confidence:.1f}</div></div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="metric-card"><div class="metric-label">Anahtar Kelime Skoru</div><div class="metric-value neutral">%{keyword_score:.1f}</div></div>', unsafe_allow_html=True)

                # ── Gauge Grafik ─────────────────────────────────────────────
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
                        "bar": {"color": gauge_color, "thickness": 0.25},
                        "bgcolor": "#1e1e2e",
                        "bordercolor": "#313244",
                        "steps": [
                            {"range": [0, PHISHING_THRESHOLD], "color": "#0d2b1e"},
                            {"range": [PHISHING_THRESHOLD, 100], "color": "#3b1219"},
                        ],
                        "threshold": {
                            "line": {"color": "#f9e2af", "width": 3},
                            "thickness": 0.75,
                            "value": PHISHING_THRESHOLD,
                        },
                    }
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
                    unsafe_allow_html=True
                )

                # ── Keyword tagları ──────────────────────────────────────────
                st.markdown("<div style='margin-top:20px;'>", unsafe_allow_html=True)
                if keywords:
                    st.markdown("<div class='metric-label' style='margin-bottom:6px;'>🔑 Tespit Edilen Şüpheli Kelimeler</div>", unsafe_allow_html=True)
                    tags_html = "".join(f'<span class="keyword-tag">{kw}</span>' for kw in keywords)
                    st.markdown(tags_html, unsafe_allow_html=True)
                else:
                    st.markdown("<div style='color:#6c7086; font-size:13px;'>Belirgin şüpheli kelime bulunamadı.</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            except FileNotFoundError as error:
                st.error(f"❌ {error}")

# ══════════════════════════════════════════════════════════
# SEKME 2 — Model Performansı
# ══════════════════════════════════════════════════════════
with tab2:
    st.markdown("## 📊 Model Performans Raporu")
    st.markdown("<p style='color:#6c7086; font-size:14px;'>Eğitim sırasında kaydedilen test verisi metrikleri.</p>", unsafe_allow_html=True)
    st.divider()

    def load_performance_data():
        project_root    = Path(__file__).resolve().parents[1]
        results_path    = project_root / "models" / "test_results.pkl"

        if not results_path.exists():
            raise FileNotFoundError(
                "Test sonuçları bulunamadı. Önce `python src/train_model.py` çalıştırın."
            )

        with open(results_path, "rb") as f:
            r = pickle.load(f)

        return r["y_test"], r["y_pred"], r["y_prob"], r.get("dataset_size", 0), r.get("test_size", 0)

    try:
        y_test, y_pred, y_prob, dataset_size, test_size = load_performance_data()

        cm = confusion_matrix(y_test, y_pred, labels=[0, 1])
        tn, fp, fn, tp = cm.ravel()

        accuracy  = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall    = recall_score(y_test, y_pred, zero_division=0)
        f1        = f1_score(y_test, y_pred, zero_division=0)

        # ── Metrik kartları ───────────────────────────────────────────────────
        c1, c2, c3, c4 = st.columns(4)
        for col, lbl, value in [
            (c1, "Accuracy",  accuracy),
            (c2, "Precision", precision),
            (c3, "Recall",    recall),
            (c4, "F1 Score",  f1),
        ]:
            with col:
                st.markdown(f"""
                <div class="perf-card">
                    <div class="perf-value">%{value*100:.1f}</div>
                    <div class="perf-label">{lbl}</div>
                </div>
                """, unsafe_allow_html=True)

        if dataset_size:
            st.markdown(
                f"<div style='font-family:JetBrains Mono; font-size:12px; color:#6c7086; margin:8px 0 16px;'>"
                f"Toplam dataset: <strong style='color:#cdd6f4'>{dataset_size:,}</strong> e-posta &nbsp;·&nbsp; "
                f"Grafikler: <strong style='color:#cdd6f4'>{test_size:,}</strong> e-posta"
                f"</div>",
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

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
            fpr, tpr, _ = roc_curve(y_test, y_prob)
            roc_auc = auc(fpr, tpr)

            fig_roc = go.Figure()
            fig_roc.add_trace(go.Scatter(
                x=fpr, y=tpr,
                mode="lines",
                name=f"ROC (AUC = {roc_auc:.3f})",
                line=dict(color="#89b4fa", width=2),
                fill="tozeroy",
                fillcolor="rgba(137,180,250,0.1)",
            ))
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
                yaxis=dict(title="True Positive Rate", gridcolor="#313244", color="#6c7086"),
                legend=dict(bgcolor="#1e1e2e", bordercolor="#313244"),
                margin=dict(l=10, r=10, t=10, b=10),
                height=300,
            )
            st.plotly_chart(fig_roc, use_container_width=True)
            st.markdown(f"""
            <div style="font-family: JetBrains Mono; font-size:13px; color:#6c7086; margin-top:8px;">
                AUC = <span style="color:#89b4fa">{roc_auc:.4f}</span> &nbsp;·&nbsp;
                1.0'e ne kadar yakınsa model o kadar iyi.
            </div>
            """, unsafe_allow_html=True)

        # ── Olasılık Dağılımı ─────────────────────────────────────────────────
        st.markdown("### 🎯 Phishing Olasılığı Dağılımı")

        phish_probs  = y_prob[y_test == 1]
        normal_probs = y_prob[y_test == 0]

        fig_dist = go.Figure()
        fig_dist.add_trace(go.Histogram(
            x=phish_probs, name="Phishing",
            marker_color="#f38ba8", opacity=0.7, nbinsx=40,
        ))
        fig_dist.add_trace(go.Histogram(
            x=normal_probs, name="Normal",
            marker_color="#a6e3a1", opacity=0.7, nbinsx=40,
        ))
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
            yaxis=dict(title="E-posta Sayısı", gridcolor="#313244", color="#6c7086"),
            legend=dict(bgcolor="#1e1e2e", bordercolor="#313244"),
            margin=dict(l=10, r=10, t=10, b=10),
            height=300,
        )
        st.plotly_chart(fig_dist, use_container_width=True)

    except FileNotFoundError:
        st.error("❌ Model bulunamadı. Önce `python src/train_model.py` çalıştırın.")
    except Exception as e:
        st.error(f"❌ Hata: {e}")