import pickle
import os
import numpy as np
from tensorflow.keras.utils import img_to_array
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.applications import ResNet50

GENDER_LABELS = {0: "Male", 1: "Female"}
RACE_LABELS = {0: "White", 1: "Black", 2: "Asian", 3: "Indian", 4: "Other"}
AGE_GROUP_LABELS = {
    0: "Young skin (0–18)",
    1: "Early aging (19–45)",
    2: "Mature skin (46+)",
}


class FacePredictor:
    """Predicts age, gender, and race from a face image using ResNet50
    embeddings and XGBoost models trained on the UTKFace dataset."""

    def __init__(self):
        base_dir = os.path.dirname(__file__)

        with open(os.path.join(base_dir, "age_model.pkl"), "rb") as f:
            self.age_model = pickle.load(f)
        with open(os.path.join(base_dir, "gender_model.pkl"), "rb") as f:
            self.gender_model = pickle.load(f)
        with open(os.path.join(base_dir, "race_model.pkl"), "rb") as f:
            self.race_model = pickle.load(f)

        self._ResNet = ResNet50(
            weights="imagenet",
            include_top=False,
            pooling="avg",
            input_shape=(224, 224, 3),
        )
        self._ResNet.trainable = False

    def _extract_embedding(self, img):
        """Extract a ResNet50 embedding from a PIL Image."""
        img = img.resize((224, 224))
        img = img_to_array(img)
        img = np.expand_dims(img, axis=0)
        img = preprocess_input(img)
        emb = self._ResNet(img, training=False).numpy()[0]
        return emb

    def predict(self, img):
        """Return a dict with predicted age, gender, and race."""
        emb = self._extract_embedding(img).reshape(1, -1)

        age_group_id = int(self.age_model.predict(emb)[0])
        gender_id = int(self.gender_model.predict(emb)[0])
        race_id = int(self.race_model.predict(emb)[0])

        return {
            "age_group": AGE_GROUP_LABELS.get(age_group_id, str(age_group_id)),
            "age_group_id": age_group_id,
            "gender": GENDER_LABELS[gender_id],
            "gender_id": gender_id,
            "race": RACE_LABELS[race_id],
            "race_id": race_id,
        }