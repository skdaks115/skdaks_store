import os
import customtkinter as ctk
import tkinter.messagebox as messagebox
from tkinter import filedialog
import hashlib

# Configuration for colors
DARK_GRAY = "#1e1e1e"
DARK_bg = "#121212"
BABY_PINK = "#F4C2C2"
LIGHT_PINK = "#FFE4E1"
HOVER_PINK = "#E5ABAB"
WHITE_TEXT = "#FFFFFF"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class FileRow(ctk.CTkFrame):
    def __init__(self, master, filename, filepath, is_duplicate=False, **kwargs):
        # 중복 파일일 경우 연한 핑크색 배경 적용, 아니면 투명
        bg_color = "#3a2b2b" if is_duplicate else "transparent"
        super().__init__(master, fg_color=bg_color, **kwargs)
        self.filename = filename
        self.filepath = filepath
        self.is_selected = ctk.BooleanVar(value=False)
        self.new_filename = filename
        self.is_duplicate = is_duplicate
        
        self.checkbox = ctk.CTkCheckBox(self, text="", variable=self.is_selected, width=20, 
                                        fg_color=BABY_PINK, hover_color=HOVER_PINK, border_color=BABY_PINK)
        self.checkbox.pack(side="left", padx=10, pady=5)
        
        # 중복 파일이면 텍스트를 약간 베이비핑크색으로 눈에 띄게
        text_color = BABY_PINK if is_duplicate else WHITE_TEXT
        
        self.label_old = ctk.CTkLabel(self, text=filename, width=300, anchor="w", text_color=text_color)
        self.label_old.pack(side="left", padx=5)
        
        self.label_arrow = ctk.CTkLabel(self, text="➜", width=30, text_color=BABY_PINK)
        self.label_arrow.pack(side="left", padx=10)
        
        self.label_new = ctk.CTkLabel(self, text=filename, width=300, anchor="w", text_color=BABY_PINK)
        self.label_new.pack(side="left", padx=5)
        
    def update_preview(self, new_ext):
        if new_ext and not new_ext.startswith("."):
            new_ext = "." + new_ext
            
        base, ext = os.path.splitext(self.filename)
        if new_ext:
            self.new_filename = base + new_ext
        else:
            self.new_filename = self.filename
            
        self.label_new.configure(text=self.new_filename)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("File Converter Pro (with. Claude)")
        self.geometry("900x700")
        self.configure(fg_color=DARK_bg)
        
        self.current_folder = ""
        self.file_rows = []
        
        self.setup_ui()
        
    def setup_ui(self):
        # 상단 폴더 선택 영역
        self.header_frame = ctk.CTkFrame(self, fg_color=DARK_GRAY, corner_radius=10)
        self.header_frame.pack(fill="x", padx=15, pady=15)
        
        self.btn_select_folder = ctk.CTkButton(self.header_frame, text="📁 폴더 선택", 
                                               fg_color=BABY_PINK, text_color=DARK_bg, 
                                               hover_color=HOVER_PINK, font=("Arial", 14, "bold"),
                                               command=self.select_folder)
        self.btn_select_folder.pack(side="left", padx=15, pady=15)
        
        self.lbl_folder_path = ctk.CTkLabel(self.header_frame, text="현재 선택된 폴더가 없습니다.", text_color=BABY_PINK, font=("Arial", 13))
        self.lbl_folder_path.pack(side="left", padx=10, fill="x", expand=True)
        
        # 툴바 영역 (기능들)
        self.tools_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.tools_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(self.tools_frame, text="변경할 확장자명:", text_color=BABY_PINK, font=("Arial", 13, "bold")).pack(side="left", padx=5)
        self.entry_ext = ctk.CTkEntry(self.tools_frame, width=120, border_color=BABY_PINK, text_color=WHITE_TEXT, placeholder_text="예: pdf, txt")
        self.entry_ext.pack(side="left", padx=5)
        self.entry_ext.bind("<KeyRelease>", self.update_previews)
        
        self.btn_apply = ctk.CTkButton(self.tools_frame, text="🔄 일괄 변경", 
                                       fg_color=BABY_PINK, text_color=DARK_bg, 
                                       hover_color=HOVER_PINK, font=("Arial", 13, "bold"),
                                       command=self.apply_rename)
        self.btn_apply.pack(side="left", padx=10)
        
        self.btn_delete = ctk.CTkButton(self.tools_frame, text="🗑️ 선택 삭제", 
                                        fg_color="transparent", border_width=1, border_color=BABY_PINK, text_color=BABY_PINK, 
                                        hover_color="#5a2a2a", font=("Arial", 13, "bold"),
                                        command=self.delete_selected)
        self.btn_delete.pack(side="left", padx=10)
        
        self.btn_scan = ctk.CTkButton(self.tools_frame, text="🔍 중복 파일 스캔", 
                                      fg_color="transparent", border_width=1, border_color=BABY_PINK, text_color=BABY_PINK, 
                                      hover_color="#3a2a2a", font=("Arial", 13, "bold"), command=self.scan_duplicates)
        self.btn_scan.pack(side="left", padx=10)
        
        # 리스트 타이틀
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=(15,0))
        ctk.CTkLabel(title_frame, text="✓", width=20, text_color=BABY_PINK, font=("Arial", 12, "bold")).pack(side="left", padx=10)
        ctk.CTkLabel(title_frame, text="현재 파일명", width=300, anchor="w", text_color=BABY_PINK, font=("Arial", 12, "bold")).pack(side="left", padx=5)
        ctk.CTkLabel(title_frame, text="변경 후 파일명", width=300, anchor="w", text_color=BABY_PINK, font=("Arial", 12, "bold")).pack(side="left", padx=45)

        # 리스트 영역
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color=DARK_GRAY, border_color=BABY_PINK, border_width=1, corner_radius=10)
        self.scroll_frame.pack(fill="both", expand=True, padx=15, pady=5)
        
        # 전체 선택 기능
        self.select_all_var = ctk.BooleanVar(value=False)
        self.chk_select_all = ctk.CTkCheckBox(self, text="전체 선택 / 해제", variable=self.select_all_var, command=self.toggle_select_all,
                                              fg_color=BABY_PINK, hover_color=HOVER_PINK, border_color=BABY_PINK, text_color=WHITE_TEXT)
        self.chk_select_all.pack(anchor="w", padx=20, pady=5)

        # 시스템 로그 라벨
        ctk.CTkLabel(self, text="📝 시스템 로그", text_color=BABY_PINK, font=("Arial", 13, "bold")).pack(anchor="w", padx=15)
        
        # 로그 영역
        self.log_textbox = ctk.CTkTextbox(self, height=120, fg_color=DARK_GRAY, text_color=WHITE_TEXT, border_color=BABY_PINK, border_width=1, corner_radius=10)
        self.log_textbox.pack(fill="x", padx=15, pady=(0, 15))
        self.log_textbox.configure(state="disabled")
        
        self.log("✅ 프로그램이 초기화되었습니다. 폴더를 선택하여 작업을 시작하세요.")
        
    def log(self, message):
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", "> " + message + "\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")

    def select_folder(self):
        folder = filedialog.askdirectory(title="작업할 폴더를 선택하세요")
        if folder:
            self.current_folder = folder
            self.lbl_folder_path.configure(text=folder)
            self.log(f"📁 폴더 변경: {folder}")
            self.refresh_list()

    def toggle_select_all(self):
        state = self.select_all_var.get()
        for row in self.file_rows:
            row.is_selected.set(state)

    def refresh_list(self, duplicates_set=None):
        if duplicates_set is None:
            duplicates_set = set()
            
        for row in self.file_rows:
            row.destroy()
        self.file_rows.clear()
        self.select_all_var.set(False)
        
        if not self.current_folder:
            return
            
        try:
            files = [f for f in os.listdir(self.current_folder) if os.path.isfile(os.path.join(self.current_folder, f))]
            for f in files:
                filepath = os.path.join(self.current_folder, f)
                is_dup = filepath in duplicates_set
                row = FileRow(self.scroll_frame, f, filepath, is_duplicate=is_dup)
                row.pack(fill="x", pady=2)
                self.file_rows.append(row)
            self.update_previews(None)
            self.log(f"📄 총 {len(files)}개의 파일을 불러왔습니다. (중복 {len(duplicates_set)}개)")
        except Exception as e:
            self.log(f"❌ 오류: 폴더를 읽는 중 문제가 발생했습니다. ({str(e)})")
            messagebox.showerror("오류", f"폴더 내용을 읽을 수 없습니다.\n자세한 내용: {e}")

    def update_previews(self, event):
        new_ext = self.entry_ext.get().strip()
        for row in self.file_rows:
            row.update_preview(new_ext)

    def apply_rename(self):
        selected_rows = [row for row in self.file_rows if row.is_selected.get()]
        if not selected_rows:
            messagebox.showwarning("경고", "변경할 파일을 먼저 선택해주세요.")
            return
            
        new_ext = self.entry_ext.get().strip()
        if not new_ext:
            messagebox.showwarning("경고", "변경할 목표 확장자(예: pdf)를 입력해주세요.")
            return
            
        success_count = 0
        error_count = 0
        total = len(selected_rows)
        
        for row in selected_rows:
            try:
                new_filepath = os.path.join(self.current_folder, row.new_filename)
                if row.filepath != new_filepath:
                    if os.path.exists(new_filepath):
                        self.log(f"⚠️ 이미 존재함: {row.new_filename} (변경을 건너뜁니다)")
                        error_count += 1
                        continue
                    os.rename(row.filepath, new_filepath)
                    self.log(f"🔄 변경 성공: {row.filename} -> {row.new_filename}")
                    row.filepath = new_filepath
                    row.filename = row.new_filename
                    success_count += 1
                else:
                    self.log(f"ℹ️ 변경 불필요: {row.filename}")
            except Exception as e:
                error_count += 1
                self.log(f"❌ 변경 실패: {row.filename} -> {e}")
                
        self.log(f"✅ 일괄 변경 완료 (성공: {success_count}, 실패/스킵: {error_count})")
        messagebox.showinfo("완료", f"총 {total}개 중 {success_count}개의 파일이 변경되었습니다.")
        self.refresh_list()

    def delete_selected(self):
        selected_rows = [row for row in self.file_rows if row.is_selected.get()]
        if not selected_rows:
            messagebox.showwarning("경고", "삭제할 파일을 선택해주세요.")
            return
            
        if not messagebox.askyesno("삭제 확인", f"선택한 {len(selected_rows)}개의 파일을 영구 삭제하시겠습니까?\n이 작업은 되돌릴 수 없습니다!"):
            return
            
        success_count = 0
        for row in selected_rows:
            try:
                os.remove(row.filepath)
                success_count += 1
                self.log(f"🗑️ 영구 삭제됨: {row.filename}")
            except Exception as e:
                self.log(f"❌ 삭제 실패 ({row.filename}): {e}")
                
        self.log(f"✅ 파일 삭제 완료: {len(selected_rows)}개 중 {success_count}개 성공.")
        messagebox.showinfo("삭제 완료", f"{success_count}개의 파일이 영구 삭제되었습니다.")
        self.refresh_list()

    def scan_duplicates(self):
        if not self.current_folder:
            messagebox.showwarning("경고", "먼저 폴더를 선택해야 합니다.")
            return
            
        self.log("🔍 중복 파일(동일한 크기와 내용)을 스캔 중입니다. 잠시만 기다려주세요...")
        self.update()
        
        # 해시를 통한 진짜 중복 파일 찾기 알고리즘
        size_dict = {}
        for row in self.file_rows:
            try:
                size = os.path.getsize(row.filepath)
                if size not in size_dict:
                    size_dict[size] = []
                size_dict[size].append(row.filepath)
            except Exception as e:
                self.log(f"❌ 파일 크기 확인 오류 ({row.filename}): {e}")
                
        duplicates = set()
        for size, paths in size_dict.items():
            if len(paths) > 1:
                hash_dict = {}
                for p in paths:
                    try:
                        # 대용량 파일의 경우 앞부분만 읽어 빠르게 해시값 생성 (성능 최적화)
                        with open(p, 'rb') as f:
                            file_hash = hashlib.md5(f.read(8192)).hexdigest()
                        if file_hash not in hash_dict:
                            hash_dict[file_hash] = []
                        hash_dict[file_hash].append(p)
                    except Exception as e:
                        pass
                        
                for h, p_list in hash_dict.items():
                    if len(p_list) > 1:
                        # 중복으로 판명된 모든 파일을 리스트에 추가
                        for p in p_list:
                            duplicates.add(p)
                            
        self.log(f"✅ 스캔 완료: {len(duplicates)}개의 중복 의심 파일을 찾았습니다. 표를 확인하세요.")
        if duplicates:
            messagebox.showinfo("스캔 결과", f"내용이 동일한 {len(duplicates)}개의 중복 파일을 발견했습니다.\n리스트에서 핑크색 글씨와 배경으로 강조됩니다.")
        else:
            messagebox.showinfo("스캔 결과", "폴더 내에 중복된 파일이 없습니다.")
            
        self.refresh_list(duplicates_set=duplicates)


if __name__ == "__main__":
    app = App()
    app.mainloop()
