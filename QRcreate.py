import pandas as pd
import qrcode
import random
import string
import os

wakeup_data = pd.read_csv("data.csv", encoding="utf-8")


def generate_random_string(length=30):
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=length))


def create_qr_code(data, filename):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)


if "고유번호" not in wakeup_data.columns:
    wakeup_data["고유번호"] = ""

if "QRcode" not in wakeup_data.columns:
    wakeup_data["QRcode"] = ""

wakeup_data["고유번호"] = wakeup_data["고유번호"].apply(
    lambda x: generate_random_string() if pd.isna(x) or x == "" else x
)

# Create QR codes for each unique identifier
for index, row in wakeup_data.iterrows():
    unique_id = row["고유번호"]
    qr_filename = f"QR_{index}.png"

    if not os.path.exists(qr_filename):
        create_qr_code(unique_id, qr_filename)

    if pd.isna(row["QRcode"]) or row["QRcode"] == "":
        wakeup_data.at[index, "QRcode"] = qr_filename

# Save the updated data back to the CSV file
wakeup_data.to_csv("data.csv", index=False, encoding="utf-8")
