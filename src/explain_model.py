from pathlib import Path
import pickle

import shap
from scipy.sparse import csr_matrix

try:
    from src.text_utils import preprocessing
except ModuleNotFoundError:
    from text_utils import preprocessing


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


def main() -> None:
    """Ornek bir e-posta metni icin SHAP kullanarak en etkili kelimeleri ekrana yazar."""
    sample_email = "Urgent! Verify your account now. Click the link and login to update your password."

    # Egitilmiş modeli ve TF-IDF vectorizer'i yükle.
    model, vectorizer = load_model_and_vectorizer()

    # Ornek metni temizle ve TF-IDF ile dönüştür.
    clean_text = preprocessing(sample_email)
    text_vector = vectorizer.transform([clean_text])

    # SHAP için boş bir arka plan vektörü oluştur.
    background = csr_matrix((1, text_vector.shape[1]))

    # Model kararını hangi kelimelerin etkilediğini hesapla.
    explainer = shap.LinearExplainer(model, background)
    shap_values = explainer(text_vector)

    # En etkili kelimeleri al.
    feature_names = vectorizer.get_feature_names_out()
    top_words = get_top_words(shap_values, feature_names)

    print("En onemli kelimeler:")
    for word, score in top_words:
        print(f"- {word}: {score:.4f}")


if __name__ == "__main__":
    main()