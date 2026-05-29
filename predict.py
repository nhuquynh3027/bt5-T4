import os
import numpy as np
import pickle
import tensorflow as tf
from tensorflow.keras.models import load_model, Model
from tensorflow.keras.preprocessing import image

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

def load_all_assets():
    print("Đang tải các mô hình và file cấu hình...")
    
    model_path = 'palm_model.h5' 
    full_model = load_model(model_path, compile=False)
    
    feature_extractor = Model(
        inputs=full_model.inputs,
        outputs=full_model.get_layer('feature_layer').output
    )
    
    with open('class_names.pkl', 'rb') as f:
        class_indices = pickle.load(f)
        class_names = {v: k for k, v in class_indices.items()}
        
    with open('scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)
        
    with open('kmeans_model.pkl', 'rb') as f:
        kmeans_model = pickle.load(f)
        
    print("Tải hoàn tất!\n")
    return full_model, feature_extractor, class_names, scaler, kmeans_model

Fortune_telling = {
    0: "Học tập: Bạn sở hữu trực giác sắc bén, tiếp thu kiến thức rất nhanh, nhưng cần rèn luyện tính kỷ luật để đạt kết quả xuất sắc. Sức khỏe: Thể trạng ổn định, tuy nhiên đừng bỏ bê việc nghỉ ngơi. Tình duyên: Những rung động nhẹ nhàng đang đến, hãy để trái tim dẫn lối và người ấy sẽ nhận ra sự chân thành từ bạn.",
    1: "Học tập: Con đường học vấn đang rộng mở, sự kiên trì bền bỉ chính là chìa khóa giúp bạn chinh phục mọi đỉnh cao. Sức khỏe: Hệ tiêu hóa hơi nhạy cảm, bạn nên ưu tiên chế độ ăn uống thanh đạm. Tình duyên: Một mối quan hệ dựa trên sự tin tưởng và thấu hiểu sẽ là điểm tựa tinh thần vững chắc cho bạn trong thời gian tới.",
    2: "Học tập: Bạn thường xuyên có những ý tưởng bay bổng, hãy cân bằng lại với thực tế để đạt hiệu quả cao nhất trong công việc. Sức khỏe: Đôi mắt cần được chăm sóc, tránh nhìn màn hình quá lâu. Tình duyên: Những tín hiệu tích cực đang đến gần, một người mới sẽ chủ động tiến về phía bạn với tâm thế chân thành.",
    3: "Học tập: Tố chất lãnh đạo tiềm ẩn giúp bạn luôn tỏa sáng khi làm việc nhóm, hãy tự tin thể hiện bản thân. Sức khỏe: Cần chú ý đến các khớp xương và duy trì vận động nhẹ nhàng mỗi ngày. Tình duyên: Tình yêu lúc này đòi hỏi sự kiên nhẫn và niềm tin tuyệt đối, đừng để những hiểu lầm nhỏ làm lung lay tình cảm.",
    4: "Học tập: Tư duy sáng tạo và tâm hồn nghệ sĩ giúp bạn rất hợp với các lĩnh vực nhân văn, nghệ thuật. Sức khỏe: Tinh thần minh mẫn, vẻ ngoài tràn đầy sức sống. Tình duyên: Dẫu đường tình đôi lúc có chút chông chênh, nhưng kết quả cuối cùng sẽ vô cùng ngọt ngào và đáng giá.",
    5: "Học tập: Bạn đang chịu khá nhiều áp lực, hãy học cách thả lỏng để não bộ làm việc hiệu quả hơn. Sức khỏe: Cần bổ sung dưỡng chất và tuân thủ giờ giấc nghỉ ngơi khoa học. Tình duyên: Đừng quá khép kín, việc mở lòng và đón nhận những người bạn mới sẽ mang đến cho bạn cơ hội bất ngờ.",
    6: "Học tập: Trí nhớ của bạn là một tài sản quý giá, hãy tận dụng nó để chinh phục những kiến thức khó. Sức khỏe: Chú ý theo dõi huyết áp và tránh xa những thực phẩm quá mặn. Tình duyên: Một cuộc gặp gỡ bất ngờ từ quá khứ sẽ gợi lại những kỷ niệm đẹp hoặc mang đến cơ hội hàn gắn thú vị.",
    7: "Học tập: Sự chọn lọc tinh tế giúp bạn không bị quá tải trong biển kiến thức mênh mông. Sức khỏe: Sức đề kháng tốt, cơ thể ít khi gặp phải những cơn ốm vặt. Tình duyên: Hai tâm hồn đồng điệu đang tìm đến nhau, đây là thời điểm vàng để vun đắp tình cảm bền lâu.",
    8: "Học tập: Sự nghiệp học hành đang thăng tiến vượt bậc như diều gặp gió, hãy tận dụng đà này để phát triển bản thân. Sức khỏe: Việc duy trì thói quen tập luyện sẽ giúp cơ thể thêm dẻo dai. Tình duyên: Mối quan hệ tiến triển theo chiều hướng chậm mà chắc, bền vững và đầy sự trân trọng.",
    9: "Học tập: Bạn dễ bị xao nhãng bởi các yếu tố bên ngoài, sự tập trung cao độ sẽ giúp bạn làm nên chuyện lớn. Sức khỏe: Cần kiểm soát căng thẳng và tìm đến những thú vui lành mạnh. Tình duyên: Hãy kiên nhẫn, người xứng đáng nhất sẽ xuất hiện đúng thời điểm bạn sẵn sàng nhất.",
    10: "Học tập: Có quý nhân phù trợ trong con đường học vấn, mọi trở ngại sẽ sớm được hóa giải nếu bạn quyết tâm. Sức khỏe: Trạng thái cơ thể rất tốt, chỉ cần duy trì lối sống điều độ là ổn. Tình duyên: Bạn rất có sức hút, nên cẩn thận kẻo sự đa sầu đa cảm khiến bạn khó đưa ra quyết định.",
    11: "Học tập: Nỗ lực gấp đôi so với hiện tại sẽ mang lại kết quả vượt ngoài mong đợi, đừng bỏ cuộc nhé. Sức khỏe: Chú ý đến đường hô hấp, tránh tiếp xúc nơi ô nhiễm. Tình duyên: Một chuyện tình yêu đẹp đòi hỏi sự thành thật và vun vén từ cả hai phía, hãy luôn chân thành.",
    12: "Học tập: Bạn có năng khiếu đặc biệt với các con số hoặc kỹ thuật, hãy khai thác thế mạnh này. Sức khỏe: Đừng quên vận động vai gáy và lưng sau nhiều giờ làm việc. Tình duyên: Người yêu bạn rất tinh tế, họ luôn biết cách làm cho bạn cảm thấy đặc biệt mỗi ngày.",
    13: "Học tập: Những ý tưởng độc đáo của bạn rất cần được chia sẻ, đừng ngần ngại bày tỏ quan điểm cá nhân. Sức khỏe: Cung cấp đủ nước cho cơ thể mỗi ngày là chìa khóa của sự tỉnh táo. Tình duyên: Tuần này là cơ hội tốt để kết nối với một người cực kỳ hợp cạ với bạn.",
    14: "Học tập: Kiên trì là phẩm chất vàng, chỉ cần không nản chí bạn chắc chắn sẽ thành công. Sức khỏe: Cơ thể đang trong giai đoạn hồi phục và tràn đầy năng lượng. Tình duyên: Những tranh cãi nhỏ chỉ là gia vị của tình yêu, chủ yếu do hiểu lầm, hãy ngồi xuống nói chuyện thẳng thắn.",
    15: "Học tập: Tài năng thiên bẩm giúp bạn đạt được thành công sớm hơn dự định, hãy giữ vững phong độ. Sức khỏe: Bạn đang sở hữu nguồn năng lượng dồi dào. Tình duyên: Người ấy coi bạn như món quà quý giá, hãy trân trọng và tận hưởng hạnh phúc này."
}
def predict_palmistry(img_path, assets):
    full_model, feature_extractor, class_names, scaler, kmeans_model = assets
    
    target_size = (224, 224)
    img = image.load_img(img_path, target_size=target_size)
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0 
    
    class_preds = full_model.predict(img_array, verbose=0)
    predicted_class_idx = np.argmax(class_preds[0])
    confidence = np.max(class_preds[0]) * 100
    hand_type = class_names[predicted_class_idx]
    
    raw_features = feature_extractor.predict(img_array, verbose=0)
    scaled_features = scaler.transform(raw_features)
    
    destiny_cluster = kmeans_model.predict(scaled_features)[0]
    message = Fortune_telling.get(destiny_cluster, "Hệ thống đang bói...")
    return hand_type, confidence, destiny_cluster, message

