import os
import shutil
import re

# 경로 설정
target_dir = r"c:\Users\user\OneDrive\Desktop\파이썬\6주차. 컴퓨터관리 및 문서활용\1. 폴더 분석 및 정리"

# 담당 부처 목록 (파일 이름에서 검색할 키워드)
departments = [
    "기계공학과", "총무팀", "입학처", "교무처", "산학협력단", 
    "시설팀", "도서관", "취업지원센터", "학생지원팀", "컴퓨터공학과"
]

def organize():
    # 파일 목록 가져오기 (스크립트 파일은 제외)
    files = [f for f in os.listdir(target_dir) if os.path.isfile(os.path.join(target_dir, f)) and f not in ['organize_files.py', 'revert_files.py']]
    
    for filename in files:
        file_path = os.path.join(target_dir, filename)
        
        # 1. 부처 확인
        assigned_dept = None
        for dept in departments:
            if dept in filename:
                assigned_dept = dept
                break
        
        if assigned_dept:
            dest_folder = os.path.join(target_dir, assigned_dept)
        else:
            # 2. 날짜 확인 (YYYYMMDD 형식 또는 유사 형식 추출 시도)
            # 파일 이름에서 8자리 숫자 또는 연도/월 패턴 찾기
            date_match = re.search(r"(\d{4})(\d{2})\d{2}", filename)
            if not date_match:
                # 2025학년도 같은 패턴
                date_match = re.search(r"(\d{4})학년도", filename)
            
            if date_match:
                year = date_match.group(1)
                # 월 정보가 있으면 사용, 없으면 04(기본값) 또는 빈값 처리
                month = date_match.group(2) if len(date_match.groups()) > 1 else "04"
                dest_folder = os.path.join(target_dir, f"{year}_{month}")
            else:
                # 3. 애매한 파일 (기본값 2026_04)
                dest_folder = os.path.join(target_dir, "2026_04")
        
        # 폴더 생성 및 이동
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)
        
        shutil.move(file_path, os.path.join(dest_folder, filename))
        print(f"Moved: {filename} -> {os.path.basename(dest_folder)}")

if __name__ == "__main__":
    organize()
    print("Organization complete.")
