from pathlib import Path
import pickle

import shap
from scipy.sparse import csr_matrix

try:
    from src.text_utils import advanced_preprocessing
except ModuleNotFoundError:
    from text_utils import advanced_preprocessing


def load_model_and_vectorizer() -> tuple[object, object]:
    """Kaydedilen model ve TF-IDF vectorizer nesnelerini models klasöründen yükler."""
    project_root = Path(__file__).resolve().parents[1]
    model_path = project_root / "models" / "phishing_model.pkl"

    if not model_path.exists():
        raise FileNotFoundError(
            f"Model bulunamadi: {model_path}. Once src/train_model.py dosyasini calistirin."
        )

    with open(model_path, "rb") as file:
        saved_objects = pickle.load(file)

    return saved_objects["model"], saved_objects["vectorizer"]


def get_top_words(shap_values: object, feature_names: object, top_n: int = 10) -> list[tuple[str, float]]:
    """SHAP değerlerine göre kararda en etkili kelimeleri bulur."""
    word_scores: list[tuple[str, float]] = []

    for index, score in enumerate(shap_values.values[0]):
        if score != 0:
            word_scores.append((feature_names[index], float(score)))

    word_scores.sort(key=lambda item: abs(item[1]), reverse=True)
    return word_scores[:top_n]


def get_shap_explanation(
    text: str, model: object, vectorizer: object, top_n: int = 12
) -> list[tuple[str, float]]:
    """Verilen metin için SHAP değerlerini hesaplar.

    Pozitif değer → phishing yönünde etkili
    Negatif değer → normal yönünde etkili
    """
    clean_text = advanced_preprocessing(text)
    text_vector = vectorizer.transform([clean_text])
    background = csr_matrix((1, text_vector.shape[1]))

    explainer = shap.LinearExplainer(model, background)
    shap_values = explainer(text_vector)

    feature_names = vectorizer.get_feature_names_out()
    return get_top_words(shap_values, feature_names, top_n)


def get_lime_explanation(
    text: str, model: object, vectorizer: object, top_n: int = 12
) -> list[tuple[str, float]]:
    """LIME kullanarak modelin kararını kelime bazında açıklar.

    Pozitif değer → phishing yönünde etkili
    Negatif değer → normal yönünde etkili
    """
    from lime.lime_text import LimeTextExplainer

    def predict_proba(texts: list[str]) -> object:
        vectors = vectorizer.transform([advanced_preprocessing(t) for t in texts])
        return model.predict_proba(vectors)

    explainer = LimeTextExplainer(class_names=["Normal", "Phishing"])
    explanation = explainer.explain_instance(
        text, predict_proba, num_features=top_n, num_samples=300
    )
    return explanation.as_list(label=1)


def get_transformer_lime_explanation(
    text: str,
    top_n: int = 12,
) -> list[tuple[str, float]]:
    """Transformer modeli için LIME açıklaması üretir (black-box yaklaşım).

    Transformer modeli eğitilmemişse boş liste döndürür.
    Pozitif değer → phishing yönünde etkili
    Negatif değer → normal yönünde etkili
    """
    try:
        import src.transformer_predictor as _tr
    except ModuleNotFoundError:
        import transformer_predictor as _tr  # type: ignore

    if not _tr.is_available():
        return []

    try:
        from lime.lime_text import LimeTextExplainer
    except ImportError:
        return []

    def predict_proba(texts: list[str]) -> object:
        import numpy as np
        probs = []
        for t in texts:
            p = _tr.predict(t)
            phish = (p / 100.0) if p is not None else 0.5
            probs.append([1.0 - phish, phish])
        return np.array(probs)

    explainer = LimeTextExplainer(class_names=["Normal", "Phishing"])
    try:
        explanation = explainer.explain_instance(
            text, predict_proba, num_features=top_n, num_samples=200
        )
        return explanation.as_list(label=1)
    except Exception:
        return []


def main() -> None:
    """Örnek bir e-posta metni için SHAP ve LIME açıklamalarını ekrana yazar."""
    sample_email = "Urgent! Verify your account now. Click the link and login to update your password."

    model, vectorizer = load_model_and_vectorizer()

    print("=== SHAP Açıklaması (TF-IDF+LR) ===")
    shap_words = get_shap_explanation(sample_email, model, vectorizer)
    for word, score in shap_words:
        direction = "→ PHISHİNG" if score > 0 else "→ NORMAL"
        print(f"  {word}: {score:.4f}  {direction}")

    print("\n=== LIME Açıklaması (TF-IDF+LR) ===")
    try:
        lime_words = get_lime_explanation(sample_email, model, vectorizer)
        for word, score in lime_words:
            direction = "→ PHISHİNG" if score > 0 else "→ NORMAL"
            print(f"  {word}: {score:.4f}  {direction}")
    except ImportError:
        print("  LIME kurulu değil: pip install lime")

    print("\n=== LIME Açıklaması (Transformer) ===")
    tr_words = get_transformer_lime_explanation(sample_email)
    if tr_words:
        for word, score in tr_words:
            direction = "→ PHISHİNG" if score > 0 else "→ NORMAL"
            print(f"  {word}: {score:.4f}  {direction}")
    else:
        print("  Transformer modeli eğitilmemiş veya LIME kurulu değil.")


if __name__ == "__main__":
    main()
