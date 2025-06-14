import pandas as pd

def checkQR(QRcode, wakeup_data):
    wakeup_data
    NotValid_msg = "유효하지 않은 QR코드입니다."
    Welcome_msg = "입장완료되었습니다"
    Duplicate_msg = "이미 입장완료된 QR코드입니다."
    filtered_rows = wakeup_data.loc
    [
        wakeup_data["고유번호"] == QRcode
    ]  # QR 코드 고유번호 찾기

    if filtered_rows.empty:
        return NotValid_msg  # QR 코드가 존재하지 않으면 출력

    elif (
        pd.isna(filtered_rows["checked"].values[0])
        or filtered_rows["checked"].values[0] == ""
    ):
        wakeup_data.loc[wakeup_data["고유번호"] == QRcode, "checked"] = "입장완료"
        return Welcome_msg

    elif filtered_rows["checked"].values[0] == "입장완료":
        return Duplicate_msg


while True:
    wakeup_data = pd.read_csv("data.csv", encoding="utf-8")
    QRcode = input("QR코드를 입력하세요 (종료하려면 'exit' 입력): ")
    if QRcode.lower() == "exit":
        break
    result = checkQR(QRcode, wakeup_data)
    print(result)
    wakeup_data.to_csv("data.csv", index=False, encoding="utf-8")
