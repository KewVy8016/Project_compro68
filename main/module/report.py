import os
import struct
import datetime
from collections import defaultdict

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

STATUS_MAPPING = {1: 'ลงทะเบียน', 0: 'ถอน'}

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
            'STATUS': STATUS_MAPPING.get(status_code, 'ไม่ทราบ')
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
                courses[course['course_id']] = course
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
            'DATE': reg_date,
            'STATUS': STATUS_MAPPING.get(status, 'ไม่ทราบ'),
            'STATUS_CODE': status
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
    report += "                          รายงานนักศึกษา\n"
    report += "==========================================================================\n"

    headers = ["STUDENT ID", "FIRST NAME", "LAST NAME", "MAJOR", "YEAR", "STATUS"]
    col_widths = [20, 20, 20, 15, 8, 15]

    header_line = " | ".join(f"{h:<{col_widths[i]}}" for i, h in enumerate(headers))
    report += header_line + "\n"
    report += "-" * len(header_line) + "\n"

    for rec in records:
        row_data = [str(rec[h]) for h in ['STUDENT ID', 'FIRST NAME', 'LAST NAME', 'MAJOR', 'YEAR', 'STATUS']]
        row_line = " | ".join(f"{row_data[i]:<{col_widths[i]}}" for i in range(len(headers)))
        report += row_line + "\n"

    report += "--------------------------------------------------------------------------\n"
    report += f"จำนวนนักศึกษาทั้งหมด: {len(records)}\n"

    major_count = defaultdict(int)
    year_count = defaultdict(int)
    status_count = defaultdict(int)
    
    for rec in records:
        major_count[rec['MAJOR']] += 1
        year_count[rec['YEAR']] += 1
        status_count[rec['STATUS']] += 1
    
    report += "\n--- สถิตินักศึกษา ---\n"
    
    # สรุปตามสาขา
    report += "นักศึกษาแยกตามสาขา:\n"
    for major, count in major_count.items():
        report += f"  - สาขา {major}: {count} คน\n"
    
    # เพิ่ม: สรุปตามชั้นปี
    report += "\nนักศึกษาแยกตามชั้นปี:\n"
    for year in sorted(year_count.keys()):  # เรียงลำดับชั้นปีเพื่อความชัดเจน
        report += f"  - ปี {year}: {year_count[year]} คน\n"
    
    # ชั้นปีที่มีนักศึกษามากที่สุด
    if year_count:
        max_year = max(year_count, key=year_count.get)
        report += f"\n- ชั้นปีที่มีนักศึกษามากที่สุด: ปี {max_year} ({year_count[max_year]} คน)\n"
    
    print(report)
    return report

# -----------------------------
# ฟังก์ชันวิเคราะห์สถิติการลงทะเบียน
# -----------------------------
def analyze_registration_statistics(records, courses, students):
    """วิเคราะห์สถิติการลงทะเบียนแบบละเอียด"""
    
    student_dict = {s['STUDENT ID']: s for s in students}
    
    stats = {
        'course_stats': defaultdict(lambda: {'registered': 0, 'dropped': 0, 'students': []}),
        'major_stats': defaultdict(lambda: {'registered': 0, 'dropped': 0}),
        'year_stats': defaultdict(lambda: {'registered': 0, 'dropped': 0}),
        'date_stats': defaultdict(int),
        'popular_courses': [],
        'drop_rates': []
    }
    
    for rec in records:
        course_id = rec['COURSE ID']
        status = rec['STATUS_CODE']
        student_id = rec['STUDENT ID']
        date_key = rec['DATE'].strftime("%Y-%m-%d")
        
        student_info = student_dict.get(student_id, {})
        major = student_info.get('MAJOR', 'ไม่ระบุ')
        year = student_info.get('YEAR', 'ไม่ระบุ')
        
        if status == 1:
            stats['course_stats'][course_id]['registered'] += 1
            stats['course_stats'][course_id]['students'].append(student_id)
        else:
            stats['course_stats'][course_id]['dropped'] += 1
        
        if status == 1:
            stats['major_stats'][major]['registered'] += 1
        else:
            stats['major_stats'][major]['dropped'] += 1
        
        if status == 1:
            stats['year_stats'][year]['registered'] += 1
        else:
            stats['year_stats'][year]['dropped'] += 1
        
        if status == 1:
            stats['date_stats'][date_key] += 1
    
    for course_id, course_data in stats['course_stats'].items():
        total = course_data['registered'] + course_data['dropped']
        drop_rate = (course_data['dropped'] / total * 100) if total > 0 else 0
        
        course_info = courses.get(course_id, {})
        course_name = course_info.get('course_name', 'ไม่ระบุ')
        
        stats['popular_courses'].append({
            'course_id': course_id,
            'course_name': course_name,
            'registered': course_data['registered'],
            'dropped': course_data['dropped'],
            'total': total,
            'drop_rate': drop_rate
        })
        
        stats['drop_rates'].append({
            'course_id': course_id,
            'course_name': course_name,
            'drop_rate': drop_rate,
            'dropped': course_data['dropped'],
            'registered': course_data['registered']
        })
    
    stats['popular_courses'].sort(key=lambda x: x['registered'], reverse=True)
    stats['drop_rates'].sort(key=lambda x: x['drop_rate'], reverse=True)
    
    return stats

# -----------------------------
# Register Report + Course Name + สถิติ
# -----------------------------
def print_register_report(records, courses, students):
    report = ""
    report += "==========================================================================\n"
    report += "                        รายงานการลงทะเบียน\n"
    report += "==========================================================================\n"
    report += f"สร้างเมื่อ: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    stats = analyze_registration_statistics(records, courses, students)
    student_dict = {s['STUDENT ID']: s for s in students}
    
    course_groups = defaultdict(list)
    for rec in records:
        if rec['STATUS_CODE'] == 1:
            course_groups[rec['COURSE ID']].append(rec)
    
    for course_id, reg_list in course_groups.items():
        course_info = courses.get(course_id, {})
        course_name = course_info.get('course_name', 'ไม่ระบุ')
        academic_year = course_info.get('academic_year', 'ไม่ระบุ')
        semester = course_info.get('semester', 'ไม่ระบุ')
        
        report += f"วิชา: {course_id} - {course_name} [ปีการศึกษา {academic_year}, ภาคเรียน {semester}]\n"
        report += "ส่วน: 1\n\n"
        
        headers = ["STUDENT ID", "FIRST NAME", "LAST NAME", "MAJOR", "YEAR", "REGISTRATION DATE", "STATUS"]
        col_widths = [20, 20, 20, 15, 8, 20, 15]

        header_line = " | ".join(f"{h:<{col_widths[i]}}" for i, h in enumerate(headers))
        report += header_line + "\n"
        report += "-" * len(header_line) + "\n"

        for rec in reg_list:
            student_info = student_dict.get(rec['STUDENT ID'], {})
            row_data = [
                rec["STUDENT ID"],
                student_info.get('FIRST NAME', 'ไม่ระบุ'),
                student_info.get('LAST NAME', 'ไม่ระบุ'),
                student_info.get('MAJOR', 'ไม่ระบุ'),
                str(student_info.get('YEAR', 'ไม่ระบุ')),
                rec["DATE"].strftime("%Y-%m-%d"),
                rec["STATUS"]
            ]
            row_line = " | ".join(f"{row_data[i]:<{col_widths[i]}}" for i in range(len(headers)))
            report += row_line + "\n"

        course_stat = stats['course_stats'][course_id]
        total_registered = course_stat['registered']
        total_dropped = course_stat['dropped']
        total_students = total_registered + total_dropped
        drop_rate = (total_dropped / total_students * 100) if total_students > 0 else 0
        
        report += f"\nจำนวนนักศึกษาทั้งหมดในส่วนนี้: {total_registered}\n"
        
        major_count = defaultdict(int)
        year_count = defaultdict(int)
        date_count = defaultdict(int)
        
        for rec in reg_list:
            student_info = student_dict.get(rec['STUDENT ID'], {})
            major = student_info.get('MAJOR', 'ไม่ระบุ')
            year = student_info.get('YEAR', 'ไม่ระบุ')
            date = rec["DATE"].strftime("%Y-%m-%d")
            
            major_count[major] += 1
            year_count[year] += 1
            date_count[date] += 1
        
        report += "- นักศึกษาแยกตามสาขา:\n"
        for major, count in major_count.items():
            report += f"  {major}: {count}\n"
        
        report += "\n--- สรุปสถานะ ---\n"
        report += f"- ลงทะเบียน: {total_registered}\n"
        report += f"- ถอน: {total_dropped}\n"
        report += f"- อัตราการถอน: {drop_rate:.1f}%\n"
        
        if year_count:
            max_year = max(year_count, key=year_count.get)
            report += f"\n- ชั้นปีที่มีการลงทะเบียนมากที่สุด: ปี {max_year} [{year_count[max_year]} คน]\n"
        
        if major_count:
            max_major = max(major_count, key=major_count.get)
            min_major = min(major_count, key=major_count.get)
            report += f"- สาขาที่มีการลงทะเบียนมากที่สุด: {max_major} [{major_count[max_major]} คน]\n"
            report += f"- สาขาที่มีการลงทะเบียนน้อยที่สุด: {min_major} [{major_count[min_major]} คน]\n"
        
        if date_count:
            max_date = max(date_count, key=date_count.get)
            report += f"- วันที่ที่มีการลงทะเบียนมากที่สุด: {max_date} [{date_count[max_date]} คน]\n"
        
        report += "\n" + "="*80 + "\n\n"

    # คำนวณ total_registrations ก่อนใช้งาน
    total_registrations = len([r for r in records if r['STATUS_CODE'] == 1])

    report += "📊 การวิเคราะห์สถิติการลงทะเบียนแบบละเอียด\n"
    report += "="*80 + "\n\n"
    
    report += "🏆 วิชายอดนิยม (เรียงตามจำนวนผู้ลงทะเบียน):\n"
    report += "-" * 60 + "\n"
    for i, course in enumerate(stats['popular_courses'][:10], 1):
        report += f"{i}. {course['course_id']} - {course['course_name']}\n"
        report += f"   👥 ลงทะเบียน: {course['registered']} คน, ❌ ถอน: {course['dropped']} คน, "
        report += f"ทั้งหมด: {course['total']} คน, อัตราการถอน: {course['drop_rate']:.1f}%\n\n"
    
    report += "⚠️ วิชาที่มีอัตราการถอนสูงที่สุด:\n"
    report += "-" * 60 + "\n"
    for i, course in enumerate(stats['drop_rates'][:5], 1):
        if course['drop_rate'] > 0:
            report += f"{i}. {course['course_id']} - {course['course_name']}\n"
            report += f"   อัตราการถอน: {course['drop_rate']:.1f}% "
            report += f"({course['dropped']} จาก {course['dropped'] + course['registered']} คน)\n\n"
    
    report += "🎯 สถิติการลงทะเบียนแยกตามสาขา:\n"
    report += "-" * 60 + "\n"
    for major, data in stats['major_stats'].items():
        total = data['registered'] + data['dropped']
        drop_rate = (data['dropped'] / total * 100) if total > 0 else 0
        report += f"- {major}: ลงทะเบียน {data['registered']} คน, ถอน {data['dropped']} คน "
        report += f"(อัตราการถอน: {drop_rate:.1f}%)\n"
    report += "\n"
    
    report += "📚 สถิติการลงทะเบียนแยกตามชั้นปี:\n"
    report += "-" * 60 + "\n"
    for year, data in sorted(stats['year_stats'].items()):
        total = data['registered'] + data['dropped']
        drop_rate = (data['dropped'] / total * 100) if total > 0 else 0
        report += f"- ปี {year}: ลงทะเบียน {data['registered']} คน, ถอน {data['dropped']} คน "
        report += f"(อัตราการถอน: {drop_rate:.1f}%)\n"
    report += "\n"
    
    report += "📅 วันที่มีการลงทะเบียนสูงสุด (5 อันดับแรก):\n"
    report += "-" * 60 + "\n"
    sorted_dates = sorted(stats['date_stats'].items(), key=lambda x: x[1], reverse=True)
    for i, (date, count) in enumerate(sorted_dates[:5], 1):
        report += f"{i}. {date}: {count} คน\n"
    report += "\n"
    
    total_registered = sum(course['registered'] for course in stats['popular_courses'])
    total_dropped = sum(course['dropped'] for course in stats['popular_courses'])
    overall_drop_rate = (total_dropped / (total_registered + total_dropped) * 100) if (total_registered + total_dropped) > 0 else 0
    
    report += "📈 สรุปภาพรวมทั้งหมด:\n"
    report += "-" * 60 + "\n"
    report += f"- จำนวนวิชาที่เปิดสอน: {len(stats['popular_courses'])} วิชา\n"
    report += f"- จำนวนการลงทะเบียนทั้งหมด: {total_registered} คน\n"
    report += f"- จำนวนการถอนทั้งหมด: {total_dropped} คน\n"
    report += f"- อัตราการถอนโดยรวม: {overall_drop_rate:.1f}%\n"
    report += f"- จำนวนนักศึกษาที่ลงทะเบียน: {len(set([r['STUDENT ID'] for r in records if r['STATUS_CODE'] == 1]))} คน\n"
    
    report += "\n--------------------------------------------------------------------------\n"
    report += f"จำนวนการลงทะเบียนทั้งหมด (เฉพาะที่ลงทะเบียน): {total_registrations}\n"

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
                print("ไม่พบนักศึกษา")

        elif choice == '2':
            regs = read_all_registrations()
            courses = load_course_dict()
            students = read_all_students()
            if regs:
                report = print_register_report(regs, courses, students)
                write_report(report, REPORT_REGISTER_FILE_PATH)
            else:
                print("ไม่พบข้อมูลการลงทะเบียน")

        elif choice == '3':
            break
        else:
            print("ตัวเลือกไม่ถูกต้อง")