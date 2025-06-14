import pandas as pd

import tkinter as tk
from tkinter import messagebox
import pandas as pd

# QR 코드 처리 클래스
class QRCodeHandler:
    def __init__(self, file_path):
        self.file_path = file_path
        self.wakeup_data = pd.read_csv(file_path, encoding="utf-8")

    def checkQR(self, QRcode):
        NotValid_msg = "유효하지 않은 QR코드입니다."
        Welcome_msg = "입장완료되었습니다"
        Duplicate_msg = "이미 입장완료된 QR코드입니다."
        
        filtered_rows = self.wakeup_data.loc[self.wakeup_data["고유번호"] == QRcode]
        
        if filtered_rows.empty:
            return NotValid_msg
        
        elif pd.isna(filtered_rows["checked"].values[0]) or filtered_rows["checked"].values[0] == "":
            self.wakeup_data.loc[self.wakeup_data["고유번호"] == QRcode, "checked"] = "입장완료"
            self.save_data()  # 데이터 저장
            return Welcome_msg
        
        elif filtered_rows["checked"].values[0] == "입장완료":
            return Duplicate_msg

    def save_data(self):
        self.wakeup_data.to_csv(self.file_path, index=False, encoding="utf-8")


# Tkinter GUI 설정
class QRscanner:
    def __init__(self, root, qr_handler):
        self.root = root
        self.qr_handler = qr_handler
        self.root.title("QR 코드 확인 시스템")
        self.root.geometry("400x250")

        self.label = tk.Label(root, text="QR 코드를 입력하세요:", font=("Arial", 12))
        self.label.pack(pady=10)

        self.entry = tk.Entry(root, font=("Arial", 12), width=30)
        self.entry.pack(pady=5)

        self.button = tk.Button(root, text="확인", font=("Arial", 12), command=self.check_qr_code)
        self.button.pack(pady=10)

        self.exit_button = tk.Button(root, text="종료", font=("Arial", 12), command=self.exit_app)
        self.exit_button.pack(pady=5)

    def check_qr_code(self):
        QRcode = self.entry.get()
        result = self.qr_handler.checkQR(QRcode)

        # 정상적인 상태 (녹색 창)
        if result == "입장 완료되었습니다":
            messagebox.showinfo("✅ 통과", result)

        # 에러 상태 (빨간색 창)
        else:
            messagebox.showerror("❌ 오류", result)

    def exit_app(self):
        self.qr_handler.save_data()
        self.root.destroy()

# 실행 코드
file_path = "data.csv"
qr_handler = QRCodeHandler(file_path)

root = tk.Tk()
app = QRscanner(root, qr_handler)
root.mainloop()