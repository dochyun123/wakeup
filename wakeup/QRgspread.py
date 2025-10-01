import gspread
from oauth2client.service_account import ServiceAccountCredentials
import tkinter as tk
from tkinter import messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from datetime import datetime
import yaml
import os
import sys
import pandas as pd
import dotenv

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# 환경설정 YAML 불러오기
with open(resource_path("config.yaml"), "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

NotValid_msg = config["NotValid_msg"]
Welcome_msg = config["Welcome_msg"]
Duplicate_msg = config["Duplicate_msg"]



# 구글 시트 URL/시트명
sheetUrl = "" # 구글시트의 url을 입력하세요.
sheetName = "" # 구글시트의 이름을 입력하세요.

# Google Sheet 연결
def getSheet(sheetUrl, sheetName):
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    jsonKeyFilePath = resource_path("") # json token 파일 경로를 입력하세요
    creds = ServiceAccountCredentials.from_json_keyfile_name(jsonKeyFilePath, scope)
    client = gspread.authorize(creds)
    spreadSheet = client.open_by_url(sheetUrl)
    return spreadSheet.worksheet(sheetName)




# 시트 객체 생성
ws = getSheet(sheetUrl, sheetName)


# QR 코드 처리 클래스
class QRCodeHandler:
    def __init__(self, worksheet):
        self.ws = worksheet
        self.ensure_checked_column()

        # ✅ 최초 실행 시 전체 데이터 캐싱
        data = self.ws.get_all_records()
        self.df = pd.DataFrame(data)
        self.entrance_num = self.count_num()

    def ensure_checked_column(self):
        """checked 컬럼이 없으면 추가"""
        header = self.ws.row_values(1)  # 1행(헤더)
        if "checked" not in header:
            col_num = len(header) + 1
            self.ws.update_cell(1, col_num, "checked")
            print("✅ 'checked' 컬럼이 없어서 새로 추가했습니다.")

    def getMessage(self, QRcode):
        current_row = self.df.loc[self.df["고유번호"] == QRcode]

        if current_row.empty:
            return NotValid_msg

        row_index = current_row.index[0] + 2  # header 제외
        check_value = current_row["checked"].values[0]


        if pd.isna(check_value) or check_value == "":
            # ✅ 시트 업데이트 (실시간 반영)
            self.ws.update_cell(row_index, self.df.columns.get_loc("checked") + 1, "입장완료")

            # ✅ 캐시 업데이트
            self.df.at[current_row.index[0], "checked"] = "입장완료"

            # ✅ 인원수 즉시 반영
            self.entrance_num += 1
            self.get_log(current_row)
            return Welcome_msg

        elif pd.notna(check_value) and check_value != "":
            return Duplicate_msg

    def get_log(self, current_row):
        """입장 기록을 로컬 log.csv에 저장"""
        if os.path.exists("log.csv"):
            log_data = pd.read_csv("log.csv", encoding="utf-8-sig")
        else:
            log_data = pd.DataFrame(columns=["이름", "중학교", "교회", "전화번호", "입장시간"])

        current_data = {
            "이름": current_row["이름을 알려주세요!"].values[0],
            "중학교": current_row["다니는 학교 이름을 알려주세요!"].values[0],
            "교회": current_row["현재 출석하고 있는 교회 이름을 알려주세요!"].values[0],
            "전화번호": current_row["전화번호를 알려주세요! (01012345678 형식으로)"].values[0],
            "입장시간": datetime.now().strftime("%m-%d %H:%M"),
        }
        log_data = pd.concat([log_data, pd.DataFrame([current_data])], ignore_index=True)
        log_data.to_csv("log.csv", index=False, encoding="utf-8-sig")

    def count_num(self):
        if "checked" not in self.df.columns:
            return 0
        num = sum(self.df["checked"] == "입장완료")
        print(f"입장한 사람 수: {num}")
        return num


# Tkinter GUI
class QRscanner:
    def __init__(self, root):
        self.root = root
        self.qr_handler = QRCodeHandler(ws)
        self.root.title("QR 코드 확인 시스템")
        self.root.geometry("400x250+800+300")

        self.label = tk.Label(
            self.root, text="QR을 찍은 후 스페이스바를 누르세요:", font=("Arial", 12)
        )
        self.label.pack(pady=10)

        self.entry = tk.Entry(self.root, font=("Arial", 12), width=30)
        self.entry.pack(pady=5)
        self.entry.bind("<space>", lambda event: self.check_qr_code())

        self.status_label = tk.Label(
            self.root,
            text=f"👥 입장한 사람 수 : {self.qr_handler.entrance_num}",
            font=("Arial", 14, "bold"),
            fg="#0078D7",
            bg="#ffffff"
        )
        self.status_label.pack(pady=10, anchor="center")

        button_frame = tk.Frame(self.root)
        button_frame.pack(side='bottom', pady=20)

        self.button = tk.Button(
            button_frame, text="확인", font=("Arial", 12), command=self.check_qr_code
        )
        self.button.pack(side="left", padx=(0, 20))

        self.exit_button = tk.Button(
            button_frame, text="종료", font=("Arial", 12), command=self.exit_app
        )
        self.exit_button.pack(side="left")

        self.entry.focus_set()

    def check_qr_code(self):
        QRcode = self.entry.get().strip()
        print(f"입력된 QR 코드: {QRcode}")
        result = self.qr_handler.getMessage(QRcode)

        if result == Welcome_msg:
            messagebox.showinfo("✅ 통과", result)
        else:
            messagebox.showerror("❌ 오류", result)

        self.status_label.config(
            text=f"입장한 사람 수 : {self.qr_handler.entrance_num}"
        )
        self.entry.delete(0, tk.END)

    def exit_app(self):
        self.root.destroy()


# 실행 코드
if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = QRscanner(root)
    root.mainloop()
