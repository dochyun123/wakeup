import pandas as pd
import tkinter as tk
from tkinter import messagebox
import pandas as pd
import yaml
import os
import sys
from tkinterdnd2 import DND_FILES, TkinterDnD
from datetime import datetime


def resource_path(relative_path):
    """PyInstaller용: 실행 파일 내부에서도 리소스를 찾게 함"""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


# YAML 파일 로드
with open(resource_path("config.yaml"), "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)


NotValid_msg = config["NotValid_msg"]
Welcome_msg = config["Welcome_msg"]
Duplicate_msg = config["Duplicate_msg"]


# QR 코드 처리 클래스
class QRCodeHandler:
    def __init__(self, file_path):
        self.file_path = file_path
        self.wakeup_data = pd.read_csv(file_path, encoding="utf-8-sig")
        self.wakeup_data["checked"] = self.wakeup_data["checked"].astype("object")
        self.entrance_num = 0

    def getMessage(self, QRcode):
        self.current_row = self.wakeup_data.loc[self.wakeup_data["고유번호"] == QRcode]
        if self.current_row.empty:
            return NotValid_msg

        check_value = self.current_row["checked"].values[0]
        if pd.isna(check_value) or check_value == "":
            self.wakeup_data.loc[self.wakeup_data["고유번호"] == QRcode, "checked"] = (
                "입장완료"
            )
            self.save_data()  # 데이터 저장
            self.entrance_num = self.count_num()  # 입장 인원 수 업데이트
            self.get_log(QRcode)
            return Welcome_msg

        elif pd.notna(check_value) and check_value != "":
            return Duplicate_msg

    def get_log(self, QRcode):
        if os.path.exists("log.csv"):
            log_data = pd.read_csv("log.csv", encoding="utf-8-sig")
        else:
            log_data = pd.DataFrame(
                columns=["이름", "중학교", "교회", "전화번호", "입장시간"]
            )
        current_row = self.wakeup_data.loc[self.wakeup_data["고유번호"] == QRcode]
        current_data = {
            "이름": current_row["이름을 알려주세요!"].values[0],
            "중학교": current_row["다니는 학교 이름을 알려주세요!"].values[0],
            "교회": current_row["현재 출석하고 있는 교회 이름을 알려주세요!"].values[0],
            "전화번호": current_row[
                "전화번호를 알려주세요! (01012345678 형식으로)"
            ].values[0],
            "입장시간": datetime.now().strftime("%m-%d %H:%M"),
        }
        log_data = pd.concat(
            [log_data, pd.DataFrame([current_data])], ignore_index=True
        )
        log_data.to_csv("log.csv", index=False, encoding="utf-8-sig")

    def count_num(self):
        num = sum(self.wakeup_data["checked"] == "입장완료")
        print(f"입장한 사람 수: {num}")
        return num

    def save_data(self):
        self.wakeup_data.to_csv(self.file_path, index=False, encoding="utf-8-sig")


# Tkinter GUI 설정
class QRscanner:
    def __init__(self, root):
        self.root = root
        # self.qr_handler = qr_handler
        self.qr_handler = None
        self.root.title("QR 코드 확인 시스템")
        self.root.geometry("400x250+800+300")
        # self.root.geometry("400x250")

        self.drop_label = tk.Label(
            root,
            text="Upload csv file here!",
            font=("Arial", 14),
            width=40,
            height=10,
            relief="groove",
            bd=2,
            bg="lightgray",
        )
        self.drop_label.pack(pady=80)
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind("<<Drop>>", self.on_drop)

    def on_drop(self, event):
        file_path = event.data.strip("{}")
        if file_path.endswith(".csv"):
            self.qr_handler = QRCodeHandler(file_path)
            self.drop_label.config(
                text=f"파일 업로드 완료: {os.path.basename(file_path)}"
            )
            self.create_widgets()
        else:
            messagebox.showerror("오류", "CSV 파일만 업로드 가능합니다.")

    def create_widgets(self):
        self.drop_label.destroy()
        self.label = tk.Label(
            self.root, text="QR을 찍은 후 스페이스바를 누르세요:", font=("Arial", 12)
        )
        self.label.pack(pady=10)

        self.entry = tk.Entry(self.root, font=("Arial", 12), width=30)
        self.entry.pack(pady=5)

        # Press Space to enter QR code
        self.entry.bind("<space>", lambda event: self.check_qr_code())
        self.status_label = tk.Label(self.root,
                                     text=f"👥 입장한 사람 수 : {self.qr_handler.entrance_num}",
                                     font=("Arial", 14, "bold"),
                                     fg="#0078D7",
                                     bg="#ffffff"
)

        self.status_label.pack(pady=10,anchor="center")

        # 확인 button
        button_frame = tk.Frame(self.root)
        button_frame.pack(side='bottom',pady=20)

        self.button = tk.Button(
            button_frame, text="확인", font=("Arial", 12), command=self.check_qr_code
        )
        self.button.pack(side="left", padx=(0, 20))  # 오른쪽 간격 조금

        # 종료 button 
        self.exit_button = tk.Button(
            button_frame, text="종료", font=("Arial", 12), command=self.exit_app
        )
        self.exit_button.pack(side="left")
        self.entry.focus_set()  # 입력창에 커서 올리기

    def check_qr_code(self):
        QRcode = self.entry.get().strip()
        print(f"입력된 QR 코드: {QRcode}")
        result = self.qr_handler.getMessage(QRcode)

        # 정상적인 상태 (녹색 창)
        if result == Welcome_msg:
            messagebox.showinfo("✅ 통과", result)

        # 에러 상태 (빨간색 창)
        else:
            messagebox.showerror("❌ 오류", result)
        self.status_label.config(
            text=f"입장한 사람 수 : {self.qr_handler.entrance_num}"
        )
        self.entry.delete(0, tk.END)

    def exit_app(self):
        self.qr_handler.save_data()
        self.root.destroy()


# 실행 코드
if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = QRscanner(root)
    root.mainloop()