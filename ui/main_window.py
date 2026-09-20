from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QApplication,
    QPushButton,
    QFrame,
    QLabel,
    QDialog,
    QComboBox
)
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import QThread, Signal, Qt, QPropertyAnimation, QEasingCurve, QTimer
from ui.sidebar import Sidebar
from ui.title_bar import TitleBar
from ui.input_bar import InputBar

from ui.chat_area import ChatArea

from ui.ai_platform_popup import AiPlatformPopup


from PySide6.QtWidgets import QFileDialog
import os
from PySide6.QtWidgets import QMessageBox
from ui.chat_area import ChatArea


class AIRequestThread(QThread):
    """AI请求线程【对接通义千问】"""
    stream_signal = Signal(str)
    finish_signal = Signal(str)

    def __init__(self, context_list, prompt):
        super().__init__()
        self.context = context_list
        self.user_prompt = prompt

    def run(self):
        import requests
        api_key = "sk-ws-H.PHLIIYE.AKpG.MEUCIHwN-veYrNHmZ2apoLGGWjHRVgxygPuZuASSkW82wXYdAiEA67G3MSICyubQ9wvKC-Zigzqdl2PHyysJDt1nfQkRLVg"
        url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        messages = self.context.copy()
        system_msg = {"role": "system",
                      "content": "你是中文AI助手，所有回答必须使用中文，简洁清晰地回答用户问题。"}
        messages.insert(0, system_msg)
        messages.append({"role": "user", "content": self.user_prompt})
        data = {
            "model": "qwen-turbo",
            "messages": messages
        }
        try:
            resp = requests.post(url, headers=headers, json=data)
            res_json = resp.json()
            ai_full_text = res_json["choices"][0]["message"]["content"]
        except Exception as e:
            ai_full_text = f"请求异常：{str(e)}"
        self.finish_signal.emit(ai_full_text)


class MainWindow(QMainWindow):
    # ====================== 主题QSS样式定义 ======================

    STYLE_LIGHT = """ QMainWindow{background-color:#ffffff;} QWidget#ChatArea, QWidget#msg_container{background:#ffffff;} QWidget{background:#ffffff;color:#222222;} QPushButton{background:#f0f0f0;color:#111;border-radius:4px;padding:4px;} QPushButton:hover{background:#e2e2e2;} QPushButton#export_btn{background-color:#ffffff;border:1px solid #d9d9d9;color:#333333;} QPushButton#export_btn:hover{background-color:#f0f7ff;border-color:#409eff;} QLabel#role_label{color:#888888;background-color:#f5f5f5;border:1px solid #e5e5e5;border-radius:6px;padding:2px 8px;} QLabel#time_label{color:#999999;} QLabel{color:#222222;} QFrame{background:#f8f8f8;} #TitleBar{background:#f3f3f3;} #InputBar{background-color:#ffffff;} """

    STYLE_DARK = """ QMainWindow{background-color:#1e1e1e;} QWidget#ChatArea, QWidget#msg_container{background:#252525;} QWidget{background:#1e1e1e;color:#eeeeee;} QPushButton{background:#333333;color:#fff;border-radius:4px;padding:4px;} QPushButton:hover{background:#444444;} QPushButton#export_btn{background-color:#333333;border:1px solid #555555;color:#eee;} QPushButton#export_btn:hover{background-color:#404b58;border-color:#409eff;} QLabel#role_label{color:#cccccc;background-color:#333333;border:1px solid #444444;border-radius:6px;padding:2px 8px;} QLabel#time_label{color:#aaaaaa;} QLabel{color:#eeeeee;} QFrame{background:#2b2b2b;} #TitleBar{background:#2d2d2d;} #InputBar{background-color:#252525;} """

    STYLE_LIGHT = """
    QMainWindow{background-color:#ffffff;}
    QWidget#ChatArea, QWidget#msg_container{background:#ffffff;}
    QWidget{background:#ffffff;color:#222222;}
    QPushButton{background:#f0f0f0;color:#111;border-radius:4px;padding:4px;}
    QPushButton:hover{background:#e2e2e2;}
    QPushButton#export_btn{background-color:#ffffff;border:1px solid #d9d9d9;color:#333333;}
    QPushButton#export_btn:hover{background-color:#f0f7ff;border-color:#409eff;}
    QLabel#role_label{color:#888888;background-color:#f5f5f5;border:1px solid #e5e5e5;border-radius:6px;padding:2px 8px;}
    QLabel#time_label{color:#999999;}
    QLabel{color:#222222;}
    QFrame{background:#f8f8f8;}
    #TitleBar{background:#f3f3f3;}
    #InputBar{background-color:#ffffff;}
    """

    STYLE_DARK = """
    QMainWindow{background-color:#1e1e1e;}
    QWidget#ChatArea, QWidget#msg_container{background:#252525;}
    QWidget{background:#1e1e1e;color:#eeeeee;}
    QPushButton{background:#333333;color:#fff;border-radius:4px;padding:4px;}
    QPushButton:hover{background:#444444;}
    QPushButton#export_btn{background-color:#333333;border:1px solid #555555;color:#eee;}
    QPushButton#export_btn:hover{background-color:#404b58;border-color:#409eff;}
    QLabel#role_label{color:#cccccc;background-color:#333333;border:1px solid #444444;border-radius:6px;padding:2px 8px;}
    QLabel#time_label{color:#aaaaaa;}
    QLabel{color:#eeeeee;}
    QFrame{background:#2b2b2b;}
    #TitleBar{background:#2d2d2d;}
    #InputBar{background-color:#252525;}
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Chat")
        self.setWindowIcon(QIcon("res/icon.png"))
        self.resize(1200, 800)
        self.batch_mode = False
        self.ocr_engine = None
        self.sidebar_expanded = True
        self.sidebar_origin_width = 200
        self.is_dark_mode = False
        self.current_editing_chat_item = None
        self.conversation_store = {}

        # 新增：打字动画定时器
        self.type_timer = QTimer()
        self.type_timer.timeout.connect(self.type_one_char)
        self.type_text_buffer = ""
        self.type_index = 0

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.title_bar = TitleBar()
        self.title_bar.switch_theme_signal.connect(self.change_global_theme)
        # =========绑定加号按钮信号（使用原有add_tab_clicked，修复报错）=========
        self.title_bar.add_tab_clicked.connect(self.show_ai_popup)
        main_layout.addWidget(self.title_bar)

        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(0)
        main_layout.addLayout(h_layout)

        self.sidebar = Sidebar()
        h_layout.addWidget(self.sidebar)
        self.sidebar.menu_clicked.connect(self.on_sidebar_menu)

        #self.sidebar.menu_btn.clicked.connect(self.on_toggle_batch)

        # 右侧分割线


        divider = QFrame()
        divider.setFixedWidth(1)
        divider.setStyleSheet("background:#cccccc;")
        h_layout.addWidget(divider)

        chat_area = QWidget()
        chat_layout = QVBoxLayout(chat_area)
        chat_layout.setContentsMargins(12, 12, 12, 12)
        chat_layout.setSpacing(10)

        self.chat_display = ChatArea()
        chat_layout.addWidget(self.chat_display, stretch=1)

        # ✅ 已删除原来遮挡界面的多余空白QWidget！

        self.input_bar = InputBar()
        self.input_bar.setObjectName("InputBar")
        chat_layout.addWidget(self.input_bar)

        h_layout.addWidget(chat_area, stretch=1)

        # =========实例AI弹窗，父容器是chat_area，只覆盖右侧=========
        self.ai_popup = AiPlatformPopup(chat_area)

        # =====================信号绑定=====================
        self.sidebar.new_chat_clicked.connect(self.new_chat)
        self.sidebar.chat_switch.connect(self.switch_conversation)
        self.sidebar.chat_delete.connect(self.delete_conversation)

        self.input_bar.sig_send_text.connect(self.on_send_text)
        self.input_bar.sig_file_selected.connect(self.on_select_file)
        self.input_bar.sig_img_selected.connect(self.on_select_image)
        self.input_bar.sig_voice_click.connect(self.on_voice_input)
        self.input_bar.sig_clear_click.connect(self.on_clear_chat)

        self.batch_mode = False
        self.sidebar.menu_btn.clicked.connect(self.on_toggle_batch)

        # 默认加载浅色模式
        self.change_global_theme(False)

        # 底部批量操作栏
        self.batch_bar = QWidget()
        batch_layout = QHBoxLayout(self.batch_bar)
        self.batch_bar.setVisible(False)

        self.btn_select_all = QPushButton("全选")
        self.btn_batch_del = QPushButton("确定删除")
        self.btn_cancel = QPushButton("取消")

        self.btn_select_all.clicked.connect(self.sidebar.toggle_select_all)
        self.btn_batch_del.clicked.connect(self.batch_delete)
        self.btn_cancel.clicked.connect(self.cancel_batch)

        batch_layout.addStretch()
        batch_layout.addWidget(self.btn_select_all)
        batch_layout.addWidget(self.btn_batch_del)
        batch_layout.addWidget(self.btn_cancel)
        main_layout.addWidget(self.batch_bar)


    # =========【新增函数：显示AI平台弹窗】=========
    def show_ai_popup(self):
        self.ai_popup.update_size(self.ai_popup.parent().rect())
        self.ai_popup.show()

    # =========【新增：窗口缩放事件，弹窗跟随窗口大小】=========
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "ai_popup") and self.ai_popup.isVisible():
            self.ai_popup.update_size(self.ai_popup.parent().rect())

    # =========新建对话：自动寻找最小空缺编号=========

    # 新增：逐字渲染回调
    def type_one_char(self):
        if self.type_index < len(self.type_text_buffer):
            self.chat_display.append_ai_char(self.type_text_buffer[self.type_index])
            self.type_index += 1
        else:
            self.type_timer.stop()


    def new_chat(self):
        self.chat_display.clear()
        self.context_history = []
        self.current_editing_chat_item = None

        name_list = []
        for i in range(self.sidebar.count()):
            item = self.sidebar.item(i)
            widget = self.sidebar.itemWidget(item)
            if widget and hasattr(widget, "chat_name"):
                try:
                    num = int(widget.chat_name.replace("对话", ""))
                    name_list.append(num)
                except:
                    pass
        min_id = 1
        while min_id in name_list:
            min_id += 1
        new_name = f"对话{min_id}"
        self.sidebar.add_chat(new_name)

        new_item = self.sidebar.item(self.sidebar.count() - 1)
        self.current_editing_chat_item = new_item
        self.conversation_store[new_name] = []
        print(f"📝新建对话：{new_name}")

    def delete_conversation(self, chat_name):
        for i in range(self.sidebar.count() - 1, -1, -1):
            item = self.sidebar.item(i)
            widget = self.sidebar.itemWidget(item)
            if widget and hasattr(widget, "chat_name") and widget.chat_name == chat_name:
                self.sidebar.takeItem(i)
                del item
                print(f"✅已删除对话：{chat_name}")
                break

        if chat_name in self.conversation_store:
            del self.conversation_store[chat_name]
            print(f"🗑️ 已清除对话存储：{chat_name}")

        self.chat_display.clear()
        self.context_history = []
        self.current_editing_chat_item = None

    def switch_conversation(self, chat_name):
        self.chat_display.clear()
        self.context_history = []

        for i in range(self.sidebar.count()):
            item = self.sidebar.item(i)
            widget = self.sidebar.itemWidget(item)
            if hasattr(widget, "chat_name") and widget.chat_name == chat_name:
                self.current_editing_chat_item = item
                break

        print("切换对话，保存当前编辑item：", self.current_editing_chat_item)
        print(f"【DEBUG】切换对话名称：{chat_name}")
        print(f"【DEBUG】全部对话存储keys：{list(self.conversation_store.keys())}")

        if chat_name in self.conversation_store:
            msg_list = self.conversation_store[chat_name]
            print(f"【DEBUG】读取到消息列表长度：{len(msg_list)}")
            self.context_history = msg_list.copy()
            for msg in msg_list:
                is_user = msg["role"] == "user"
                self.add_chat_bubble(msg["content"], is_user=is_user)
        else:
            print(f"【DEBUG】警告：{chat_name} 不在conversation_store中！")

    def toggle_sidebar(self):
        pass

    # ====================== 全局主题切换函数 ======================
    def change_global_theme(self, is_dark: bool):
        self.is_dark_mode = is_dark
        if is_dark:
            self.setStyleSheet(self.STYLE_DARK)

            # 弹窗深色样式
            self.ai_popup.setStyleSheet("""
                #AiPlatformPopup{background-color:#252525;}
                QPushButton{background:#333;border:1px solid #555;color:#eee;}
                QPushButton:hover{background:#404b58;border-color:#409eff;}
                QLabel{color:#eee;}
            """)
        else:
            self.setStyleSheet(self.STYLE_LIGHT)
            # 弹窗浅色样式
            self.ai_popup.setStyleSheet("""
                #AiPlatformPopup{background-color:#ffffff;}
                QPushButton{background:#f8f8f8;border:1px solid #cccccc;color:#222;}
                QPushButton:hover{background:#e8f2ff;border-color:#409eff;}
                QLabel{color:#222;}
            """)

            self.title_bar.theme_btn.setText("🌙 深色模式")
        else:
            self.setStyleSheet(self.STYLE_LIGHT)
            self.title_bar.theme_btn.setText("☀ 浅色模式")

    def toggle_theme(self):
        pass


    def show_batch_bar(self):
        self.batch_bar.setVisible(True)

    def hide_batch_bar(self):
        self.batch_bar.setVisible(False)

    def on_toggle_batch(self):
        self.batch_mode = not self.batch_mode
        print(f"【MAIN DEBUG】主窗口批量模式 {self.batch_mode}")
        if self.batch_mode:
            self.show_batch_bar()
        else:
            self.hide_batch_bar()
        self.sidebar.set_all_chat_item_batch(self.batch_mode)

    def batch_delete(self, selected_names):
        if not selected_names:
            QMessageBox.information(self, "提示", "请勾选要删除的对话！")
            return
        ret = QMessageBox.question(self, "确认删除", f"确定删除选中{len(selected_names)}条对话吗？",
                                   QMessageBox.Yes | QMessageBox.No)
        if ret == QMessageBox.Yes:
            for name in selected_names:
                self.delete_conversation(name)

        self.sidebar.set_all_chat_item_batch(False)
        self.batch_mode = False
        self.hide_batch_bar()
        self.sidebar.close_batch_mode()

    def on_sidebar_menu(self, batch_enable):
        if batch_enable:
            self.show_batch_bar()
        else:
            self.hide_batch_bar()

    def cancel_batch(self):
        self.batch_mode = False
        self.sidebar.set_all_chat_item_batch(False)
        self.hide_batch_bar()

    def on_send_text(self, text):
        print("发送文本：", text)

        if self.current_editing_chat_item is None:
            new_title = text[:15]
            chat_widget = self.sidebar.add_chat(new_title)
            self.current_editing_chat_item = self.sidebar.item(self.sidebar.count() - 1)
            self.context_history = []
            self.conversation_store[new_title] = []

        self.add_chat_bubble(text, is_user=True)
        self.context_history.append({"role": "user", "content": text})

        if len(self.context_history) == 1 and self.current_editing_chat_item is not None:
            chat_item_widget = self.sidebar.itemWidget(self.current_editing_chat_item)
            if chat_item_widget and hasattr(chat_item_widget, "btn_name"):
                old_title = chat_item_widget.chat_name
                new_title = text[:15]
                chat_item_widget.chat_name = new_title
                chat_item_widget.btn_name.setText(new_title)
                print(f"对话自动重命名：{old_title} → {new_title}")

                if old_title in self.conversation_store:
                    self.conversation_store[new_title] = self.conversation_store.pop(old_title)

        if self.current_editing_chat_item is not None:
            chat_item_widget = self.sidebar.itemWidget(self.current_editing_chat_item)
            chat_name = chat_item_widget.chat_name
            self.conversation_store[chat_name] = self.context_history.copy()

        # 展示思考动画
        self.chat_display.show_thinking()

        self.ai_thread = AIRequestThread(self.context_history, text)
        self.ai_thread.finish_signal.connect(self.receive_ai_finish)
        self.ai_thread.start()

    def on_select_file(self, file_path):
        print("选择文件：", file_path)

    def on_select_image(self, img_path):
        print("选择图片：", img_path)

    def on_voice_input(self):
        print("语音输入点击")

    def on_clear_chat(self):
        print("清空对话")
        self.chat_display.clear()
        self.context_history = []

        if self.current_editing_chat_item is not None:
            widget = self.sidebar.itemWidget(self.current_editing_chat_item)
            chat_name = widget.chat_name
            self.conversation_store[chat_name] = []

    def add_chat_bubble(self, text, is_user):
        self.chat_display.add_bubble(text, is_user)

    def receive_ai_stream(self, chunk_text):
        print("AI片段：", chunk_text)

    def receive_ai_finish(self, full_text):
        # 隐藏思考动画
        self.chat_display.hide_thinking()
        # 开启逐字打字
        self.type_text_buffer = full_text
        self.type_index = 0
        # =========【这里控制打字速度，单位毫秒，数字越大越慢】=========
        self.type_timer.setInterval(80)
        # ==========================================================
        self.chat_display.create_empty_ai_bubble()
        self.type_timer.start()

        self.context_history.append({"role": "assistant", "content": full_text})

        if self.current_editing_chat_item is not None:
            widget = self.sidebar.itemWidget(self.current_editing_chat_item)
            chat_name = widget.chat_name
            self.conversation_store[chat_name] = self.context_history.copy()

    def handle_ai_message(self):
        pass

    def upload_file(self):
        pass

    def speech_recognize(self):
        pass

    def closeEvent(self, event):
        pass


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
