import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw, ImageFilter
import numpy as np

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

DEEP_PURPLE   = "#1A0A2E"
MID_PURPLE    = "#2D1B5E"
CARD_BG       = "#1E0F3A"
ACCENT_GOLD   = "#C9A84C"
ACCENT_GLOW   = "#A67C3A"
ACCENT_VIOLET = "#7B5EA7"
TEXT_MAIN     = "#F0E6FF"
TEXT_MUTED    = "#A08CC0"
TEXT_GOLD     = "#E8C878"
SUCCESS_GREEN = "#4CAF82"
BORDER_COLOR  = "#3D2870"

FORTUNE = {
    0:  "Học tập: Bạn sở hữu trực giác sắc bén, tiếp thu kiến thức rất nhanh, nhưng cần rèn luyện tính kỷ luật để đạt kết quả xuất sắc.\n\nSức khỏe: Thể trạng ổn định, tuy nhiên đừng bỏ bê việc nghỉ ngơi.\n\nTình duyên: Những rung động nhẹ nhàng đang đến, hãy để trái tim dẫn lối.",
    1:  "Học tập: Con đường học vấn đang rộng mở, sự kiên trì bền bỉ chính là chìa khóa giúp bạn chinh phục mọi đỉnh cao.\n\nSức khỏe: Hệ tiêu hóa hơi nhạy cảm, bạn nên ưu tiên chế độ ăn uống thanh đạm.\n\nTình duyên: Một mối quan hệ dựa trên sự tin tưởng và thấu hiểu sẽ là điểm tựa tinh thần.",
    2:  "Học tập: Bạn thường xuyên có những ý tưởng bay bổng, hãy cân bằng lại với thực tế để đạt hiệu quả cao nhất.\n\nSức khỏe: Đôi mắt cần được chăm sóc, tránh nhìn màn hình quá lâu.\n\nTình duyên: Những tín hiệu tích cực đang đến gần, một người mới sẽ chủ động tiến về phía bạn.",
    3:  "Học tập: Tố chất lãnh đạo tiềm ẩn giúp bạn luôn tỏa sáng khi làm việc nhóm.\n\nSức khỏe: Cần chú ý đến các khớp xương và duy trì vận động nhẹ nhàng mỗi ngày.\n\nTình duyên: Tình yêu lúc này đòi hỏi sự kiên nhẫn và niềm tin tuyệt đối.",
    4:  "Học tập: Tư duy sáng tạo và tâm hồn nghệ sĩ giúp bạn rất hợp với các lĩnh vực nhân văn, nghệ thuật.\n\nSức khỏe: Tinh thần minh mẫn, vẻ ngoài tràn đầy sức sống.\n\nTình duyên: Dẫu đường tình đôi lúc có chút chông chênh, nhưng kết quả cuối cùng sẽ rất ngọt ngào.",
    5:  "Học tập: Bạn đang chịu khá nhiều áp lực, hãy học cách thả lỏng để não bộ làm việc hiệu quả hơn.\n\nSức khỏe: Cần bổ sung dưỡng chất và tuân thủ giờ giấc nghỉ ngơi khoa học.\n\nTình duyên: Đừng quá khép kín, việc mở lòng sẽ mang đến cho bạn cơ hội bất ngờ.",
    6:  "Học tập: Trí nhớ của bạn là một tài sản quý giá, hãy tận dụng nó để chinh phục những kiến thức khó.\n\nSức khỏe: Chú ý theo dõi huyết áp và tránh xa những thực phẩm quá mặn.\n\nTình duyên: Một cuộc gặp gỡ bất ngờ từ quá khứ sẽ gợi lại những kỷ niệm đẹp.",
    7:  "Học tập: Sự chọn lọc tinh tế giúp bạn không bị quá tải trong biển kiến thức mênh mông.\n\nSức khỏe: Sức đề kháng tốt, cơ thể ít khi gặp phải những cơn ốm vặt.\n\nTình duyên: Hai tâm hồn đồng điệu đang tìm đến nhau, đây là thời điểm vàng.",
    8:  "Học tập: Sự nghiệp học hành đang thăng tiến vượt bậc như diều gặp gió.\n\nSức khỏe: Việc duy trì thói quen tập luyện sẽ giúp cơ thể thêm dẻo dai.\n\nTình duyên: Mối quan hệ tiến triển theo chiều hướng chậm mà chắc, bền vững và đầy trân trọng.",
    9:  "Học tập: Bạn dễ bị xao nhãng bởi các yếu tố bên ngoài, sự tập trung cao độ sẽ giúp bạn làm nên chuyện lớn.\n\nSức khỏe: Cần kiểm soát căng thẳng và tìm đến những thú vui lành mạnh.\n\nTình duyên: Hãy kiên nhẫn, người xứng đáng nhất sẽ xuất hiện đúng lúc.",
    10: "Học tập: Có quý nhân phù trợ trong con đường học vấn, mọi trở ngại sẽ sớm được hóa giải.\n\nSức khỏe: Trạng thái cơ thể rất tốt, chỉ cần duy trì lối sống điều độ.\n\nTình duyên: Bạn rất có sức hút, nên cẩn thận kẻo sự đa sầu đa cảm khiến khó quyết định.",
    11: "Học tập: Nỗ lực gấp đôi so với hiện tại sẽ mang lại kết quả vượt ngoài mong đợi.\n\nSức khỏe: Chú ý đến đường hô hấp, tránh tiếp xúc nơi ô nhiễm.\n\nTình duyên: Một chuyện tình đẹp đòi hỏi sự thành thật và vun vén từ cả hai phía.",
    12: "Học tập: Bạn có năng khiếu đặc biệt với các con số hoặc kỹ thuật, hãy khai thác thế mạnh này.\n\nSức khỏe: Đừng quên vận động vai gáy và lưng sau nhiều giờ làm việc.\n\nTình duyên: Người yêu bạn rất tinh tế, họ luôn biết cách làm cho bạn cảm thấy đặc biệt.",
    13: "Học tập: Những ý tưởng độc đáo của bạn rất cần được chia sẻ, đừng ngần ngại bày tỏ quan điểm.\n\nSức khỏe: Cung cấp đủ nước cho cơ thể mỗi ngày là chìa khóa của sự tỉnh táo.\n\nTình duyên: Tuần này là cơ hội tốt để kết nối với người hợp cạ với bạn.",
    14: "Học tập: Kiên trì là phẩm chất vàng, chỉ cần không nản chí bạn chắc chắn sẽ thành công.\n\nSức khỏe: Cơ thể đang trong giai đoạn hồi phục và tràn đầy năng lượng.\n\nTình duyên: Những tranh cãi nhỏ chỉ là gia vị của tình yêu, hãy nói chuyện thẳng thắn.",
    15: "Học tập: Tài năng thiên bẩm giúp bạn đạt được thành công sớm hơn dự định.\n\nSức khỏe: Bạn đang sở hữu nguồn năng lượng dồi dào.\n\nTình duyên: Người ấy coi bạn như món quà quý giá, hãy trân trọng hạnh phúc này.",
}

HAND_LABEL_VI = {
    "left":  "Bàn Tay Trái",
    "right": "Bàn Tay Phải",
    "both":  "Cả Hai Tay",
}

class PalmApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("✦ Bói Bàn Tay · Palmistry AI ✦")
        self.geometry("960x740")
        self.minsize(860, 660)
        self.configure(fg_color=DEEP_PURPLE)

        self.assets = None
        self.img_path = None
        self._photo = None
        self._loading_angle = 0
        self._loading_active = False

        self._build_ui()
        self._load_models_async()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1, minsize=320)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)

        self._build_header()
        self._build_left_panel()
        self._build_right_panel()
        self._build_footer()

    def _build_header(self):
        hdr = ctk.CTkFrame(self, fg_color=MID_PURPLE, corner_radius=0, height=64)
        hdr.grid(row=0, column=0, columnspan=2, sticky="ew")
        hdr.grid_propagate(False)
        hdr.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            hdr,
            text="✦  BÓI BÀN TAY · PALMISTRY AI  ✦",
            font=ctk.CTkFont(family="Georgia", size=20, weight="bold"),
            text_color=TEXT_GOLD,
        )
        title.grid(row=0, column=0, pady=18)

        self.status_dot = ctk.CTkLabel(
            hdr, text="● Đang tải mô hình...",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED,
        )
        self.status_dot.grid(row=0, column=1, padx=20)

    def _build_left_panel(self):
        left = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=0)
        left.grid(row=1, column=0, sticky="nsew", padx=(12, 6), pady=12)
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(2, weight=1)

        section_lbl = ctk.CTkLabel(
            left, text="📷  ẢNH BÀN TAY",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=ACCENT_GOLD,
        )
        section_lbl.grid(row=0, column=0, padx=16, pady=(16, 8), sticky="w")

        self.img_canvas = tk.Canvas(
            left, bg="#120626", bd=0, highlightthickness=1,
            highlightbackground=BORDER_COLOR, width=280, height=280,
        )
        self.img_canvas.grid(row=1, column=0, padx=16, pady=0, sticky="ew")
        self._draw_placeholder()

        btn_frame = ctk.CTkFrame(left, fg_color="transparent")
        btn_frame.grid(row=2, column=0, padx=16, pady=12, sticky="ew")
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        self.upload_btn = ctk.CTkButton(
            btn_frame,
            text="📁  Chọn Ảnh",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=ACCENT_VIOLET,
            hover_color="#9B7EC8",
            text_color=TEXT_MAIN,
            corner_radius=8,
            height=40,
            command=self._pick_image,
        )
        self.upload_btn.grid(row=0, column=0, padx=(0, 4), sticky="ew")

        self.predict_btn = ctk.CTkButton(
            btn_frame,
            text="🔮  Bói Ngay",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=ACCENT_GOLD,
            hover_color=ACCENT_GLOW,
            text_color="#1A0A2E",
            corner_radius=8,
            height=40,
            state="disabled",
            command=self._run_predict,
        )
        self.predict_btn.grid(row=0, column=1, padx=(4, 0), sticky="ew")

        info_frame = ctk.CTkFrame(left, fg_color="#150B30", corner_radius=8)
        info_frame.grid(row=3, column=0, padx=16, pady=(0, 16), sticky="ew")
        info_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(info_frame, text="Loại bàn tay:", font=ctk.CTkFont(size=11), text_color=TEXT_MUTED).grid(row=0, column=0, sticky="w", padx=10, pady=(10, 2))
        self.hand_var = ctk.CTkLabel(info_frame, text="—", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_GOLD)
        self.hand_var.grid(row=1, column=0, sticky="w", padx=10, pady=(0, 10))

        ctk.CTkLabel(info_frame, text="Độ tin cậy:", font=ctk.CTkFont(size=11), text_color=TEXT_MUTED).grid(row=0, column=1, sticky="w", padx=10, pady=(10, 2))
        self.conf_var = ctk.CTkLabel(info_frame, text="—", font=ctk.CTkFont(size=12, weight="bold"), text_color=SUCCESS_GREEN)
        self.conf_var.grid(row=1, column=1, sticky="w", padx=10, pady=(0, 10))

        ctk.CTkLabel(info_frame, text="Nhóm vận mệnh:", font=ctk.CTkFont(size=11), text_color=TEXT_MUTED).grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=(6, 2))
        self.cluster_var = ctk.CTkLabel(info_frame, text="—", font=ctk.CTkFont(size=13, weight="bold"), text_color=ACCENT_VIOLET)
        self.cluster_var.grid(row=3, column=0, columnspan=2, sticky="w", padx=10, pady=(0, 10))

    def _build_right_panel(self):
        right = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=0)
        right.grid(row=1, column=1, sticky="nsew", padx=(6, 12), pady=12)
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)

        section_lbl = ctk.CTkLabel(
            right, text="🌙  LỜI TIÊN TRI",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=ACCENT_GOLD,
        )
        section_lbl.grid(row=0, column=0, padx=16, pady=(16, 8), sticky="w")

        self.fortune_box = ctk.CTkScrollableFrame(
            right, fg_color="#100825", corner_radius=8,
            scrollbar_button_color=ACCENT_VIOLET,
            scrollbar_button_hover_color=ACCENT_GOLD,
        )
        self.fortune_box.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="nsew")
        self.fortune_box.grid_columnconfigure(0, weight=1)

        self.fortune_label = ctk.CTkLabel(
            self.fortune_box,
            text="Hãy chọn ảnh bàn tay và nhấn\n「Bói Ngay」để khám phá vận mệnh ✨",
            font=ctk.CTkFont(family="Georgia", size=14),
            text_color=TEXT_MUTED,
            justify="center",
            wraplength=460,
        )
        self.fortune_label.grid(row=0, column=0, padx=20, pady=60)

        self.progress_canvas = tk.Canvas(
            right, bg=CARD_BG, bd=0, highlightthickness=0, height=4,
        )
        self.progress_canvas.grid(row=2, column=0, sticky="ew", padx=0, pady=0)

    def _build_footer(self):
        foot = ctk.CTkFrame(self, fg_color=MID_PURPLE, corner_radius=0, height=30)
        foot.grid(row=2, column=0, columnspan=2, sticky="ew")
        foot.grid_propagate(False)

        ctk.CTkLabel(
            foot,
            text="✦ Palmistry AI · Powered by Deep Learning  ·  Mô hình: CNN + KMeans  ✦",
            font=ctk.CTkFont(size=10),
            text_color=TEXT_MUTED,
        ).pack(pady=6)

    def _draw_placeholder(self):
        self.img_canvas.delete("all")
        w, h = 280, 280
        self.img_canvas.create_rectangle(0, 0, w, h, fill="#120626", outline="")
        cx, cy = w // 2, h // 2
        for r, alpha in [(90, 20), (70, 30), (50, 40)]:
            self.img_canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                outline=ACCENT_VIOLET, width=1,
            )
        self.img_canvas.create_text(
            cx, cy,
            text="🖐",
            font=("Segoe UI Emoji", 48),
            fill="#3D2870",
        )
        self.img_canvas.create_text(
            cx, cy + 80,
            text="Nhấn「Chọn Ảnh」để bắt đầu",
            font=("Georgia", 11),
            fill=TEXT_MUTED,
        )

    def _pick_image(self):
        path = filedialog.askopenfilename(
            title="Chọn ảnh bàn tay",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.webp"), ("All", "*.*")],
        )
        if not path:
            return
        self.img_path = path
        self._show_image(path)
        if self.assets:
            self.predict_btn.configure(state="normal")
        self.fortune_label.configure(
            text='Ảnh đã được tải lên!\nNhấn 「Bói Ngay」 để khám phá vận mệnh 🔮',
            text_color=TEXT_MAIN,
        )
        self.hand_var.configure(text="—")
        self.conf_var.configure(text="—")
        self.cluster_var.configure(text="—")

    def _show_image(self, path):
        try:
            img = Image.open(path).convert("RGB")
            img.thumbnail((270, 270), Image.LANCZOS)
            w, h = img.size
            self.img_canvas.config(width=280, height=280)
            self.img_canvas.delete("all")
            self.img_canvas.create_rectangle(0, 0, 280, 280, fill="#120626", outline="")
            ox = (280 - w) // 2
            oy = (280 - h) // 2
            self._photo = ImageTk.PhotoImage(img)
            self.img_canvas.create_image(ox, oy, anchor="nw", image=self._photo)
            self.img_canvas.create_rectangle(ox, oy, ox + w, oy + h, outline=ACCENT_GOLD, width=2)
        except Exception as e:
            self._show_error(f"Không thể đọc ảnh:\n{e}")

    def _load_models_async(self):
        def worker():
            try:
                from predict import load_all_assets
                assets = load_all_assets()
                self.after(0, self._on_models_loaded, assets)
            except Exception as e:
                self.after(0, self._on_models_error, str(e))
        threading.Thread(target=worker, daemon=True).start()

    def _on_models_loaded(self, assets):
        self.assets = assets
        self.status_dot.configure(text="● Sẵn sàng", text_color=SUCCESS_GREEN)
        if self.img_path:
            self.predict_btn.configure(state="normal")

    def _on_models_error(self, msg):
        self.status_dot.configure(text="● Lỗi mô hình", text_color="#E24B4A")
        self._show_error(f"⚠ Không thể tải mô hình:\n{msg}\n\nĐảm bảo các file .h5 và .pkl nằm cùng thư mục với script này.")

    def _run_predict(self):
        if not self.assets or not self.img_path:
            return
        self.predict_btn.configure(state="disabled", text="⏳  Đang phán...")
        self.fortune_label.configure(text="✨ Đang đọc vân tay của bạn...", text_color=ACCENT_GOLD)
        self._start_progress_anim()

        def worker():
            try:
                from predict import predict_palmistry
                hand_type, confidence, cluster, message = predict_palmistry(self.img_path, self.assets)
                self.after(0, self._show_result, hand_type, confidence, cluster, message)
            except Exception as e:
                self.after(0, self._show_error, str(e))
            finally:
                self.after(0, self._stop_progress_anim)

        threading.Thread(target=worker, daemon=True).start()

    def _show_result(self, hand_type, confidence, cluster, message):
        label_vi = HAND_LABEL_VI.get(hand_type.lower(), hand_type)
        self.hand_var.configure(text=label_vi)
        self.conf_var.configure(text=f"{confidence:.1f}%")
        self.cluster_var.configure(text=f"Nhóm #{cluster + 1}  (id: {cluster})")

        stars = "★" * min(5, int(confidence / 20))
        full_text = (
            f"✦  VẬN MỆNH NHÓM #{cluster + 1}  ✦\n"
            f"{'─' * 42}\n\n"
            f"{message}\n\n"
            f"{'─' * 42}\n"
            f"Bàn tay: {label_vi}   |   Độ tin cậy: {confidence:.1f}%  {stars}"
        )
        self.fortune_label.configure(text=full_text, text_color=TEXT_MAIN, justify="left")
        self.predict_btn.configure(state="normal", text="🔮  Bói Lại")

    def _show_error(self, msg):
        self.fortune_label.configure(text=f"⚠  Đã xảy ra lỗi:\n\n{msg}", text_color="#E24B4A")
        self.predict_btn.configure(state="normal", text="🔮  Bói Ngay")

    def _start_progress_anim(self):
        self._loading_active = True
        self._animate_progress()

    def _stop_progress_anim(self):
        self._loading_active = False
        self.progress_canvas.delete("all")

    def _animate_progress(self):
        if not self._loading_active:
            return
        self.progress_canvas.delete("all")
        w = self.progress_canvas.winfo_width() or 600
        self._loading_angle = (self._loading_angle + 4) % 360
        seg_len = int(w * 0.25)
        start = int((self._loading_angle / 360) * w)
        x1 = start % w
        x2 = (start + seg_len) % w
        if x1 < x2:
            self.progress_canvas.create_rectangle(x1, 0, x2, 4, fill=ACCENT_GOLD, outline="")
        else:
            self.progress_canvas.create_rectangle(x1, 0, w, 4, fill=ACCENT_GOLD, outline="")
            self.progress_canvas.create_rectangle(0, 0, x2, 4, fill=ACCENT_GOLD, outline="")
        self.after(16, self._animate_progress)


if __name__ == "__main__":
    app = PalmApp()
    app.mainloop()