import numpy as np
import pickle
import tensorflow as tf
from tensorflow.keras.models import load_model, Model
from tensorflow.keras.preprocessing import image
import os

# ── Load models once at import ──────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

_palm_model   = None
_feature_model = None
_kmeans        = None
_scaler        = None
_class_names   = None   # dict: {class_folder_name: index}


def _load_all():
    global _palm_model, _feature_model, _kmeans, _scaler, _class_names

    _palm_model = load_model(os.path.join(BASE_DIR, "palm_model.h5"))

    _feature_model = Model(
        inputs  = _palm_model.layers[0].input,
        outputs = _palm_model.get_layer("feature_layer").output,
    )

    with open(os.path.join(BASE_DIR, "kmeans_model.pkl"), "rb") as f:
        _kmeans = pickle.load(f)

    with open(os.path.join(BASE_DIR, "scaler.pkl"), "rb") as f:
        _scaler = pickle.load(f)

    with open(os.path.join(BASE_DIR, "class_names.pkl"), "rb") as f:
        _class_names = pickle.load(f)   # e.g. {"left": 0, "right": 1, "both": 2}


# ── Cluster → destiny mapping ────────────────────────────────────────────────
DESTINY_MAP = {
    0:  {
        "name": "Người Tiên Phong",
        "title": "Nhà Khám Phá",
        "desc": "Bàn tay bạn mang dấu ấn của người khai mở con đường mới. Đường sinh mệnh sâu và dài – ý chí mạnh mẽ, không ngại thử thách.",
        "element": "🔥 Hỏa",
        "lucky": "Đỏ · Cam · 3 · 7",
        "icon": "🌋",
    },
    1:  {
        "name": "Người Nghệ Sĩ",
        "title": "Tâm Hồn Sáng Tạo",
        "desc": "Đường trí tuệ cong nhẹ về phía mặt trăng – bạn có tư duy nghệ thuật và trực giác nhạy bén hiếm có.",
        "element": "🌊 Thủy",
        "lucky": "Xanh dương · Bạc · 2 · 6",
        "icon": "🎨",
    },
    2:  {
        "name": "Nhà Lãnh Đạo",
        "title": "Bàn Tay Quyền Lực",
        "desc": "Ngón tay dài và thẳng, đường số phận nổi bật – thiên mệnh dẫn dắt người khác đã được khắc vào lòng bàn tay.",
        "element": "⚡ Lôi",
        "lucky": "Vàng · Tím hoàng gia · 1 · 8",
        "icon": "👑",
    },
    3:  {
        "name": "Người Chữa Lành",
        "title": "Trái Tim Nhân Ái",
        "desc": "Đường tình cảm sâu và đều – bạn sinh ra để mang lại sự chữa lành và bình an cho những người xung quanh.",
        "element": "🌿 Mộc",
        "lucky": "Xanh lá · Hồng · 4 · 9",
        "icon": "💚",
    },
    4:  {
        "name": "Nhà Tư Tưởng",
        "title": "Trí Tuệ Thâm Sâu",
        "desc": "Đường trí tuệ thẳng và rõ nét – bạn sở hữu khả năng phân tích và tư duy logic phi thường.",
        "element": "🌀 Phong",
        "lucky": "Xám · Nâu · 5 · 11",
        "icon": "🧠",
    },
    5:  {
        "name": "Người Bảo Vệ",
        "title": "Thành Lũy Kiên Cường",
        "desc": "Cấu trúc bàn tay vững chắc, gò Kim Tinh nổi cao – bạn là chỗ dựa vững chắc cho gia đình và bạn bè.",
        "element": "🪨 Thổ",
        "lucky": "Nâu đất · Trắng · 6 · 10",
        "icon": "🛡️",
    },
    6:  {
        "name": "Người Mơ Mộng",
        "title": "Thế Giới Nội Tâm",
        "desc": "Gò Mặt Trăng phát triển mạnh – trí tưởng tượng phong phú, tâm linh nhạy cảm, thường thấy trước tương lai.",
        "element": "🌙 Nguyệt",
        "lucky": "Trắng · Bạc · 7 · 12",
        "icon": "🌙",
    },
    7:  {
        "name": "Người Hành Động",
        "title": "Năng Lượng Bất Tận",
        "desc": "Bàn tay rộng và dày, các đường tay sắc nét – bạn là người của hành động, không ngừng xây dựng và tạo ra.",
        "element": "🔥 Hỏa",
        "lucky": "Đỏ tươi · Đen · 1 · 5",
        "icon": "⚡",
    },
    8:  {
        "name": "Nhà Ngoại Giao",
        "title": "Cầu Nối Nhân Tâm",
        "desc": "Nhiều đường nhánh trên đường tình cảm – kỹ năng giao tiếp xuất chúng, dễ tạo sự đồng cảm với mọi người.",
        "element": "🌊 Thủy",
        "lucky": "Xanh ngọc · Vàng nhạt · 3 · 8",
        "icon": "🤝",
    },
    9:  {
        "name": "Người Tự Do",
        "title": "Linh Hồn Phóng Khoáng",
        "desc": "Đường sinh mệnh cong rộng ra ngoài – tinh thần phiêu lưu, không bị ràng buộc, luôn tìm kiếm chân trời mới.",
        "element": "🌀 Phong",
        "lucky": "Xanh dương · Trắng · 9 · 14",
        "icon": "🦅",
    },
    10: {
        "name": "Nhà Chiến Lược",
        "title": "Bậc Thầy Kế Hoạch",
        "desc": "Gò Sao Thổ cao và rõ – kiên nhẫn, chu đáo, luôn nghĩ xa trông rộng trước khi bước đi.",
        "element": "🪨 Thổ",
        "lucky": "Đen · Xanh lam · 8 · 13",
        "icon": "♟️",
    },
    11: {
        "name": "Người Yêu Thương",
        "title": "Trái Tim Nồng Hậu",
        "desc": "Đường tình cảm dài và cong – tình yêu vô điều kiện, lòng trắc ẩn sâu sắc là đặc trưng lớn nhất của bạn.",
        "element": "🌿 Mộc",
        "lucky": "Hồng · Đỏ · 2 · 6",
        "icon": "❤️",
    },
    12: {
        "name": "Nhà Tiên Tri",
        "title": "Giác Quan Thứ Sáu",
        "desc": "Nhiều đường chỉ tay nhỏ trên gò Mặt Trăng – trực giác cực nhạy, đôi khi cảm nhận được những điều người khác không thấy.",
        "element": "🌙 Nguyệt",
        "lucky": "Tím · Bạc · 11 · 22",
        "icon": "🔮",
    },
    13: {
        "name": "Người Thực Tế",
        "title": "Đôi Tay Xây Dựng",
        "desc": "Đường số phận thẳng đứng và sâu – bạn cần sự ổn định, giỏi quản lý tài chính và xây dựng nền tảng vững chắc.",
        "element": "🪨 Thổ",
        "lucky": "Nâu · Xanh lá · 4 · 8",
        "icon": "🏗️",
    },
    14: {
        "name": "Nhà Triết Học",
        "title": "Tìm Kiếm Ý Nghĩa",
        "desc": "Đường trí tuệ kéo dài về phía gò Mặt Trăng – bạn không ngừng tìm kiếm ý nghĩa sâu xa đằng sau mọi sự vật.",
        "element": "🌀 Phong",
        "lucky": "Tím đậm · Xám · 7 · 11",
        "icon": "📜",
    },
    15: {
        "name": "Người Cân Bằng",
        "title": "Trung Dung Hoàn Hảo",
        "desc": "Các đường tay cân đối và hài hòa – bạn có khả năng cân bằng mọi mặt của cuộc sống một cách tự nhiên.",
        "element": "⭐ Ngũ Hành",
        "lucky": "Vàng · Xanh · 5 · 10",
        "icon": "☯️",
    },
}

CLASS_LABEL_MAP = {
    # Flip key/value from class_indices (folder_name → index becomes index → label)
    # We do this dynamically after loading
}

PALM_TYPE_DESC = {
    "left":  ("Bàn Tay Trái", "Tiềm năng thiên bẩm – những gì bạn được sinh ra với"),
    "right": ("Bàn Tay Phải", "Vận mệnh tạo ra – những gì bạn đã xây dựng"),
    "both":  ("Cả Hai Tay",   "Hội tụ thiên mệnh và nỗ lực"),
}


# ── Public API ────────────────────────────────────────────────────────────────
def predict(img_path: str) -> dict:
    """
    Returns a dict with:
      - palm_type: str
      - palm_type_desc: (str, str)
      - confidence: float  (0-100)
      - cluster_id: int
      - destiny: dict  (from DESTINY_MAP)
    """
    global _palm_model, _feature_model, _kmeans, _scaler, _class_names

    if _palm_model is None:
        _load_all()

    # Pre-process image
    img = image.load_img(img_path, target_size=(224, 224))
    arr = image.img_to_array(img) / 255.0
    arr = np.expand_dims(arr, axis=0)

    # Classification
    preds = _palm_model.predict(arr, verbose=0)[0]
    class_idx = int(np.argmax(preds))
    confidence = float(np.max(preds)) * 100

    # Reverse class_indices → name
    idx_to_name = {v: k for k, v in _class_names.items()}
    raw_label = idx_to_name.get(class_idx, "unknown")
    palm_type_info = PALM_TYPE_DESC.get(raw_label, (raw_label.title(), ""))

    # Feature extraction + clustering
    features = _feature_model.predict(arr, verbose=0)
    features = features.reshape(1, -1)
    scaled   = _scaler.transform(features)
    cluster_id = int(_kmeans.predict(scaled)[0])

    return {
        "palm_type":      raw_label,
        "palm_type_label": palm_type_info[0],
        "palm_type_desc": palm_type_info[1],
        "confidence":     round(confidence, 1),
        "cluster_id":     cluster_id,
        "destiny":        DESTINY_MAP[cluster_id],
    }
