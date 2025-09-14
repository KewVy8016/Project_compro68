import pandas as pd
import os
import struct
from tabulate import tabulate
from datetime import datetime

# กำหนดชื่อไฟล์และพาธ
STUDENT_FILE_NAME = 'student.bin'
REPORT_FILE_NAME = 'student_report.txt'
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

def print_report(df):
    """สร้างและแสดงรายงานสรุปผลการลงทะเบียน"""
    report_string = ""
    report_string += "=========================================================================================\n"
    report_string += "                      Student Registration Report\n"
    report_string += "=========================================================================================\n"
    
    report_string += tabulate(df, headers='keys', tablefmt='grid') + "\n"
    report_string += "-----------------------------------------------------------------------------------------\n"
    
    total_students = len(df)
    students_by_major = df['MAJOR'].value_counts()
    status_counts = df['STATUS'].value_counts()
    
    # แก้ไขส่วนนี้เพื่อให้ตรงตามที่คุณต้องการ
    report_string += f"Total students in this section: {total_students}\n"
    report_string += f"Students by Major:\n"
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
    if not df.empty:
        most_common_year = df['YEAR'].mode().tolist()
        most_common_major = df['MAJOR'].mode().tolist()
        most_common_date = df['REGISTRATION DATE'].mode().tolist()
        
        least_common_major_counts = students_by_major.sort_values(ascending=True)
        least_common_major_name = least_common_major_counts.index[0]
        least_common_major_count = least_common_major_counts.iloc[0]

        report_string += f"- Year with the most registrations: Year {most_common_year[0]} ({df['YEAR'].value_counts()[most_common_year[0]]} students)\n"
        report_string += f"- Major with the most registrations: {most_common_major[0]} ({df['MAJOR'].value_counts()[most_common_major[0]]} students)\n"
        report_string += f"- Major with the least registrations: {least_common_major_name} ({least_common_major_count} students)\n"
        report_string += f"- Date with the most registrations: {most_common_date[0]} ({df['REGISTRATION DATE'].value_counts()[most_common_date[0]]} students)\n"
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
if __name__ == "__main__":
    student_records = read_all_records_from_file()
    
    if student_records:
        df = pd.DataFrame(student_records)
        report_content = print_report(df)
        write_report_to_text_file(report_content)
        read_text_file()
    else:
        print("ไม่พบข้อมูลนักเรียนในไฟล์ หรือมีข้อผิดพลาดในการอ่านไฟล์")