import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap import Style
from ttkbootstrap.widgets import Notebook, Frame, Label, Entry, Button, Combobox, Checkbutton
from tkinter import Text
import threading
import time
import os
import serial
import queue

class Controller:
    def __init__(self):
        self.out_file_entry = None
        self.gdb_file_entry = None
        self.gdb_file_button = None
        self.script_file_entry = None
        self.script_file_button = None
        self.serial_ports = []

    def register_out_file_widget(self, entry):
        self.out_file_entry = entry

    def register_gdb_file_widget(self, entry, button):
        self.gdb_file_entry = entry
        # self.gdb_file_button = button

    def register_script_file_widget(self, entry, button):
        self.script_file_entry = entry
        # self.script_file_button = button

    def register_serial_ports(self, serial_lists):
        self.serial_ports = serial_lists

    def get_out_file(self):
        return self.out_file_entry.get()

    def get_gdb_file(self):
        return self.gdb_file_entry.get()

    def get_script_file(self):
        return self.script_file_entry.get()

    def get_serial_port(self, index):
        if index < len(self.serial_ports):
            return self.serial_ports[index][0].get(), self.serial_ports[index][1].get()
        return None, None

class TestToolApp:
    def __init__(self):
        self.controller = Controller()
        # self.exc_file_path = ''
        self.window = ttk.Window(themename="superhero", title="Test Tool")
        self.window.geometry("1280x720")
        self.notebook = TestToolNotebook(self.window, self.controller)
        self.notebook.add_pages()

    def run(self):
        self.window.mainloop()

class TestToolNotebook:
    def __init__(self, master, controller):
        self.notebook = Notebook(master)
        self.page1 = TestToolCasePerform(self.notebook, controller)
        self.page2 = TestToolUpdateFirmware(self.notebook)

    def add_pages(self):
        self.notebook.add(self.page1.frame, text="集成测试")
        self.notebook.add(self.page2.frame, text="固件升级")
        self.notebook.pack(fill="both", expand=True)

class TestToolCasePerform:
    def __init__(self, master, controller):
        self.frame = Frame(master)
        self.frame_upper = TestToolControlPanel(self.frame, controller)    # 上半部分布局
        self.frame_lower = TestToolSerialPannel(self.frame, controller)    # 下半部分布局
        self.configure_layout()

    def configure_layout(self):
        # 配置页面1布局和组件
        self.frame_upper.frame.pack(pady=20, padx=20, fill="x")
        # 下部分：串口选择和日志框
        self.frame_lower.frame.pack(fill="both", expand=True, padx=20, pady=10)
        pass

class TestToolControlPanel:
    def __init__(self, master, controller):
        self.frame = Frame(master)
        self.frame_left = TestToolControlConfigPannel(self.frame, controller)
        self.frame_midle = TestToolControlRunCasePannel(self.frame, controller)
        self.frame_right = TestToolControlLogShowPannel(self.frame, controller)
        self.configure_layout()

    def configure_layout(self):
        self.frame_left.frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.frame_midle.frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.frame_right.frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)
        pass

class TestToolControlConfigPannel:
    def __init__(self, master, controller):
        self.frame = Frame(master)
        self.controller = controller

        # 第一行：OUT文件
        self.out_frame = Frame(self.frame)
        self.config_out_label = Label(self.out_frame, text="OUT文件")
        self.config_out_entry = Entry(self.out_frame, width=40)
        self.config_out_button = Button(self.out_frame, text="选择文件", command=lambda: self.select_file([("OUT Files", "*.out")], self.config_out_entry))
        self.controller.register_out_file_widget(self.config_out_entry)

        # 第二行：GDB脚本文件
        self.gdb_frame = Frame(self.frame)
        self.config_gdb_label = Label(self.gdb_frame, text="GDB配置")
        self.config_gdb_entry = Entry(self.gdb_frame, width=40)
        self.config_gdb_botton = Button(self.gdb_frame, text="选择文件", command=lambda: self.select_file([("OUT Files", "*.txt")], self.config_gdb_entry))
        self.edit_gdb_botton = Button(self.gdb_frame, text="编辑", command=lambda: self.edit_file(self.config_gdb_entry))
        self.controller.register_gdb_file_widget(self.config_gdb_entry, self.edit_gdb_botton)

        # 第三行：测试用例脚本
        self.script_frame = Frame(self.frame)
        self.config_script_label = Label(self.script_frame, text="测试用例")
        self.config_script_entry = Entry(self.script_frame, width=40)
        self.config_script_botton = Button(self.script_frame, text="打开文件", command=lambda: self.select_file([("OUT Files", "*.py")], self.config_script_entry))
        self.edit_script_botton = Button(self.script_frame, text="编辑", command=lambda: self.edit_file(self.config_script_entry))
        self.controller.register_script_file_widget(self.config_script_entry, self.edit_script_botton)

        self.configure_layout()

    def configure_layout(self):
        # 第一行布局
        self.out_frame.pack(side="top", fill="x", pady=5)
        self.config_out_label.pack(side="left")
        self.config_out_entry.pack(side="left", padx=10)
        self.config_out_button.pack(side="left")
        # 第二行布局
        self.gdb_frame.pack(side="top", fill="x", pady=5)
        self.config_gdb_label.pack(side="left")
        self.config_gdb_entry.pack(side="left", padx=10)
        self.config_gdb_botton.pack(side="left")
        self.edit_gdb_botton.pack(side="left", padx=10)
        # 第三行布局
        self.script_frame.pack(side="top", fill="x", pady=5)
        self.config_script_label.pack(side="left")
        self.config_script_entry.pack(side="left", padx=10)
        self.config_script_botton.pack(side="left")
        self.edit_script_botton.pack(side="left", padx=10)

    def select_file(self, filter_rule, file_path_entry):
        file = filedialog.askopenfilename(filetypes=filter_rule)
        if file:
            file_path_entry.delete(0, tk.END)
            file_path_entry.insert(0, file)

    def edit_file(self, file_path_entry):
        file = file_path_entry.get()
        if file:
            try:
                import subprocess
                subprocess.run(["notepad", file])  # Windows下默认使用记事本打开
            except Exception as e:
                messagebox.showerror("错误", f"打开文件失败: {e}")

    def open_out_file(self):
        file = filedialog.askopenfilename(filetypes=[("OUT Files", "*.out")])
        if file:
            self.config_out_entry.delete(0, tk.END)
            self.config_out_entry.insert(0, file)
    def open_gdb_file(self):
        pass
    def open_gdb_editor(self):
        pass
    def open_script_file(self):
        pass
    def open_script_editor(self):
        pass


class TestToolControlRunCasePannel:
    def __init__(self, master, controller):
        self.frame = Frame(master)
        self.controller = controller
        self.run_case_button = Button(self.frame, text="\n运行测试\n", command=self.run_testcase)
        self.configure_layout()

    def configure_layout(self):
        self.run_case_button.pack(side="right", anchor=tk.CENTER)

    def run_testcase(self):
        out_file_path = self.controller.out_file_entry.get()
        gdb_file_path = self.controller.gdb_file_entry.get()
        script_file_path = self.controller.script_file_entry.get()
        for serial_port in self.controller.serial_ports:
            print(serial_port)

        self.controller.serial_ports[0].serial_start_monitor()
        # for xxx in range(10):
        self.controller.serial_ports[0].serial_send("Hello.")
        self.controller.serial_ports[0].serial_send("Hello.")
        self.controller.serial_ports[0].serial_send("Hello.")
        self.controller.serial_ports[0].serial_send("Hello.")
        self.controller.serial_ports[0].serial_send("Hello.")
        self.controller.serial_ports[0].serial_send("Hello.")
        self.controller.serial_ports[0].serial_send("Hello.")
        self.controller.serial_ports[0].serial_send("Hello.")
        self.controller.serial_ports[0].serial_send("Hello.")
        self.controller.serial_ports[0].serial_send("Hello.")
        #     time.sleep(1)
        # self.controller.serial_ports[0].serial_stop_monitor()

class TestToolControlLogShowPannel:
    def __init__(self, master, controller):
        self.frame = Frame(master)
        self.log_show_text = Text(self.frame, wrap="word", height=6)
        self.configure_layout()
        self.LogShow("Hello...")

    def LogShow(self, message):
        count = 0
        while count < 10:
            time.sleep(1)
            count += 1
            self.log_show_text.insert(tk.END, f"Message test: {count} {message}\n")
            self.log_show_text.yview(tk.END)


    def configure_layout(self):
        self.log_show_text.pack(fill="both", expand=True)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)

class TestToolSerialPannel:
    def __init__(self, master, controller):
        self.frame = Frame(master)
        self.controller = controller
        self.serial_lists = []
        self.serial_nums = 3
        try:
            assert self.serial_nums >= 1
        except Exception as e:
            print("串口数量至少为1，用于AT指令下发")

        for serial_idx in range(self.serial_nums):
            self.serial_lists.append(TestToolSerialPort(self.frame, controller))
        
        self.controller.register_serial_ports(self.serial_lists)
        self.configure_layout()

    def configure_layout(self):
        self.frame.grid_rowconfigure(0, weight=1) # 垂直方向自动扩展
        for serial_idx in range(self.serial_nums):
            self.serial_lists[serial_idx].frame.grid(row=0, column=serial_idx, padx=10, pady=10, sticky="nsew")
            self.frame.grid_columnconfigure(serial_idx, weight=1) # 水平方向自动扩展

class TestToolSerialPort:
    def __init__(self, master, controller):
        self.controller = controller
        self.frame = Frame(master)
        self.serial_port = None
        self.serial_state = "Closed"
        self.serial_tx_queue = queue.Queue(maxsize = 10)
        self.serial_rx_queue = queue.Queue(maxsize = 10)

        # Serial Config Panel Frame.
        self.serial_config_frame = Frame(self.frame)
        self.label_serial = Label(self.serial_config_frame, text="串口")
        self.combo_serial = Combobox(self.serial_config_frame, values=["COM1", "COM2", "COM3"], width=10)
        self.label_baud = Label(self.serial_config_frame, text="波特率")
        self.combo_baud = Combobox(self.serial_config_frame, values=["9600", "115200", "19200"], width=10)
        self.check_logging = Checkbutton(self.serial_config_frame, text="文件日志")

        # Serial Trace Frame 
        self.serial_trace_frame = Frame(self.frame)
        self.log_box = Text(self.serial_trace_frame, wrap="word", height=10)

        self.configure_layout()

    def configure_layout(self):
        # For serial config frame.
        self.serial_config_frame.pack(side="top", fill="x", pady=5)
        self.label_serial.pack(side="left")
        self.combo_serial.pack(side="left", padx=10)
        self.label_baud.pack(side="left")
        self.combo_baud.pack(side="left", padx=10)
        self.check_logging.pack(side="left", padx=10)

        # For serial log show frame
        self.serial_trace_frame.pack(side="top", fill="both", expand=True)
        self.log_box.pack(fill="both", expand=True)

    def close_serial_port(self):
        # FIXME: Better add lock.
        if self.serial_state == "Closed":
            print("Serial was closed already.")
            # FIXME: Unlock.
            return
        self.serial_port.close()
        self.serial_state = "Closed"
        print("Serial was closed successfully.")
        # FIXME: Unlock.

    def open_serial_port(self):
        self.port = self.combo_serial.get()
        self.baud = self.combo_baud.get()
        # FIXME: Better add lock.
        if self.serial_state == "Open":
            # FIXME: Unlock.
            return
        try:
            self.serial_port = serial.Serial(self.port, self.baud, timeout=1)
            self.serial_state = "Open"
            print(f"Open serial success:")
        except serial.SerialException as e:
            self.serial_port = None
            print(f"Open serial failed: {e}")
        # FIXME: Unlock.
        return

    def serial_port_read(self):
        while True:
            # FIXME: Add lock.
            if self.serial_state == "Closed":
                # Unlock and stop read the serial.
                print("Serial was closed, stop read from serial")
                return
            if self.serial_port.in_waiting > 0:
                data = self.serial_port.read(self.serial_port.in_waiting) # FIXME: blocked?
                # Unlock
                self.serial_rx_queue.put("<--: " + data.decode('utf-8', errors='ignore'))
            # Unlock

    def serial_rx_message_show(self):
        while True:
            try:
                message = self.serial_rx_queue.get(timeout = 1)
            except queue.Empty:
                # FIXME: Lock
                if self.serial_state == "Closed":
                    # FIXME: Unlock
                    print("No more message received.")
                    return
                # FIXME: Unlock
                continue

            self.log_box.insert(tk.END, f"{message}\n")
            self.log_box.yview(tk.END)



    def serial_start_monitor(self):
        # First open the serial.
        try:
            self.open_serial_port()
        except Exception as e:
            return
        # Start a thread for reading from serial.
        self.rx_thread = threading.Thread(target = self.serial_port_read)
        self.rx_thread.start()
        print("Start serial_port_read")

        # Start a thread for sending message to serial.
        self.tx_thread = threading.Thread(target = self.serial_port_write)
        self.tx_thread.start()
        print("Start serial_port_write")

        # Start a thread for message show
        self.msgshow_thread = threading.Thread(target = self.serial_rx_message_show)
        self.msgshow_thread.start()
        print("Start serial_rx_message_show")

    def serial_stop_monitor(self):
        self.close_serial_port()
        self.rx_thread.join()
        self.tx_thread.join()
        self.msgshow_thread.join()
        # Close the serial
        # Clear the message queue.
        pass

    def serial_send(self, message):
        self.serial_tx_queue.put(message) # Try Exception for full

    def serial_port_write(self):
        while True:
            try:
                message = self.serial_tx_queue.get(timeout=1) # Try Exception for full
            except queue.Empty:
                continue
            try:
                self.serial_rx_queue.put("-->: " + message)
            except queue.Full:
                # Discard this message.
                continue
            try:
                self.serial_port.write((message).encode())
            except serial.SerialException as e:
                print(f"Serial send error: {e}")

            # FIXME: Lock
            if self.serial_state == "Closed":
                # FIXME: Unlock
                return
            # FIXME: Unlock

class TestToolUpdateFirmware:
    def __init__(self, master):
        self.frame = Frame(master)
        self.configure_layout()

    def configure_layout(self):
        # 配置页面2布局和组件
        pass

if __name__ == '__main__':
    app = TestToolApp()
    app.run()
