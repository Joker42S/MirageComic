import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import threading
import zipfile
from datetime import datetime
from MirageComic import create_simple_phantom_tank

class MirageComicGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("幻影漫画生成器")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # 设置窗口图标和样式
        self.setup_styles()
        
        # 初始化变量
        self.hidden_img_paths = []  # 改为列表以支持批量
        self.output_folder = tk.StringVar(value=os.getcwd())  # 输出文件夹
        self.create_zip = tk.BooleanVar(value=False)  # 是否创建压缩包
        self.preview_img = None
        self.current_preview_index = 0
        
        # 创建主界面
        self.create_widgets()
        
    def setup_styles(self):
        """设置现代化的样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 配置按钮样式
        style.configure('Title.TLabel', 
                       font=('Arial', 16, 'bold'),
                       background='#f0f0f0',
                       foreground='#333333')
        
        style.configure('Header.TLabel', 
                       font=('Arial', 12, 'bold'),
                       background='#f0f0f0',
                       foreground='#444444')
        
        style.configure('Action.TButton',
                       font=('Arial', 10, 'bold'),
                       padding=(10, 5))
        
    def create_widgets(self):
        """创建GUI组件"""
        # 主标题
        title_frame = tk.Frame(self.root, bg='#f0f0f0', pady=10)
        title_frame.pack(fill='x')
        
        title_label = ttk.Label(title_frame, text="🎭 批量幻影坦克生成器", style='Title.TLabel')
        title_label.pack()
        
        subtitle_label = ttk.Label(title_frame, text="为黑白漫画创建批量幻影图", 
                                 font=('Arial', 10, 'italic'),
                                 background='#f0f0f0', foreground='#666666')
        subtitle_label.pack()
        
        # 主容器
        main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=20, pady=10)
        main_frame.pack(fill='both', expand=True)
        
        # 左侧面板 - 控制区域
        left_frame = tk.Frame(main_frame, bg='#ffffff', relief='raised', bd=1)
        left_frame.pack(side='left', fill='y', padx=(0, 10))
        left_frame.configure(width=350)
        left_frame.pack_propagate(False)
        
        # 文件选择区域
        self.create_file_selection(left_frame)
        
        # 输出设置区域
        self.create_output_settings(left_frame)
        
        # 操作按钮
        self.create_action_buttons(left_frame)
        
        # 右侧面板 - 预览区域
        right_frame = tk.Frame(main_frame, bg='#ffffff', relief='raised', bd=1)
        right_frame.pack(side='right', fill='both', expand=True)
        
        self.create_preview_area(right_frame)
        
        # 状态栏
        self.create_status_bar()
        
    def create_file_selection(self, parent):
        """创建文件选择区域"""
        file_frame = tk.Frame(parent, bg='#ffffff', pady=15, padx=15)
        file_frame.pack(fill='x')
        
        ttk.Label(file_frame, text="📁 选择隐藏图像", style='Header.TLabel').pack(anchor='w')
        
        # 选择按钮组
        button_frame = tk.Frame(file_frame, bg='#ffffff')
        button_frame.pack(fill='x', pady=(5, 0))
        
        select_files_btn = ttk.Button(button_frame, text="选择图片文件", 
                                     command=self.select_hidden_images,
                                     style='Action.TButton')
        select_files_btn.pack(side='left')
        
        select_folder_btn = ttk.Button(button_frame, text="选择图片文件夹", 
                                      command=self.select_image_folder,
                                      style='Action.TButton')
        select_folder_btn.pack(side='left', padx=(5, 0))
        
        clear_selection_btn = ttk.Button(button_frame, text="清除选择", 
                                        command=self.clear_selection)
        clear_selection_btn.pack(side='left', padx=(5, 0))
        
        # 文件列表
        list_frame = tk.Frame(file_frame, bg='#ffffff')
        list_frame.pack(fill='both', expand=True, pady=(10, 0))
        
        # 创建滚动条和列表框
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.file_listbox = tk.Listbox(list_frame, 
                                      font=('Arial', 9),
                                      bg='#f8f8f8',
                                      selectmode=tk.SINGLE,
                                      yscrollcommand=scrollbar.set,
                                      height=8)
        self.file_listbox.pack(side='left', fill='both', expand=True)
        self.file_listbox.bind('<<ListboxSelect>>', self.on_file_select)
        
        scrollbar.config(command=self.file_listbox.yview)
        
        # 支持的格式提示
        ttk.Label(file_frame, text="支持: PNG, JPG, JPEG, BMP", 
                 font=('Arial', 8), 
                 background='#ffffff', foreground='#888888').pack(anchor='w', pady=(5, 0))
        
    def create_output_settings(self, parent):
        """创建输出设置区域"""
        settings_frame = tk.Frame(parent, bg='#ffffff', pady=15, padx=15)
        settings_frame.pack(fill='x')
        
        ttk.Label(settings_frame, text="⚙️ 输出设置", style='Header.TLabel').pack(anchor='w')
        
        # 输出文件夹选择
        folder_frame = tk.Frame(settings_frame, bg='#ffffff')
        folder_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Label(folder_frame, text="输出文件夹:", 
                 background='#ffffff', font=('Arial', 9)).pack(anchor='w')
        
        folder_path_frame = tk.Frame(folder_frame, bg='#ffffff')
        folder_path_frame.pack(fill='x', pady=(2, 0))
        
        self.folder_entry = tk.Entry(folder_path_frame, textvariable=self.output_folder,
                                    font=('Arial', 9), state='readonly',
                                    bg='#f8f8f8', relief='flat', bd=5)
        self.folder_entry.pack(side='left', fill='x', expand=True)
        
        folder_btn = ttk.Button(folder_path_frame, text="浏览", 
                               command=self.select_output_folder)
        folder_btn.pack(side='right', padx=(5, 0))
        
        # 压缩包选项
        zip_frame = tk.Frame(settings_frame, bg='#ffffff')
        zip_frame.pack(fill='x', pady=(15, 0))
        
        self.zip_checkbox = ttk.Checkbutton(zip_frame, text="打包为压缩文件 (.zip)",
                                           variable=self.create_zip,
                                           onvalue=True, offvalue=False)
        self.zip_checkbox.pack(anchor='w')
        
    def create_action_buttons(self, parent):
        """创建操作按钮"""
        button_frame = tk.Frame(parent, bg='#ffffff', pady=15, padx=15)
        button_frame.pack(fill='x', side='bottom')
        
        # 生成按钮
        self.generate_btn = ttk.Button(button_frame, text="🎨 批量生成幻影坦克",
                                      command=self.generate_phantoms,
                                      style='Action.TButton')
        self.generate_btn.pack(fill='x', pady=(0, 10))
        
        # 清除按钮
        clear_btn = ttk.Button(button_frame, text="🗑️ 清除全部",
                              command=self.clear_all)
        clear_btn.pack(fill='x')
        
    def create_preview_area(self, parent):
        """创建预览区域"""
        preview_frame = tk.Frame(parent, bg='#ffffff', pady=15, padx=15)
        preview_frame.pack(fill='both', expand=True)
        
        # 预览标题和导航
        header_frame = tk.Frame(preview_frame, bg='#ffffff')
        header_frame.pack(fill='x')
        
        ttk.Label(header_frame, text="🖼️ 图像预览", style='Header.TLabel').pack(side='left')
        
        # 预览导航按钮
        nav_frame = tk.Frame(header_frame, bg='#ffffff')
        nav_frame.pack(side='right')
        
        self.prev_btn = ttk.Button(nav_frame, text="◀", command=self.prev_image, width=3)
        self.prev_btn.pack(side='left')
        
        self.image_info_label = tk.Label(nav_frame, text="0/0", 
                                        font=('Arial', 9), bg='#ffffff')
        self.image_info_label.pack(side='left', padx=5)
        
        self.next_btn = ttk.Button(nav_frame, text="▶", command=self.next_image, width=3)
        self.next_btn.pack(side='left')
        
        # 预览画布
        canvas_frame = tk.Frame(preview_frame, bg='#f8f8f8', relief='sunken', bd=2)
        canvas_frame.pack(fill='both', expand=True, pady=(10, 0))
        
        self.preview_canvas = tk.Canvas(canvas_frame, bg='#ffffff', highlightthickness=0)
        self.preview_canvas.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 默认提示
        self.show_default_preview()
        
    def show_default_preview(self):
        """显示默认预览提示"""
        self.preview_canvas.delete("all")
        self.preview_canvas.create_text(
            250, 200, text="请选择隐藏图像\n预览将显示在这里",
            font=('Arial', 12), fill='#cccccc', justify='center'
        )
        self.image_info_label.config(text="0/0")
        
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = tk.Frame(self.root, bg='#e0e0e0', height=25)
        self.status_bar.pack(fill='x', side='bottom')
        self.status_bar.pack_propagate(False)
        
        self.status_label = tk.Label(self.status_bar, text="就绪",
                                    bg='#e0e0e0', fg='#333333',
                                    font=('Arial', 9), anchor='w')
        self.status_label.pack(side='left', padx=10, pady=2)
        
        # 进度条
        self.progress = ttk.Progressbar(self.status_bar, mode='determinate')
        self.progress.pack(side='right', padx=10, pady=2)
        
    def select_hidden_images(self):
        """批量选择隐藏图像"""
        file_types = [
            ("图像文件", "*.png *.jpg *.jpeg *.bmp *.gif"),
            ("PNG文件", "*.png"),
            ("JPEG文件", "*.jpg *.jpeg"),
            ("所有文件", "*.*")
        ]
        
        filenames = filedialog.askopenfilenames(
            title="批量选择隐藏图像",
            filetypes=file_types
        )
        
        if filenames:
            self.hidden_img_paths = list(filenames)
            self.update_file_list()
            self.current_preview_index = 0
            self.update_preview()
            self.update_status(f"已选择 {len(filenames)} 个文件")
            
    def select_image_folder(self):
        """选择包含图片的文件夹"""
        folder = filedialog.askdirectory(
            title="选择包含图片的文件夹"
        )
        
        if folder:
            try:
                # 获取文件夹中的所有图片文件
                image_files = []
                for f in os.listdir(folder):
                    if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                        image_files.append(os.path.join(folder, f))
                
                if image_files:
                    self.hidden_img_paths = image_files
                    self.update_file_list()
                    self.current_preview_index = 0
                    self.update_preview()
                    self.update_status(f"从文件夹中加载 {len(image_files)} 个图片文件")
                else:
                    messagebox.showwarning("警告", "所选文件夹中没有找到支持的图片文件！\n支持格式：PNG, JPG, JPEG, BMP, GIF")
                    
            except Exception as e:
                messagebox.showerror("错误", f"读取文件夹时出错: {str(e)}")
            
    def clear_selection(self):
        """清除文件选择"""
        self.hidden_img_paths = []
        self.update_file_list()
        self.show_default_preview()
        self.current_preview_index = 0
        self.update_status("文件选择已清除")
        
    def update_file_list(self):
        """更新文件列表显示"""
        self.file_listbox.delete(0, tk.END)
        for i, filepath in enumerate(self.hidden_img_paths):
            filename = os.path.basename(filepath)
            self.file_listbox.insert(tk.END, f"{i+1}. {filename}")
            
    def on_file_select(self, event):
        """文件列表选择事件"""
        selection = self.file_listbox.curselection()
        if selection:
            self.current_preview_index = selection[0]
            self.update_preview()
            
    def prev_image(self):
        """上一张图片"""
        if self.hidden_img_paths and self.current_preview_index > 0:
            self.current_preview_index -= 1
            self.update_preview()
            self.file_listbox.selection_clear(0, tk.END)
            self.file_listbox.selection_set(self.current_preview_index)
            
    def next_image(self):
        """下一张图片"""
        if self.hidden_img_paths and self.current_preview_index < len(self.hidden_img_paths) - 1:
            self.current_preview_index += 1
            self.update_preview()
            self.file_listbox.selection_clear(0, tk.END)
            self.file_listbox.selection_set(self.current_preview_index)
            
    def update_preview(self):
        """更新预览图像"""
        if not self.hidden_img_paths:
            self.show_default_preview()
            return
            
        if 0 <= self.current_preview_index < len(self.hidden_img_paths):
            filepath = self.hidden_img_paths[self.current_preview_index]
            self.load_preview_image(filepath)
            self.image_info_label.config(text=f"{self.current_preview_index + 1}/{len(self.hidden_img_paths)}")
            
    def select_output_folder(self):
        """选择输出文件夹"""
        folder = filedialog.askdirectory(
            title="选择输出文件夹",
            initialdir=self.output_folder.get()
        )
        
        if folder:
            self.output_folder.set(folder)
            self.update_status(f"输出文件夹: {folder}")
            
    def load_preview_image(self, filepath):
        """加载预览图像"""
        try:
            # 加载并调整图像大小以适应预览
            img = Image.open(filepath)
            img = img.convert('RGB')
            
            # 计算预览尺寸
            canvas_width = 500
            canvas_height = 400
            
            # 保持宽高比
            img_ratio = img.width / img.height
            canvas_ratio = canvas_width / canvas_height
            
            if img_ratio > canvas_ratio:
                new_width = canvas_width
                new_height = int(canvas_width / img_ratio)
            else:
                new_height = canvas_height
                new_width = int(canvas_height * img_ratio)
            
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 转换为tkinter可用的格式
            self.preview_img = ImageTk.PhotoImage(img)
            
            # 清除画布并显示图像
            self.preview_canvas.delete("all")
            x = (canvas_width - new_width) // 2
            y = (canvas_height - new_height) // 2
            self.preview_canvas.create_image(x, y, anchor='nw', image=self.preview_img)
            
            # 显示文件名
            filename = os.path.basename(filepath)
            self.preview_canvas.create_text(
                canvas_width // 2, canvas_height - 20, 
                text=filename, font=('Arial', 10), fill='#666666'
            )
            
        except Exception as e:
            messagebox.showerror("错误", f"无法加载图像: {str(e)}")
            
    def generate_phantoms(self):
        """批量生成幻影坦克"""
        if not self.hidden_img_paths:
            messagebox.showwarning("警告", "请先选择隐藏图像！")
            return
            
        if not self.output_folder.get():
            messagebox.showwarning("警告", "请选择输出文件夹！")
            return
            
        # 在新线程中生成，避免界面冻结
        self.generate_btn.configure(state='disabled', text="正在批量生成...")
        self.progress.configure(mode='determinate', maximum=len(self.hidden_img_paths), value=0)
        self.update_status("开始批量生成幻影坦克...")
        
        def generate_task():
            try:
                output_files = []
                
                for i, img_path in enumerate(self.hidden_img_paths):
                    # 更新进度
                    filename = os.path.basename(img_path)
                    self.root.after(0, lambda: self.update_status(f"正在处理: {filename}"))
                    
                    # 生成幻影坦克
                    result = create_simple_phantom_tank(img_path)
                    
                    # 生成输出文件名
                    base_name = os.path.splitext(filename)[0]
                    output_file = os.path.join(self.output_folder.get(), f"{base_name}_phantom.png")
                    
                    # 确保文件名唯一
                    counter = 1
                    while os.path.exists(output_file):
                        output_file = os.path.join(
                            self.output_folder.get(), 
                            f"{base_name}_phantom_{counter}.png"
                        )
                        counter += 1
                    
                    # 保存文件
                    result.save(output_file, format="PNG")
                    output_files.append(output_file)
                    
                    # 更新进度条
                    self.root.after(0, lambda i=i: self.progress.configure(value=i + 1))
                
                # 是否创建压缩包
                zip_file = None
                if self.create_zip.get():
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    zip_file = os.path.join(self.output_folder.get(), f"phantom_tanks_{timestamp}.zip")
                    
                    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zf:
                        for file_path in output_files:
                            zf.write(file_path, os.path.basename(file_path))
                
                # 更新UI
                self.root.after(0, lambda: self.generation_complete(output_files, zip_file))
                
            except Exception as e:
                self.root.after(0, lambda: self.generation_error(str(e)))
        
        threading.Thread(target=generate_task, daemon=True).start()
        
    def generation_complete(self, output_files, zip_file):
        """生成完成"""
        self.progress.configure(value=0)
        self.generate_btn.configure(state='normal', text="🎨 批量生成幻影坦克")
        
        if zip_file:
            message = f"批量生成完成！\n共生成 {len(output_files)} 个文件\n已打包为: {os.path.basename(zip_file)}"
            self.update_status(f"生成完成并打包: {os.path.basename(zip_file)}")
        else:
            message = f"批量生成完成！\n共生成 {len(output_files)} 个文件\n保存位置: {self.output_folder.get()}"
            self.update_status(f"批量生成完成: {len(output_files)} 个文件")
        
        result = messagebox.askyesno("成功", f"{message}\n\n是否打开输出文件夹？")
        if result:
            # 打开输出文件夹
            os.startfile(self.output_folder.get())
            
    def generation_error(self, error_msg):
        """生成错误"""
        self.progress.configure(value=0)
        self.generate_btn.configure(state='normal', text="🎨 批量生成幻影坦克")
        self.update_status("批量生成失败")
        messagebox.showerror("错误", f"批量生成失败: {error_msg}")
        
    def clear_all(self):
        """清除所有内容"""
        self.hidden_img_paths = []
        self.current_preview_index = 0
        self.update_file_list()
        self.show_default_preview()
        self.create_zip.set(False)
        self.update_status("已清除所有内容")
        
    def update_status(self, message):
        """更新状态栏"""
        self.status_label.config(text=message)

def main():
    root = tk.Tk()
    app = MirageComicGUI(root)
    
    # 设置窗口居中
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main() 