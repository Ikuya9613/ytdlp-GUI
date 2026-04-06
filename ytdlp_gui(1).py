import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yt_dlp
import threading
import json

class YtDlpGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Python 進階影音下載器 (yt-dlp)")
        self.root.geometry("650x550")
        
        # 儲存分析出來的格式資料
        self.video_formats = []
        self.audio_formats = []
        self.info_dict = None

        # --- 第一區：URL 輸入與分析 ---
        url_frame = ttk.LabelFrame(root, text=" 1. 輸入影片網址 ", padding=10)
        url_frame.pack(fill="x", padx=15, pady=10)

        ttk.Label(url_frame, text="YouTube URL:").pack(side="left", padx=(0, 10))
        self.url_entry = ttk.Entry(url_frame, width=50)
        self.url_entry.pack(side="left", expand=True, fill="x", padx=(0, 10))
        
        self.analyze_btn = ttk.Button(url_frame, text="分析連結", command=self.start_analyze_thread)
        self.analyze_btn.pack(side="left")

        # --- 第二區：影片資訊顯示 ---
        info_frame = ttk.Frame(root, padding=(15, 0))
        info_frame.pack(fill="x")
        self.title_label = ttk.Label(info_frame, text="影片標題: (尚未分析)", font=("Helvetica", 10, "bold"), wraplength=600)
        self.title_label.pack(anchor="w")

        # --- 第三區：格式選擇選單 ---
        options_frame = ttk.LabelFrame(root, text=" 2. 選擇下載格式 ", padding=10)
        options_frame.pack(fill="x", padx=15, pady=10)

        # 影片畫質選單
        ttk.Label(options_frame, text="影片畫質:").grid(row=0, column=0, sticky="w", pady=5)
        self.video_combo = ttk.Combobox(options_frame, state="disabled", width=50)
        self.video_combo.grid(row=0, column=1, sticky="we", padx=(10, 0))
        self.video_combo.set("請先點擊'分析連結'")

        # 音頻音質選單
        ttk.Label(options_frame, text="音頻音質:").grid(row=1, column=0, sticky="w", pady=5)
        self.audio_combo = ttk.Combobox(options_frame, state="disabled", width=50)
        self.audio_combo.grid(row=1, column=1, sticky="we", padx=(10, 0))
        self.audio_combo.set("請先點擊'分析連結'")
        
        # 封裝格式 (Container)
        ttk.Label(options_frame, text="封裝格式:").grid(row=2, column=0, sticky="w", pady=5)
        self.container_combo = ttk.Combobox(options_frame, values=["mp4", "mkv"], width=10)
        self.container_combo.current(0) # 預設 MP4
        self.container_combo.grid(row=2, column=1, sticky="w", padx=(10, 0))

        options_frame.columnconfigure(1, weight=1)

        # --- 第四區：儲存路徑 ---
        path_frame = ttk.Frame(root, padding=(15, 0))
        path_frame.pack(fill="x")
        ttk.Label(path_frame, text="儲存至:").pack(side="left", padx=(0, 10))
        self.path_entry = ttk.Entry(path_frame)
        self.path_entry.pack(side="left", expand=True, fill="x", padx=(0, 10))
        self.path_entry.insert(0, "./downloads") # 預設路徑
        ttk.Button(path_frame, text="瀏覽...", command=self.browse_path).pack(side="left")

        # --- 第五區：下載按鈕與進度 ---
        ttk.Separator(root, orient="horizontal").pack(fill="x", padx=15, pady=15)
        
        self.download_btn = ttk.Button(root, text="開始下載", command=self.start_download_thread, state="disabled")
        self.download_btn.pack(pady=(0, 10))
        
        self.progress_bar = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate")
        self.progress_bar.pack(padx=15, pady=5)
        
        self.status_label = ttk.Label(root, text="準備就緒")
        self.status_label.pack(pady=5)

    # ==========================
    #      核心邏輯部分
    # ==========================

    def browse_path(self):
        path = filedialog.askdirectory()
        if path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)

    def start_analyze_thread(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("警告", "請輸入 YouTube 連結！")
            return
        
        # 使用執行緒避免介面卡頓
        self.status_label.config(text="正在分析中，請稍候...")
        self.analyze_btn.config(state="disabled")
        self.download_btn.config(state="disabled")
        threading.Thread(target=self.analyze_url, args=(url,), daemon=True).start()

    def analyze_url(self, url):
        ydl_opts = {
            'skip_download': True, # 關鍵：不下載檔案
            'quiet': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.info_dict = ydl.extract_info(url, download=False)
            
            # 取得標題
            title = self.info_dict.get('title', 'Unknown')
            self.root.after(0, lambda: self.title_label.config(text=f"影片標題: {title}"))
            
            # 解析格式
            formats = self.info_dict.get('formats', [])
            self.video_formats = []
            self.audio_formats = []
            
            # 預設選項 (自動選擇)
            v_options = ["最高畫質 (影像only)"]
            a_options = ["最高音質 (音頻only)"]
            
            self.video_formats.append({'id': 'bv', 'desc': 'Best Video'})
            self.audio_formats.append({'id': 'ba', 'desc': 'Best Audio'})

            # 迴圈解析所有可用格式
            for f in formats:
                f_id = f.get('format_id')
                ext = f.get('ext')
                note = f.get('format_note', '')
                
                # 分離影片流 (無聲)
                if f.get('vcodec') != 'none' and f.get('acodec') == 'none':
                    res = f.get('resolution', f'{f.get("width")}x{f.get("height")}')
                    fps = f.get('fps', '')
                    fps_str = f'{fps}fps' if fps else ''
                    v_options.append(f"{res} ({ext}) - {note} {fps_str}".strip())
                    self.video_formats.append({'id': f_id, 'desc': f"{res} ({ext})"})
                    
                # 分離音頻流
                elif f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                    abr = f.get('abr', 0)
                    a_options.append(f"{ext} - {note} ({abr}kbps)".strip())
                    self.audio_formats.append({'id': f_id, 'desc': f"{ext} ({abr}kbps)"})

            # 更新 GUI 選單 (必須在主執行緒執行)
            self.root.after(0, lambda: self.update_combos(v_options, a_options))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("錯誤", f"分析連結失敗: {str(e)}"))
            self.root.after(0, lambda: self.status_label.config(text="分析失敗。"))
            self.root.after(0, lambda: self.analyze_btn.config(state="normal"))

    def update_combos(self, v_opts, a_opts):
        self.video_combo.config(values=v_opts, state="readonly")
        self.video_combo.current(0)
        
        self.audio_combo.config(values=a_opts, state="readonly")
        self.audio_combo.current(0)
        
        self.analyze_btn.config(state="normal")
        self.download_btn.config(state="normal")
        self.status_label.config(text="分析完成，請選擇格式。")

    def start_download_thread(self):
        v_idx = self.video_combo.current()
        a_idx = self.audio_combo.current()
        
        # 組合 yt-dlp 格式字串
        v_id = self.video_formats[v_idx]['id']
        a_id = self.audio_formats[a_idx]['id']
        format_str = f"{v_id}+{a_id}" # 例如: "137+140"
        
        container = self.container_combo.get()
        out_path = self.path_entry.get().strip()
        
        ydl_opts = {
            'format': format_str,
            'outtmpl': f'{out_path}/%(title)s.%(ext)s',
            'merge_output_format': container, # 強制 FFmpeg 合併為指定格式
            'progress_hooks': [self.progress_hook], # 設定進度條回調函數
            # 'ffmpeg_location': 'C:/ffmpeg/bin', # 如果 FFmpeg 沒加到 PATH，可以在此指定位置
        }
        
        self.status_label.config(text="開始下載...")
        self.download_btn.config(state="disabled")
        self.progress_bar['value'] = 0
        
        # 使用執行緒下載
        threading.Thread(target=self.download_video, args=(ydl_opts,), daemon=True).start()

    def download_video(self, opts):
        url = self.url_entry.get().strip()
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            
            self.root.after(0, lambda: self.status_label.config(text="下載完畢！"))
            self.root.after(0, lambda: messagebox.showinfo("成功", "影片下載並合併完成。"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("錯誤", f"下載失敗: {str(e)}"))
            self.root.after(0, lambda: self.status_label.config(text="下載失敗。"))
        finally:
            self.root.after(0, lambda: self.download_btn.config(state="normal"))

    # 進度條鉤子函數 (yt-dlp 會自動呼叫)
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                # 去除百分比符號並轉為浮點數
                p = d.get('_percent_str', '0%').replace('%', '')
                progress = float(p)
                self.root.after(0, lambda: self.update_progress(progress))
            except ValueError:
                pass
        elif d['status'] == 'finished':
            # 下載完成，正在進行後處理 (FFmpeg 合併)
            self.root.after(0, lambda: self.status_label.config(text="下載完成，正在轉碼/合併 (FFmpeg)..."))

    def update_progress(self, progress):
        self.progress_bar['value'] = progress
        self.status_label.config(text=f"正在下載... {progress}%")

if __name__ == "__main__":
    root = tk.Tk()
    app = YtDlpGUI(root)
    root.mainloop()
