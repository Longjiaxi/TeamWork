from PySide6.QtWidgets import (QDialog, QWidget, QHBoxLayout, QVBoxLayout,
                                 QGroupBox, QLineEdit, QPushButton, QLabel, QTextEdit, QRadioButton)
from PySide6.QtCore import Qt
import subprocess
import os
from datetime import datetime

class GitBackupWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("项目代码自动备份同步（Gitee）")
        self.resize(1500, 900)
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        self.setLayout(main_layout)
        main_layout.setSpacing(24)
        main_layout.setContentsMargins(24, 24, 24, 24)

        # ========== 左侧：Git仓库基础配置 ==========
        left_group = QGroupBox()
        left_group.setStyleSheet("""
            QGroupBox {
                background-color: #ffffff;
                border-radius: 14px;
                border: 1px solid #e5e7eb;
            }
        """)
        left_layout = QVBoxLayout(left_group)
        left_layout.setContentsMargins(28, 28, 28, 28)
        left_layout.setSpacing(18)

        # 蓝色通栏标题
        blue_title = QLabel("Git仓库基础配置")
        blue_title.setStyleSheet("""
            background-color: #1677ff;
            color: white;
            font-size: 16pt;
            font-weight: bold;
            padding: 14px 18px;
            border-radius: 10px;
        """)
        left_layout.addWidget(blue_title)

        # 表单标签和输入框统一加大
        label_style = "font-size:11pt; font-weight:500; color:#303133;"
        input_style = """
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #dcdfe6;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 11pt;
                color: #303133;
                selection-background-color: #1677ff;
            }
            QLineEdit:focus {
                border: 1px solid #1677ff;
            }
        """

        label_project = QLabel("项目本地源码路径")
        label_project.setStyleSheet(label_style)
        left_layout.addWidget(label_project)
        self.edit_project_path = QLineEdit(r"")
        self.edit_project_path.setPlaceholderText("填写项目根目录，程序从此目录读取代码上传")
        self.edit_project_path.setStyleSheet(input_style)
        left_layout.addWidget(self.edit_project_path)

        label_name = QLabel("Git用户名")
        label_name.setStyleSheet(label_style)
        left_layout.addWidget(label_name)
        self.edit_git_name = QLineEdit("")
        self.edit_git_name.setStyleSheet(input_style)
        left_layout.addWidget(self.edit_git_name)

        label_email = QLabel("Git邮箱")
        label_email.setStyleSheet(label_style)
        left_layout.addWidget(label_email)
        self.edit_git_email = QLineEdit("")
        self.edit_git_email.setStyleSheet(input_style)
        left_layout.addWidget(self.edit_git_email)

        label_url = QLabel("仓库地址")
        label_url.setStyleSheet(label_style)
        left_layout.addWidget(label_url)
        self.edit_repo_url = QLineEdit("")
        self.edit_repo_url.setStyleSheet(input_style)
        left_layout.addWidget(self.edit_repo_url)

        label_token = QLabel("Gitee私人令牌(token)")
        label_token.setStyleSheet(label_style)
        left_layout.addWidget(label_token)
        self.edit_token = QLineEdit()
        self.edit_token.setEchoMode(QLineEdit.Password)
        self.edit_token.setPlaceholderText("请输入 Gitee 私人令牌")
        self.edit_token.setStyleSheet(input_style)
        left_layout.addWidget(self.edit_token)

        label_commit = QLabel("自动备份默认提交说明")
        label_commit.setStyleSheet(label_style)
        left_layout.addWidget(label_commit)
        self.edit_commit_msg = QLineEdit("修改：模型api密钥V1.2.6")
        self.edit_commit_msg.setPlaceholderText("定时同步自动拼接时间戳，例：定时自动备份 2026-08-11 17:20")
        self.edit_commit_msg.setStyleSheet(input_style)
        left_layout.addWidget(self.edit_commit_msg)

        left_layout.addStretch(1)

        # 保存配置按钮加大
        self.btn_save_config = QPushButton("保存配置")
        self.btn_save_config.setStyleSheet("""
            QPushButton {
                background-color: #1677ff;
                color: white;
                font-size: 14pt;
                font-weight: bold;
                padding: 14px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #409eff;
            }
        """)
        left_layout.addWidget(self.btn_save_config)

        # ========== 右侧区域 ==========
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(18)

        card_title_style = """
            background-color: %s;
            color: white;
            font-size: 14pt;
            font-weight: bold;
            padding: 12px 16px;
            border-radius: 8px;
        """

        # 卡片1 手动一键推送备份
        card1 = QGroupBox()
        card1.setStyleSheet("""
            QGroupBox {
                background-color: #ffffff;
                border-radius: 14px;
                border: 1px solid #e5e7eb;
            }
        """)
        card1_layout = QVBoxLayout(card1)
        card1_layout.setContentsMargins(24, 24, 24, 24)
        card1_layout.setSpacing(16)

        card1_title = QLabel("手动一键推送备份")
        card1_title.setStyleSheet(card_title_style % "#222222")
        card1_layout.addWidget(card1_title)

        label_manual = QLabel("提交备注信息")
        label_manual.setStyleSheet(label_style)
        card1_layout.addWidget(label_manual)
        self.edit_manual_msg = QLineEdit()
        self.edit_manual_msg.setPlaceholderText("请输入本次提交备注")
        self.edit_manual_msg.setStyleSheet(input_style)
        card1_layout.addWidget(self.edit_manual_msg)

        self.btn_push = QPushButton("立即推送至Gitee")
        self.btn_push.setStyleSheet("""
            QPushButton {
                background-color: #222222;
                color: white;
                font-size: 13pt;
                font-weight: bold;
                padding: 12px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        card1_layout.addWidget(self.btn_push)
        right_layout.addWidget(card1)

        # 卡片2 推送运行日志
        card2 = QGroupBox()
        card2.setStyleSheet("""
            QGroupBox {
                background-color: #ffffff;
                border-radius: 14px;
                border: 1px solid #e5e7eb;
            }
        """)
        card2_layout = QVBoxLayout(card2)
        card2_layout.setContentsMargins(24, 24, 24, 24)
        card2_layout.setSpacing(16)

        card2_title = QLabel("推送运行日志")
        card2_title.setStyleSheet(card_title_style % "#00b8d9")
        card2_layout.addWidget(card2_title)

        self.log_text = QTextEdit()
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #000000;
                color: #00ff00;
                font-size: 11pt;
                border-radius: 8px;
                padding: 10px;
                border: none;
            }
        """)
        card2_layout.addWidget(self.log_text, stretch=1)
        right_layout.addWidget(card2, stretch=1)

        # 卡片3 自动定时同步
        card3 = QGroupBox()
        card3.setStyleSheet("""
            QGroupBox {
                background-color: #f5f5f5;
                border-radius: 14px;
                border: 1px solid #e5e7eb;
            }
        """)
        card3_layout = QVBoxLayout(card3)
        card3_layout.setContentsMargins(24, 24, 24, 24)
        card3_layout.setSpacing(16)

        card3_title = QLabel("自动定时同步（间隔2分钟自动推送）")
        card3_title.setStyleSheet(card_title_style % "#606c76")
        card3_layout.addWidget(card3_title)

        self.radio_off = QRadioButton("自动同步已关闭")
        self.radio_off.setChecked(True)
        self.radio_off.setStyleSheet("font-size:11pt; spacing:8px;")
        card3_layout.addWidget(self.radio_off)

        self.btn_auto_sync = QPushButton("开启自动同步")
        self.btn_auto_sync.setStyleSheet("""
            QPushButton {
                background-color: #009440;
                color: white;
                font-size: 13pt;
                font-weight: bold;
                padding: 12px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #00ab4b;
            }
        """)
        card3_layout.addWidget(self.btn_auto_sync)
        right_layout.addWidget(card3)

        # 左右1:1均分宽度
        main_layout.addWidget(left_group, stretch=1)
        main_layout.addWidget(right_widget, stretch=1)

        # 绑定按钮事件
        self.btn_push.clicked.connect(self.git_push)
        self.btn_save_config.clicked.connect(self.save_config)

    def log(self, msg):
        """日志输出"""
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.append(f"[{time_str}] {msg}")

    def run_git_cmd(self, cmd_list, work_dir):
        """执行git命令，返回输出"""
        try:
            result = subprocess.run(
                cmd_list,
                cwd=work_dir,
                capture_output=True,
                text=True,
                encoding="utf-8"
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            return -1, "", str(e)

    def git_push(self):
        """一键推送逻辑"""
        project_path = self.edit_project_path.text().strip()
        git_name = self.edit_git_name.text().strip()
        git_email = self.edit_git_email.text().strip()
        repo_url = self.edit_repo_url.text().strip()
        token = self.edit_token.text().strip()
        commit_msg = self.edit_manual_msg.text().strip() or self.edit_commit_msg.text().strip()

        if not os.path.isdir(project_path):
            self.log("❌ 错误：项目路径不存在！")
            return
        if not repo_url:
            self.log("❌ 错误：仓库地址不能为空！")
            return

        self.log("======= 开始备份 =======")
        # 设置用户名邮箱
        self.run_git_cmd(["git", "config", "user.name", git_name], project_path)
        self.run_git_cmd(["git", "config", "user.email", git_email], project_path)

        # 拼接带token的gitee地址
        if token:
            if repo_url.startswith("https://gitee.com"):
                repo_url_with_token = repo_url.replace("https://", f"https://{token}@")
                self.run_git_cmd(["git", "remote", "set-url", "origin", repo_url_with_token], project_path)

        # add -> commit -> push
        code, out, err = self.run_git_cmd(["git", "add", "."], project_path)
        self.log(out if out else err)
        if code != 0:
            self.log("⚠️ git add 执行完成")

        code, out, err = self.run_git_cmd(["git", "commit", "-m", commit_msg], project_path)
        self.log(out if out else err)

        code, out, err = self.run_git_cmd(["git", "push", "origin", "main"], project_path)
        self.log(out if out else err)
        if code == 0:
            self.log("✅ 推送成功！")
        else:
            self.log(f"❌ 推送失败: {err}")

    def save_config(self):
        """简单保存配置到本地json"""
        import json
        cfg = {
            "project_path": self.edit_project_path.text(),
            "git_name": self.edit_git_name.text(),
            "git_email": self.edit_git_email.text(),
            "repo_url": self.edit_repo_url.text(),
            "token": self.edit_token.text(),
            "default_msg": self.edit_commit_msg.text()
        }
        with open("git_config.json", "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
        self.log("✅ 配置已保存到 git_config.json")
