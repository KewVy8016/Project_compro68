import os
import struct
import datetime

# -----------------------------
# Path และ Format
# -----------------------------
STUDENT_FILE_NAME = 'student.bin'
REGISTER_FILE_NAME = 'registration.bin'
COURSE_FILE_NAME = 'CourseSubject.bin'

current_dir = os.path.dirname(os.path.abspath(__file__))
main_dir = os.path.dirname(current_dir)   # ขยับไป main/
STUDENT_FILE_PATH = os.path.join(main_dir, STUDENT_FILE_NAME)
REGISTER_FILE_PATH = os.path.join(main_dir, REGISTER_FILE_NAME)
COURSE_FILE_PATH = os.path.join(main_dir, COURSE_FILE_NAME)

# Report ให้ออกมาที่ main/
REPORT_STUDENT_FILE_PATH = os.path.join(main_dir, "student_report.txt")
REPORT_REGISTER_FILE_PATH = os.path.join(main_dir, "register_report.txt")

# Student Format
STUDENT_RECORD_FORMAT = '<16s50s50s20sBB'
STUDENT_RECORD_SIZE = struct.calcsize(STUDENT_RECORD_FORMAT)

# Register Format
REGISTER_RECORD_FORMAT = '<I16s16sdB'
REGISTER_RECORD_SIZE = struct.calcsize(REGISTER_RECORD_FORMAT)

# Course Format
COURSE_RECORD_FORMAT = '<10s50sB H B B'
COURSE_RECORD_SIZE = struct.calcsize(COURSE_RECORD_FORMAT)

STATUS_MAPPING = {1: 'Registered', 0: 'Dropped'}

# -----------------------------
# อ่าน student record
# -----------------------------
def read_student_record(record_data):
    try:
        unpacked_data = struct.unpack(STUDENT_RECORD_FORMAT, record_data)
        student_id = unpacked_data[0].strip(b'\x00').decode('utf-8')
        first_name = unpacked_data[1].strip(b'\x00').decode('utf-8')
        last_name = unpacked_data[2].strip(b'\x00').decode('utf-8')
        major = unpacked_data[3].strip(b'\x00').decode('utf-8')
        year_level = unpacked_data[4]
        status_code = unpacked_data[5]

        return {
            'STUDENT ID': student_id,
            'FIRST NAME': first_name,
            'LAST NAME': last_name,
            'MAJOR': major,
            'YEAR': year_level,
            'STATUS': STATUS_MAPPING.get(status_code, 'Unknown')
        }
    except struct.error:
        return None

def read_all_students(file_path=STUDENT_FILE_PATH):
    records = []
    if not os.path.exists(file_path):
        return records
    with open(file_path, 'rb') as f:
        while True:
            record_data = f.read(STUDENT_RECORD_SIZE)
            if not record_data:
                break
            record = read_student_record(record_data)
            if record:
                records.append(record)
    return records

# -----------------------------
# อ่าน course record
# -----------------------------
def read_course_record(record_data):
    try:
        unpacked_data = struct.unpack(COURSE_RECORD_FORMAT, record_data)
        course_id = unpacked_data[0].strip(b'\x00').decode('utf-8')
        course_name = unpacked_data[1].strip(b'\x00').decode('utf-8')
        return {
            'course_id': course_id,
            'course_name': course_name,
            'credit': unpacked_data[2],
            'academic_year': unpacked_data[3],
            'semester': unpacked_data[4],
            'is_active': unpacked_data[5]
        }
    except struct.error:
        return None

def load_course_dict(file_path=COURSE_FILE_PATH):
    courses = {}
    if not os.path.exists(file_path):
        return courses
    with open(file_path, 'rb') as f:
        while True:
            record_data = f.read(COURSE_RECORD_SIZE)
            if not record_data:
                break
            course = read_course_record(record_data)
            if course:
                courses[course['course_id']] = course['course_name']
    return courses

# -----------------------------
# อ่าน register record
# -----------------------------
def read_register_record(record_data):
    try:
        unpacked_data = struct.unpack(REGISTER_RECORD_FORMAT, record_data)
        reg_id = unpacked_data[0]
        student_id = unpacked_data[1].strip(b'\x00').decode('utf-8')
        course_id = unpacked_data[2].strip(b'\x00').decode('utf-8')
        reg_date = datetime.datetime.fromtimestamp(unpacked_data[3])
        status = unpacked_data[4]
        return {
            'REGISTER ID': reg_id,
            'STUDENT ID': student_id,
            'COURSE ID': course_id,
            'DATE': reg_date.strftime("%Y-%m-%d %H:%M:%S"),
            'STATUS': STATUS_MAPPING.get(status, 'Unknown')
        }
    except struct.error:
        return None

def read_all_registrations(file_path=REGISTER_FILE_PATH):
    records = []
    if not os.path.exists(file_path):
        return records
    with open(file_path, 'rb') as f:
        while True:
            record_data = f.read(REGISTER_RECORD_SIZE)
            if not record_data:
                break
            record = read_register_record(record_data)
            if record:
                records.append(record)
    return records

# -----------------------------
# Student Report
# -----------------------------
def print_student_report(records):
    report = ""
    report += "==========================================================================\n"
    report += "                          Student Report\n"
    report += "==========================================================================\n"

    headers = ["STUDENT ID", "FIRST NAME", "LAST NAME", "MAJOR", "YEAR", "STATUS"]
    col_widths = [15, 15, 15, 10, 5, 10]

    header_line = " | ".join(f"{h:<{col_widths[i]}}" for i, h in enumerate(headers))
    report += header_line + "\n"
    report += "-" * len(header_line) + "\n"

    for rec in records:
        row_data = [str(rec[h]) for h in headers]
        row_line = " | ".join(f"{row_data[i]:<{col_widths[i]}}" for i in range(len(headers)))
        report += row_line + "\n"

    report += "--------------------------------------------------------------------------\n"
    report += f"Total Students: {len(records)}\n"

    print(report)
    return report

# -----------------------------
# Register Report + Course Name
# -----------------------------
def print_register_report(records, courses):
    report = ""
    report += "==========================================================================\n"
    report += "                        Registration Report\n"
    report += "==========================================================================\n"

    headers = ["REGISTER ID", "STUDENT ID", "COURSE ID", "COURSE NAME", "DATE", "STATUS"]
    col_widths = [12, 15, 10, 20, 20, 12]

    header_line = " | ".join(f"{h:<{col_widths[i]}}" for i, h in enumerate(headers))
    report += header_line + "\n"
    report += "-" * len(header_line) + "\n"

    for rec in records:
        course_name = courses.get(rec['COURSE ID'], "N/A")
        row_data = [
            str(rec["REGISTER ID"]),
            rec["STUDENT ID"],
            rec["COURSE ID"],
            course_name,
            rec["DATE"],
            rec["STATUS"]
        ]
        row_line = " | ".join(f"{row_data[i]:<{col_widths[i]}}" for i in range(len(headers)))
        report += row_line + "\n"

    report += "--------------------------------------------------------------------------\n"
    report += f"Total Registrations: {len(records)}\n"

    status_counts = {}
    for rec in records:
        status_counts[rec['STATUS']] = status_counts.get(rec['STATUS'], 0) + 1
    for status, count in status_counts.items():
        report += f"- {status}: {count}\n"

    print(report)
    return report

# -----------------------------
# Save Report
# -----------------------------
def write_report(report_string, filename):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_string)
        print(f"✅ บันทึกรายงานลงไฟล์ {filename} เรียบร้อย")
    except IOError as e:
        print(f"❌ Error writing file: {e}")

# -----------------------------
# Main Menu
# -----------------------------
def generate_report():
    while True:
        print("\n--- เมนูรายงาน ---")
        print("1. ดูรายงานนักเรียน")
        print("2. ดูรายงานการลงทะเบียน")
        print("3. ย้อนกลับไปหน้าแรก")

        choice = input("เลือกเมนู: ")

        if choice == '1':
            students = read_all_students()
            if students:
                report = print_student_report(students)
                write_report(report, REPORT_STUDENT_FILE_PATH)
            else:
                print("ไม่พบนักเรียน")

        elif choice == '2':
            regs = read_all_registrations()
            courses = load_course_dict()
            if regs:
                report = print_register_report(regs, courses)
                write_report(report, REPORT_REGISTER_FILE_PATH)
            else:
                print("ไม่พบข้อมูลการลงทะเบียน")

        elif choice == '3':
            break
        else:
            print("ตัวเลือกไม่ถูกต้อง")
