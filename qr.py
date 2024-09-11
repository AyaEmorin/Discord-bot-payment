from promptpay import qrcode

# generate a payload
id_or_phone_number = "0628054697"
payload = qrcode.generate_payload(id_or_phone_number)
payload_with_amount = qrcode.generate_payload(id_or_phone_number, 1.23)

# export to PIL image
img = qrcode.to_image(payload)

# export to file
qrcode.to_file(payload, "./qrcode-0841234567.png")
qrcode.to_file(payload_with_amount, "/Users/joe/Downloads/qrcode-0841234567.png") 