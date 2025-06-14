import pandas as pd

wakeup_data = pd.read_csv("data.csv", encoding="utf-8")

QRcode = "QEw5m3PQl0WKVEY255LUliYOJxYe24"

if "checked" not in wakeup_data.columns:
    wakeup_data["checked"] = ""  # 기본값을 False로 설정


filtered_rows = wakeup_data.loc[wakeup_data["고유번호"] == QRcode]


# print(filtered_rows["checked"].values[0])

if filtered_rows.empty:
    print("유효하지 않은 QR코드입니다.")  # QR 코드가 존재하지 않으면 출력
else:
    checked_value = filtered_rows["checked"].values[0]

    if pd.isna(checked_value) or checked_value == "":
        wakeup_data.loc[wakeup_data["고유번호"] == QRcode, "checked"] = "입장완료"
        print("입장완료되었습니다.")
        name = wakeup_data.loc[wakeup_data["고유번호"] == QRcode, "이름"]
        print(f"입장한 사람의 이름: {name.values[0]}")

    else:
        print("이미 입장완료된 QR코드입니다.")

wakeup_data.to_csv("data.csv", index=False, encoding="utf-8")
