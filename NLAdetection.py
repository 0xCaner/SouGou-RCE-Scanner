import os
import signal
import socket
import subprocess
import cv2
import psutil
import pyautogui
import time

# 抓取当前屏幕截图并保存
def capture_screenshot():
    screenshot = pyautogui.screenshot()
    screenshot.save('screenshot.png')

# 在截图中找到目标图像的位置
def find_image_on_screen(target_image_path, threshold=0.8):
    # 抓取当前屏幕截图
    capture_screenshot()

    # 读取屏幕截图和目标图像
    screenshot = cv2.imread('screenshot.png')
    target_image = cv2.imread(target_image_path)

    # 将两张图像转换为灰度图
    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    target_image_gray = cv2.cvtColor(target_image, cv2.COLOR_BGR2GRAY)

    # 执行模板匹配
    result = cv2.matchTemplate(screenshot_gray, target_image_gray, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # 如果匹配程度超过设定的阈值，那么获取匹配位置的中心点
    if max_val >= threshold:
        target_w, target_h = target_image_gray.shape[::-1]
        center_x = max_loc[0] + target_w // 2
        center_y = max_loc[1] + target_h // 2
        return center_x, center_y
    else:
        return None

# 自动点击指定位置
def click_position(position):
    x, y = position
    pyautogui.moveTo(x, y)
    pyautogui.click()

def check_port(rdpaddress, timeout=1):
    """
    检查指定主机的端口是否开启

    :param host: 主机地址（IP 地址或域名）
    :param port: 端口号
    :param timeout: 连接超时时间（秒），默认为1秒
    :return: 是否开启 (True: 开启, False: 未开启)
    """
    res = rdpaddress.split(":")
    if len(res) == 1:
        host = res[0]
        port = 3389
    else:
        host, port = rdpaddress.split(":")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((host, int(port)))
    except (socket.timeout, socket.error):
        return False
    finally:
        sock.close()
    return True

Default = open("Default.rdp", "r", encoding="utf-8").read()
def AutoCheck():
    file = open("RDPList.txt", "r", encoding="utf-8")
    result = open("result.txt", "w", encoding="utf-8")
    result.write("\n")
    while (line := file.readline()):
        if line.endswith("\n"):
            rdpaddress = line[:-1]
        else:
            rdpaddress = line
        if not check_port(rdpaddress):
            print(f"端口未开放连接: {rdpaddress}")
            continue
        open("NLA.rdp", "w", encoding="utf-8").write(Default.replace("47.118.52.141:3389", rdpaddress))
        process = subprocess.Popen(["mstsc", "NLA.rdp"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(0.8)
        target_image_path = 'confirmConnection.png'  # 目标图像路径
        position = find_image_on_screen(target_image_path) # 图像匹配到屏幕上所在图片的中心位置

        if position:
            x, y = position
            # 确认按钮与图像匹配中心偏移量，该偏移量为1080P win11版测试可用，其他分辨率需要自行调整
            position = (x + 894 - 755, y + 563 - 455)

            print(position) # 确认按钮位置
            print(f"确认连接: {rdpaddress}")
            click_position(position)
        else:
            print(f"未找到确认连接按钮: {rdpaddress}")
            if process.poll() is None:  # 检查进程是否还在运行
                # parent = psutil.Process(process.pid)
                # children = parent.children(recursive=True)
                # for child in children:
                #     print(child.pid, child.name())
                #     os.kill(child.pid, signal.SIGTERM)  # 使用SIGKILL信号终止子进程
                os.kill(process.pid, signal.SIGTERM)  # 使用SIGKILL信号终止父进程
                print(f"Terminated process with PID: {process.pid}")


            result.write(line)
            continue

        time.sleep(0.8)
        target_image_path = 'connectionFailed.png'  # 目标图像路径
        position = find_image_on_screen(target_image_path)
        if position:
            x, y = position
            # 确认按钮与图像匹配中心偏移量，该偏移量为1080P win11版测试可用，其他分辨率需要自行调整
            position = (x + 980 - 841, y + 460 - 352)
            print(position)
            print(f"连接失败: {rdpaddress},原因：开启了NLA")
            click_position(position)
        else:
            print(f"未找到连接失败按钮: {rdpaddress}, 需要人工复查")
            result.write(line)

        if process.poll() is None:  # 检查进程是否还在运行
            # parent = psutil.Process(process.pid)
            # children = parent.children(recursive=True)
            # for child in children:
            #     print(child.pid, child.name())
            #     os.kill(child.pid, signal.SIGTERM)  # 使用SIGKILL信号终止子进程
            os.kill(process.pid, signal.SIGTERM)  # 使用SIGKILL信号终止父进程
            print(f"Terminated process with PID: {process.pid}")


def ManualCheck():
    result = open("result.txt", "r", encoding="utf-8")
    lines = result.readlines()
    for i in range(len(lines)):
        line = lines[i+1]
        rdpaddress = line[:-1]
        if not check_port(rdpaddress):
            print(f"端口未开放连接: {rdpaddress}")
            continue
        open("NLA.rdp", "w", encoding="utf-8").write(Default.replace("47.118.52.141:3389", rdpaddress))
        process = subprocess.Popen(["mstsc", "NLA.rdp"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(0.8)
        target_image_path = 'confirmConnection.png'  # 目标图像路径
        position = find_image_on_screen(target_image_path)

        if position:
            x, y = position
            # 确认按钮与图像匹配中心偏移量，该偏移量为1080P win11版测试可用，其他分辨率需要自行调整
            position = (x + 894 - 755, y + 563 - 455)
            print(position)
            print(f"确认连接: {rdpaddress}")
            click_position(position)
        else:
            print(f"未找到确认连接按钮: {rdpaddress}")
            exit(0)

        time.sleep(0.8)
        target_image_path = 'oldVersionConfirm.png'  # 目标图像路径
        position = find_image_on_screen(target_image_path)
        if position:
            x, y = position
            # 确认按钮与图像匹配中心偏移量，该偏移量为1080P win11版测试可用，其他分辨率需要自行调整
            position = (x + 830 - 756, y + 545 - 459)
            print(position)
            print(f"老版本连接，二次确认: {rdpaddress}")
            click_position(position)
            time.sleep(0.8)
        else:
            print(f"非老版本: {rdpaddress}")

        target_image_path = 'certConfirm.png'  # 目标图像路径
        position = find_image_on_screen(target_image_path)
        if position:
            x, y = position
            # 确认按钮与图像匹配中心偏移量，该偏移量为1080P win11版测试可用，其他分辨率需要自行调整
            position = (x + 828 - 754, y + 710 - 458)
            print(position)
            print(f"连接证书不可信确认，自动确认: {rdpaddress}")
            click_position(position)
            time.sleep(0.8)
        else:
            print(f"非证书可信认证页面: {rdpaddress}")

        target_image_path = 'connectionFailed.png'  # 目标图像路径
        position = find_image_on_screen(target_image_path)
        if position:
            x, y = position
            # 确认按钮与图像匹配中心偏移量，该偏移量为1080P win11版测试可用，其他分辨率需要自行调整
            position = (x + 980 - 841, y + 460 - 352)
            print(position)
            print(f"连接失败: {rdpaddress},原因：开启了NLA")
            click_position(position)
            continue
        else:
            print(f"未找到连接失败按钮: {rdpaddress}")

        # print(lines[i+1:])
        open("result.txt", "w", encoding="utf-8").writelines(lines[i+1:])
        break

def closeOtherRDPClient():
    python_processes = []
    for process in psutil.process_iter():
        try:
            cmdlines = process.cmdline()
            if 'mstsc' in cmdlines[0] and cmdlines[1] == "NLA.rdp":
                python_processes.append({
                    'pid': process.pid,
                    'params': cmdlines[1]
                })
        except Exception:
            pass

    for i in python_processes:
        print(i)
        os.kill(i["pid"], signal.SIGTERM)

def main():
    print("请选择一个功能：")
    print("1: 自动对RDPList.txt中的RDP地址进行NLA关闭检查(非1080p win11 请按说明修改代码适配),启动后请勿移动鼠标,")
    print("   结果将保存在result.txt中")
    print("2: 将对result.txt中的RDP地址进行手动复查，即将从第二行开始检查，每次检查将从result.txt中删除上一次的检查的RDP地址,")
    print("   若可利用攻击，请及时保存RDP地址，上一次运行功能2连接的RDP地址位于result.txt的第一行，下次运行功能2将删除本次RDP连接的地址")
    print("3: 一键关闭本程序启动的mstsc.exe,手动检查功能发现存在前台已关闭，后台程序继续运行的情况，建议尝试一定连接次数后执行一下")
    print("直接按Enter键默认选择功能2")

    while True:
        choice = input("请输入你的选择: ")
        if choice == '1':
            AutoCheck()
            print("检查完成，可以开始手动检查")
        elif choice == '2':
            ManualCheck()
        elif choice == '3':
            closeOtherRDPClient()
        else:
            ManualCheck()


if __name__ == "__main__":
    main()
