from PIL import Image

def check_image(path):
    try:
        img = Image.open(path)
        img.verify()  # 이미지가 손상되었는지 확인
        print(f"{path}는 올바른 이미지입니다.")
    except (IOError, SyntaxError) as e:
        print(f"{path}가 올바르지 않습니다: {e}")

check_image("/home/BlueDump/BlueDump_Android_AI/reboot_bl/13/targets/탁재훈 프로필_converted.jpeg")
