from kernelbot import apihelper


def test_api_url_format():
    url = apihelper.API_URL.format("123:ABC", "getMe")
    assert url == "https://api.kernelgram.club/bot123:ABC/getMe"


def test_file_url_format():
    url = apihelper.FILE_URL.format("123:ABC", "photos/file.jpg")
    assert url == "https://api.kernelgram.club/file/bot123:ABC/photos/file.jpg"


def test_force_ipv4_default():
    assert apihelper.FORCE_IPV4 is True
