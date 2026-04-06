import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yt_dlp
import threading

class YtDlpGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Python 進階影音下載器 (yt-dlp) - 支援純音訊")
        self.root.geometry("650x620")
        
        # 狀態變數
        self.video_formats = []
        self.audio_formats = []
        self.info_dict = None
        self.is_analyzed = False # 記錄是否已經分析過網址

        # --- 第一區：URL 輸入與分析 ---
        url_frame = ttk.LabelFrame(root, text=" 1. 輸入影片網址 ", padding=10)
        url_frame.pack(fill="x", padx=15, pady=5)

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

        # --- 第三區：下載模式與格式選擇 ---
        options_frame = ttk.LabelFrame(root, text=" 2. 選擇下載模式與格式 ", padding=10)
        options_frame.pack(fill="x", padx=15, pady=10)

        # 模式選擇 (Radiobuttons)
        self.download_mode = tk.StringVar(value="video") # 預設為影音模式
        mode_frame = ttk.Frame(options_frame)
        mode_frame.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        ttk.Radiobutton(mode_frame, text="下載影音 (Video + Audio)", variable=self.download_mode, 
                        value="video", command=self.on_mode_change).pack(side="left", padx=(0, 20))
        ttk.Radiobutton(mode_frame, text="僅下載純音訊 (Audio Only)", variable=self.download_mode, 
                        value="audio", command=self.on_mode_change).pack(side="left")

        # 影片畫質選單
        ttk.Label(options_frame, text="影片畫質:").grid(row=1, column=0, sticky="w", pady=5)
        self.video_combo = ttk.Combobox(options_frame, state="disabled", width=50)
        self.video_combo.grid(row=1, column=1, sticky="we", padx=(10, 0))
        self.video_combo.set("請先點擊'分析連結'")

        # 音頻音質選單
        ttk.Label(options_frame, text="音頻音質:").grid(row=2, column=0, sticky="w", pady=5)
        self.audio_combo = ttk.Combobox(options_frame, state="disabled", width=50)
        self.audio_combo.grid(row=2, column=1, sticky="we", padx=(10, 0))
        self.audio_combo.set("請先點擊'分析連結'")
        
        # 輸出格式 (Container / Codec)
        self.format_label = ttk.Label(options_frame, text="封裝格式:")
        self.format_label.grid(row=3, column=0, sticky="w", pady=5)
        self.format_combo = ttk.Combobox(options_frame, state="readonly", width=15)
        self.format_combo.grid(row=3, column=1, sticky="w", padx=(10, 0))
        
        options_frame.columnconfigure(1, weight=1)
        
        # 初始化選單狀態
        self.on_mode_change()

        # --- 第四區：儲存路徑 ---
        path_frame = ttk.Frame(root, padding=(15, 0))
        path_frame.pack(fill="x")
        ttk.Label(path_frame, text="儲存至:").pack(side="left", padx=(0, 10))
        self.path_entry = ttk.Entry(path_frame)
        self.path_entry.pack(side="left", expand=True, fill="x", padx=(0, 10))
        self.path_entry.insert(0, "./downloads")
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
    #      UI 動態切換邏輯
    # ==========================
    def on_mode_change(self):
        mode = self.download_mode.get()
        if mode == "video":
            self.format_label.config(text="封裝格式:")
            self.format_combo.config(values=["mp4", "mkv"])
            self.format_combo.current(0)
            # 如果已經分析過，則恢復影片選單；否則保持禁用
            if self.is_analyzed:
                self.video_combo.config(state="readonly")
        elif mode == "audio":
            self.format_label.config(text="音檔格式:")
            self.format_combo.config(values=["mp3", "flac", "opus", "aac", "wav"])
            self.format_combo.current(0) # 預設選 mp3
            # 純音訊模式不需要選擇影片畫質
            self.video_combo.config(state="disabled")

    def browse_path(self):
        path = filedialog.askdirectory()
        if path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)

    # ==========================
    #      分析與下載邏輯
    # ==========================
    def start_analyze_thread(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("警告", "請輸入 YouTube 連結！")
            return
        
        self.status_label.config(text="正在分析中，請稍候...")
        self.analyze_btn.config(state="disabled")
        self.download_btn.config(state="disabled")
        threading.Thread(target=self.analyze_url, args=(url,), daemon=True).start()

    def analyze_url(self, url):
        ydl_opts = {'skip_download': True, 'quiet': True}
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.info_dict = ydl.extract_info(url, download=False)
            
            title = self.info_dict.get('title', 'Unknown')
            self.root.after(0, lambda: self.title_label.config(text=f"影片標題: {title}"))
            
            formats = self.info_dict.get('formats', [])
            self.video_formats = [{'id': 'bv', 'desc': 'Best Video'}]
            self.audio_formats = [{'id': 'ba', 'desc': 'Best Audio'}]
            
            v_options = ["最高畫質 (自動選擇)"]
            a_options = ["最高音質 (自動選擇)"]

            for f in formats:
                f_id = f.get('format_id')
                ext = f.get('ext')
                note = f.get('format_note', '')
                
                if f.get('vcodec') != 'none' and f.get('acodec') == 'none':
                    res = f.get('resolution', f'{f.get("width")}x{f.get("height")}')
                    fps = f.get('fps', '')
                    fps_str = f'{fps}fps' if fps else ''
                    v_options.append(f"{res} ({ext}) - {note} {fps_str}".strip())
                    self.video_formats.append({'id': f_id, 'desc': f"{res} ({ext})"})
                    
                elif f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                    abr = f.get('abr', 0)
                    a_options.append(f"{ext} - {note} ({abr}kbps)".strip())
                    self.audio_formats.append({'id': f_id, 'desc': f"{ext} ({abr}kbps)"})

            self.root.after(0, lambda: self.update_combos(v_options, a_options))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("錯誤", f"分析連結失敗: {str(e)}"))
            self.root.after(0, lambda: self.status_label.config(text="分析失敗。"))
            self.root.after(0, lambda: self.analyze_btn.config(state="normal"))

    def update_combos(self, v_opts, a_opts):
        self.is_analyzed = True
        
        self.video_combo.config(values=v_opts)
        self.video_combo.current(0)
        
        self.audio_combo.config(values=a_opts, state="readonly")
        self.audio_combo.current(0)
        
        # 根據當前模式刷新 UI 狀態 (決定影片選單是否要 disabled)
        self.on_mode_change()
        
        self.analyze_btn.config(state="normal")
        self.download_btn.config(state="normal")
        self.status_label.config(text="分析完成，請選擇格式並開始下載。")

    def start_download_thread(self):
        mode = self.download_mode.get()
        target_format = self.format_combo.get()
        out_path = self.path_entry.get().strip()
        
        a_idx = self.audio_combo.current()
        a_id = self.audio_formats[a_idx]['id']
        
        ydl_opts = {
            'outtmpl': f'{out_path}/%(title)s.%(ext)s',
            'progress_hooks': [self.progress_hook],
        }

        # 根據模式設定 yt-dlp 參數
        if mode == "video":
            v_idx = self.video_combo.current()
            v_id = self.video_formats[v_idx]['id']
            ydl_opts['format'] = f"{v_id}+{a_id}"
            ydl_opts['merge_output_format'] = target_format # mp4 或 mkv
        
        elif mode == "audio":
            ydl_opts['format'] = a_id # 只下載音頻流
            # 使用後處理器將音檔轉為指定格式
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudioPP',
                'preferredcodec': target_format, # mp3, flac, opus, aac, wav
                'preferredquality': '192',       # 預設轉碼品質
            }]
        
        self.status_label.config(text=f"開始下載 ({mode} 模式)...")
        self.download_btn.config(state="disabled")
        self.progress_bar['value'] = 0
        
        threading.Thread(target=self.download_video, args=(ydl_opts,), daemon=True).start()

    def download_video(self, opts):
        url = self.url_entry.get().strip()
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            
            self.root.after(0, lambda: self.status_label.config(text="處理完畢！"))
            self.root.after(0, lambda: messagebox.showinfo("成功", "檔案下載與處理完成。"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("錯誤", f"處理失敗: {str(e)}"))
            self.root.after(0, lambda: self.status_label.config(text="處理失敗。"))
        finally:
            self.root.after(0, lambda: self.download_btn.config(state="normal"))

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                p = d.get('_percent_str', '0%').replace('%', '')
                progress = float(p)
                self.root.after(0, lambda: self.update_progress(progress))
            except ValueError:
                pass
        elif d['status'] == 'finished':
            self.root.after(0, lambda: self.status_label.config(text="下載完成，正在由 FFmpeg 進行轉碼/合併..."))

    def update_progress(self, progress):
        self.progress_bar['value'] = progress
        self.status_label.config(text=f"正在下載... {progress}%")

if __name__ == "__main__":
    root = tk.Tk()
    app = YtDlpGUI(root)
    root.mainloop()
