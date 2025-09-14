import os
import struct

# กำหนดชื่อไฟล์และพาธ
STUDENT_FILE_NAME = 'student.bin'
REPORT_FILE_NAME = 'report.txt'
current_dir = os.path.dirname(os.path.abspath(__file__))
main_dir = os.path.dirname(current_dir)
STUDENT_FILE_PATH = os.path.join(main_dir, STUDENT_FILE_NAME)
REPORT_FILE_PATH = os.path.join(main_dir, REPORT_FILE_NAME)

# รูปแบบของข้อมูลในไฟล์ไบนารี
STUDENT_RECORD_FORMAT = '<16s50s50s20sB B'
STUDENT_RECORD_SIZE = struct.calcsize(STUDENT_RECORD_FORMAT)
STATUS_MAPPING = {1: 'Registered', 0: 'Dropped'}

def read_student_record(record_data):
    """อ่านบันทึกข้อมูลนักเรียนจากรูปแบบไบนารี"""
    try:
        unpacked_data = struct.unpack(STUDENT_RECORD_FORMAT, record_data)
        student_id = unpacked_data[0].strip(b'\x00').decode('utf-8')
        first_name = unpacked_data[1].strip(b'\x00').decode('utf-8')
        last_name = unpacked_data[2].strip(b'\x00').decode('utf-8')
        major = unpacked_data[3].strip(b'\x00').decode('utf-8')
        year_level = unpacked_data[4]
        status_code = unpacked_data[5]

        # ใช้ค่าวันที่ที่กำหนดไว้ตายตัวแทน
        registration_date = '2025-09-09'
        
        return {
            'STUDENT ID': student_id,
            'FIRST NAME': first_name,
            'LAST NAME': last_name,
            'MAJOR': major,
            'YEAR': year_level,
            'REGISTRATION DATE': registration_date,
            'STATUS': STATUS_MAPPING.get(status_code, 'Unknown')
        }
    except struct.error:
        return None

def read_all_records_from_file(file_path=STUDENT_FILE_PATH):
    """อ่านบันทึกข้อมูลทั้งหมดจากไฟล์ไบนารี"""
    records = []
    try:
        if not os.path.exists(file_path):
            print(f"❌ Error: ไม่พบไฟล์ '{file_path}'")
            return records
        with open(file_path, 'rb') as f:
            while True:
                record_data = f.read(STUDENT_RECORD_SIZE)
                if not record_data:
                    break
                record = read_student_record(record_data)
                if record:
                    records.append(record)
    except IOError as e:
        print(f"❌ เกิดข้อผิดพลาดในการอ่านไฟล์: {e}")
    return records

def format_table(records, headers):
    """สร้างตารางในรูปแบบข้อความจากรายการบันทึก"""
    column_widths = {
        'STUDENT ID': 15,
        'FIRST NAME': 20,
        'LAST NAME': 20,
        'MAJOR': 15,
        'YEAR': 5,
        'REGISTRATION DATE': 18,
        'STATUS': 12
    }
    
    table_string = ""
    
    # ส่วนหัวตาราง
    header_line = " | ".join(f"{h:<{column_widths[h]}}" for h in headers)
    table_string += header_line + "\n"
    table_string += "-" * len(header_line) + "\n"
    
    # ข้อมูลแต่ละแถว
    for record in records:
        row_data = [
            record['STUDENT ID'],
            record['FIRST NAME'],
            record['LAST NAME'],
            record['MAJOR'],
            str(record['YEAR']),
            record['REGISTRATION DATE'],
            record['STATUS']
        ]
        row_line = " | ".join(f"{d:<{column_widths[h]}}" for d, h in zip(row_data, headers))
        table_string += row_line + "\n"
        
    return table_string

def print_report(records):
    """สร้างและแสดงรายงานสรุปผลการลงทะเบียน"""
    report_string = ""
    report_string += "=========================================================================================\n"
    report_string += "                               Student Registration Report\n"
    report_string += "=========================================================================================\n"
    
    headers = ['STUDENT ID', 'FIRST NAME', 'LAST NAME', 'MAJOR', 'YEAR', 'REGISTRATION DATE', 'STATUS']
    report_string += format_table(records, headers) + "\n"
    report_string += "-----------------------------------------------------------------------------------------\n"
    
    total_students = len(records)
    
    # นับจำนวนนักเรียนตามสาขาวิชา สถานะ ปี และวันที่ลงทะเบียน
    students_by_major = {}
    status_counts = {}
    year_counts = {}
    date_counts = {}
    
    for record in records:
        major = record['MAJOR']
        status = record['STATUS']
        year = record['YEAR']
        reg_date = record['REGISTRATION DATE']
        
        students_by_major[major] = students_by_major.get(major, 0) + 1
        status_counts[status] = status_counts.get(status, 0) + 1
        year_counts[year] = year_counts.get(year, 0) + 1
        date_counts[reg_date] = date_counts.get(reg_date, 0) + 1
        
    report_string += f"Total students in this section: {total_students}\n"
    report_string += "Students by Major:\n"
    for major, count in students_by_major.items():
        report_string += f"  - {major}: {count}\n"
    
    report_string += "-----------------------------------------------------------------------------------------\n"
    report_string += "**Summary of Status:**\n"
    
    registered_status = STATUS_MAPPING[1]
    dropped_status = STATUS_MAPPING[0]
    
    registered_count = status_counts.get(registered_status, 0)
    report_string += f"  - {registered_status}: {registered_count}\n"
    
    dropped_count = status_counts.get(dropped_status, 0)
    report_string += f"  - {dropped_status}: {dropped_count}\n"

    report_string += "-----------------------------------------------------------------------------------------\n"
    report_string += "Summary:\n"
    
    if records:
        # ฟังก์ชันช่วยหาค่าที่พบบ่อยที่สุดและน้อยที่สุด
        def find_most_common(counts):
            if not counts:
                return None, 0
            most_common = max(counts, key=counts.get)
            return most_common, counts[most_common]

        def find_least_common(counts):
            if not counts:
                if not counts:
                    return None, 0
            least_common = min(counts, key=counts.get)
            return least_common, counts[least_common]

        most_common_year, most_common_year_count = find_most_common(year_counts)
        most_common_major, most_common_major_count = find_most_common(students_by_major)
        least_common_major, least_common_major_count = find_least_common(students_by_major)
        most_common_date, most_common_date_count = find_most_common(date_counts)

        report_string += f"- ปีที่มีนักเรียนลงทะเบียนมากที่สุด: Year {most_common_year} ({most_common_year_count} students)\n"
        report_string += f"- สาขาวิชาที่มีนักเรียนลงทะเบียนมากที่สุด: {most_common_major} ({most_common_major_count} students)\n"
        report_string += f"- สาขาวิชาที่มีนักเรียนลงทะเบียนน้อยที่สุด: {least_common_major} ({least_common_major_count} students)\n"
        report_string += f"- วันที่ลงทะเบียนมากที่สุด: {most_common_date} ({most_common_date_count} students)\n"
    else:
        report_string += "- No data to summarize.\n"
        
    report_string += "-----------------------------------------------------------------------------------------\n"

    print(report_string)
    
    return report_string

def write_report_to_text_file(report_string, file_path=REPORT_FILE_PATH):
    """บันทึกรายงานลงในไฟล์ .txt"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(report_string)
        print(f"✅ บันทึกรายงานลงในไฟล์ '{file_path}' เรียบร้อยแล้ว!")
    except IOError as e:
        print(f"❌ เกิดข้อผิดพลาดในการบันทึกไฟล์: {e}")

def read_text_file(file_path=REPORT_FILE_PATH):
    """อ่านและแสดงเนื้อหาจากไฟล์ .txt"""
    print(f"\n--- เนื้อหาจากไฟล์ '{file_path}' ---")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content)
    except FileNotFoundError:
        print(f"❌ ไม่พบไฟล์ '{file_path}'")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการอ่านไฟล์: {e}")

# --- Main Program Execution ---
def generate_report():
    """แสดงเมนูหลักและรับตัวเลือกจากผู้ใช้"""
    while True:
            print("\n--- เมนูจัดการรายวิชา ---")
            print("1. ดูข้อมูล REPORT ")
            print("2. ย้อนกลับไปหน้าแรก")
            choice = input("กรุณาเลือกเมนู: ")
                
            if choice == '1':
                student_records = read_all_records_from_file()
    
                if student_records:
                    report_content = print_report(student_records)
                    write_report_to_text_file(report_content)
                    read_text_file()
                else:
                    print("ไม่พบข้อมูลนักเรียนในไฟล์ หรือมีข้อผิดพลาดในการอ่านไฟล์")

            elif choice == '2':
                print("ย้อนกลับสู่เมนูหลัก...")
                break
            else:
                print("ตัวเลือกไม่ถูกต้อง กรุณาลองอีกครั้ง")
