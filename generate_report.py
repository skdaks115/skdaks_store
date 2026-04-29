import psutil
import datetime
import os
from fpdf import FPDF

class Report(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 20)
        self.cell(0, 10, 'System Health & Task Manager Report', ln=True, align='C')
        self.set_font('helvetica', 'I', 10)
        self.cell(0, 10, f'Generated on: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', ln=True, align='C')
        self.ln(10)

    def chapter_title(self, title):
        self.set_font('helvetica', 'B', 14)
        self.set_fill_color(230, 230, 230)
        self.cell(0, 10, title, ln=True, align='L', fill=True)
        self.ln(5)

    def section_title(self, title):
        self.set_font('helvetica', 'B', 12)
        self.cell(0, 8, title, ln=True, align='L')
        self.ln(2)

def generate_report():
    pdf = Report()
    pdf.add_page()
    
    # --- Performance Summary ---
    pdf.chapter_title('1. Performance Summary')
    
    cpu_usage = psutil.cpu_percent(interval=1)
    cpu_freq = psutil.cpu_freq()
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    pdf.set_font('helvetica', '', 11)
    
    # CPU info
    cpu_status = "NORMAL"
    if cpu_usage > 80:
        cpu_status = "CRITICAL / HIGH USAGE"
        pdf.set_text_color(255, 0, 0)
    elif cpu_usage > 50:
        cpu_status = "MODERATE"
        pdf.set_text_color(255, 140, 0)
    
    pdf.cell(0, 8, f"CPU Usage: {cpu_usage}% ({cpu_status})", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, f"CPU Frequency: {cpu_freq.current:.2f} MHz", ln=True)
    pdf.cell(0, 8, f"CPU Cores: {psutil.cpu_count(logical=False)} Physical, {psutil.cpu_count(logical=True)} Logical", ln=True)
    pdf.ln(5)
    
    # Memory info
    mem_status = "NORMAL"
    if mem.percent > 90:
        mem_status = "CRITICAL"
        pdf.set_text_color(255, 0, 0)
    elif mem.percent > 75:
        mem_status = "HIGH"
        pdf.set_text_color(255, 140, 0)
        
    pdf.cell(0, 8, f"Memory Usage: {mem.percent}% ({mem_status})", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, f"Used: {mem.used / (1024**3):.2f} GB / Total: {mem.total / (1024**3):.2f} GB", ln=True)
    pdf.ln(5)
    
    # Disk info
    pdf.cell(0, 8, f"Disk Usage (C:): {disk.percent}%", ln=True)
    pdf.cell(0, 8, f"Free Space: {disk.free / (1024**3):.2f} GB / Total: {disk.total / (1024**3):.2f} GB", ln=True)
    pdf.ln(10)
    
    # --- Top Processes ---
    pdf.chapter_title('2. Top Processes Analysis')
    
    # CPU intensive
    pdf.section_title('Top 10 Processes by CPU Usage (%)')
    processes = []
    for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_info', 'pid']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
            
    # Sort by CPU
    top_cpu = sorted(processes, key=lambda x: x['cpu_percent'] or 0, reverse=True)[:10]
    
    # Table Header
    pdf.set_font('helvetica', 'B', 10)
    pdf.cell(60, 8, 'Process Name', 1)
    pdf.cell(30, 8, 'PID', 1)
    pdf.cell(40, 8, 'CPU %', 1)
    pdf.cell(60, 8, 'Memory (MB)', 1)
    pdf.ln()
    
    pdf.set_font('helvetica', '', 10)
    for p in top_cpu:
        name = str(p['name'])[:25]
        cpu = p['cpu_percent'] or 0
        mem_mb = (p['memory_info'].rss / (1024**2)) if p['memory_info'] else 0
        
        if cpu > 10: # Highlight processes using significant CPU
            pdf.set_fill_color(255, 200, 200)
            fill = True
        else:
            fill = False
            
        pdf.cell(60, 8, name, 1, fill=fill)
        pdf.cell(30, 8, str(p['pid']), 1, fill=fill)
        pdf.cell(40, 8, f"{cpu:.1f}%", 1, fill=fill)
        pdf.cell(60, 8, f"{mem_mb:.1f} MB", 1, fill=fill)
        pdf.ln()
        
    pdf.ln(10)
    
    # Memory intensive
    pdf.section_title('Top 10 Processes by Memory Usage (MB)')
    # Sort by Memory
    top_mem = sorted(processes, key=lambda x: x['memory_info'].rss if x['memory_info'] else 0, reverse=True)[:10]
    
    # Table Header
    pdf.set_font('helvetica', 'B', 10)
    pdf.cell(60, 8, 'Process Name', 1)
    pdf.cell(30, 8, 'PID', 1)
    pdf.cell(40, 8, 'CPU %', 1)
    pdf.cell(60, 8, 'Memory (MB)', 1)
    pdf.ln()
    
    pdf.set_font('helvetica', '', 10)
    for p in top_mem:
        name = str(p['name'])[:25]
        cpu = p['cpu_percent'] or 0
        mem_mb = (p['memory_info'].rss / (1024**2)) if p['memory_info'] else 0
        
        if mem_mb > 1000: # Highlight processes using > 1GB RAM
            pdf.set_fill_color(255, 230, 150)
            fill = True
        else:
            fill = False
            
        pdf.cell(60, 8, name, 1, fill=fill)
        pdf.cell(30, 8, str(p['pid']), 1, fill=fill)
        pdf.cell(40, 8, f"{cpu:.1f}%", 1, fill=fill)
        pdf.cell(60, 8, f"{mem_mb:.1f} MB", 1, fill=fill)
        pdf.ln()

    # --- Recommendations ---
    pdf.add_page()
    pdf.chapter_title('3. Observations & Recommendations')
    pdf.set_font('helvetica', '', 11)
    
    issues = []
    if cpu_usage > 70:
        issues.append("- HIGH CPU USAGE detected. Check if any unnecessary background tasks are running.")
    if mem.percent > 85:
        issues.append("- RAM usage is CRITICAL. Consider closing memory-heavy applications like browser tabs or dedicated editors.")
    if disk.percent > 90:
        issues.append("- DISK space is running low. It might affect virtual memory and system performance.")
    
    if not issues:
        pdf.cell(0, 8, "No abnormal behavior detected. Your system is running optimally.", ln=True)
    else:
        pdf.set_text_color(255, 0, 0)
        pdf.set_font('helvetica', 'B', 11)
        pdf.cell(0, 8, "ATTENTION REQUIRED:", ln=True)
        pdf.set_font('helvetica', '', 11)
        for issue in issues:
            pdf.multi_cell(0, 8, issue)
        pdf.set_text_color(0,0,0)

    pdf.ln(5)
    pdf.chapter_title('4. Glossary')
    pdf.set_font('helvetica', 'I', 9)
    pdf.multi_cell(0, 6, "CPU Usage: Central Processing Unit load. High usage can cause system lag.\nMemory (RAM): Temporary workspace for active applications. Exceeding this triggers 'Swapping' to Disk, which is much slower.\nDisk Usage: Percentage of storage used. SSDs perform best with some free space.")

    target_file = '작업관리자.pdf'
    pdf.output(target_file)
    print(f"Report saved to {target_file}")

if __name__ == "__main__":
    generate_report()
