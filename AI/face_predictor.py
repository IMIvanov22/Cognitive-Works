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
ACNE_SEVERITY_LABELS = {
    0: "Low (0-1)",
    1: "High (2-3)",
}


class FacePredictor:
    def __init__(self):
        base_dir = os.path.dirname(__file__)

        with open(os.path.join(base_dir, "age_classifier_model.pkl"), "rb") as f:
            self.age_model = pickle.load(f)
        with open(os.path.join(base_dir, "gender_classifier_model.pkl"), "rb") as f:
            self.gender_model = pickle.load(f)
        with open(os.path.join(base_dir, "acne_classifier_model.pkl"), "rb") as f:
            self.acne_model = pickle.load(f)

        self._ResNet = ResNet50(
            weights="imagenet",
            include_top=False,
            pooling="avg",
            input_shape=(224, 224, 3),
        )
        self._ResNet.trainable = False

    def _extract_embedding(self, img):
        img = img.resize((224, 224))
        img = img_to_array(img)
        img = np.expand_dims(img, axis=0)
        img = preprocess_input(img)
        emb = self._ResNet(img, training=False).numpy()[0]
        return emb

    def predict(self, img):
        emb = self._extract_embedding(img).reshape(1, -1)

        age_group_id = int(self.age_model.predict(emb)[0])
        gender_id = int(self.gender_model.predict(emb)[0])
        acne_severity_id = int(self.acne_model.predict(emb)[0])

        return {
            "age_group": AGE_GROUP_LABELS.get(age_group_id, str(age_group_id)),
            "age_group_id": age_group_id,
            "gender": GENDER_LABELS[gender_id],
            "gender_id": gender_id,
            "acne_severity": ACNE_SEVERITY_LABELS.get(acne_severity_id, str(acne_severity_id)),
            "acne_severity_id": acne_severity_id,
        }