import os
import pickle
from pathlib import Path

import numpy as np
import tensorflow as tf

keras = tf.keras

GENDER_LABELS = {0: "Male", 1: "Female"}
AGE_GROUP_LABELS = {
    0: "Young skin (0–18)",
    1: "Early aging (19–45)",
    2: "Mature skin (46+)",
}

SKIN_LABELS = ["redness", "acne", "pigmentation", "wrinkles", "normal_skin"]

class FacePredictor:
    def __init__(
        self,
        *,
        skin_model_path=None,
        skin_img_size=(224, 224),
    ):
        base_dir = Path(__file__).resolve().parent

        age_path = base_dir / "age_classifier_model.pkl"
        gender_path = base_dir / "gender_classifier_model.pkl"
        self.age_model = None
        self.gender_model = None
        if age_path.exists():
            with age_path.open("rb") as f:
                self.age_model = pickle.load(f)
        if gender_path.exists():
            with gender_path.open("rb") as f:
                self.gender_model = pickle.load(f)

        self.skin_img_size = skin_img_size

        if skin_model_path is None:
            skin_model_path = base_dir / "resnet50_5labels.keras"
        self.skin_model_path = Path(skin_model_path)

        self.skin_model = keras.models.load_model(self.skin_model_path)

        self._resnet_embedder = keras.applications.ResNet50(
            weights="imagenet",
            include_top=False,
            pooling="avg",
            input_shape=(224, 224, 3),
        )
        self._resnet_embedder.trainable = False

    def _extract_embedding(self, img):
        preprocess_input = keras.applications.resnet50.preprocess_input
        arr = keras.utils.img_to_array(img.resize((224, 224)))
        arr = np.expand_dims(arr, axis=0)
        arr = preprocess_input(arr)
        emb = self._resnet_embedder(arr, training=False).numpy()[0]
        return emb

    def _prepare_skin_input(self, img):
        preprocess_input = keras.applications.resnet50.preprocess_input

        resized = img.resize(self.skin_img_size)
        arr = keras.utils.img_to_array(resized).astype(np.float32)
        arr = preprocess_input(arr)
        arr = np.expand_dims(arr, axis=0)
        return arr

    def predict(self, img):
        x = self._prepare_skin_input(img)
        probs = self.skin_model.predict(x, verbose=0)[0]
        return np.asarray(probs, dtype=np.float32)

    def predict_demographics(self, img):
        emb = self._extract_embedding(img).reshape(1, -1)
        age_group_id = int(self.age_model.predict(emb)[0])
        gender_id = int(self.gender_model.predict(emb)[0])
        return {
            "age_group": AGE_GROUP_LABELS.get(age_group_id, str(age_group_id)),
            "age_group_id": age_group_id,
            "gender": GENDER_LABELS.get(gender_id, str(gender_id)),
            "gender_id": gender_id,
        }