import streamlit as st

from src.predict import predict_details
from src.text_utils import build_email_text


def analyze_email(subject: str, body: str = "") -> dict:
    """Subject ve body alanlarini birlestirir, tahmin yapar ve aciklama hazirlar."""
    text = build_email_text(subject, body)
    result = predict_details(text)
    matched_keywords = result["matched_keywords"]

    if matched_keywords:
        explanation = "Bu e-posta su supheli kelimeleri iceriyor: " + ", ".join(matched_keywords)
    else:
        explanation = "Bu e-postada belirgin phishing kelimeleri bulunmadi."

    result["explanation"] = explanation
    return result


def main() -> None:
    """Streamlit arayüzünü oluşturur ve kullanıcıdan gelen e-postayı analiz eder."""
    st.set_page_config(page_title="Phishing Email Dashboard", page_icon="📧", layout="centered")

    st.title("Phishing E-posta Analizi")
    st.write("Body alani zorunluya yakin ana girdidir. Subject varsa ekleyebilirsiniz.")

    subject = st.text_input(
        "Subject",
        placeholder="Opsiyonel: Verify Your Bank Account",
    )
    body = st.text_area(
        "Body",
        height=220,
        placeholder="Ornek: Dear user, verify your account now by clicking the secure login link.",
    )

    if st.button("Analiz Et", use_container_width=True):
        if not body.strip() and not subject.strip():
            st.warning("Lutfen analiz icin en azindan body veya subject girin.")
            return

        try:
            result = analyze_email(subject, body)

            st.subheader("Sonuc")
            st.write(f"Phishing: {result['label']}")
            st.write(f"Confidence: %{result['confidence']:.2f}")
            st.write(f"Risk Score: {result['risk_score']:.2f}")
            st.write(f"Phishing Probability: %{result['phishing_probability']:.2f}")
            st.write(f"Keyword Score: %{result['keyword_score']:.2f}")
            st.info(result["explanation"])
        except FileNotFoundError as error:
            st.error(str(error))


if __name__ == "__main__":
    main()