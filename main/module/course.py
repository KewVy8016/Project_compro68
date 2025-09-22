import struct
import os

COURSE_FILE_NAME = 'CourseSubject.bin'
COURSE_RECORD_FORMAT = '<10s50sB H B B'
COURSE_RECORD_SIZE = struct.calcsize(COURSE_RECORD_FORMAT)

current_dir = os.path.dirname(os.path.abspath(__file__))
main_dir = os.path.dirname(current_dir)
COURSE_FILE_PATH = os.path.join(main_dir, COURSE_FILE_NAME)

def create_course_record(course_id, course_name, credit, academic_year, semester, is_active):
    """สร้างบันทึกข้อมูลรายวิชาในรูปแบบไบนารี"""
    packed_course_id = course_id.encode('utf-8')[:10].ljust(10, b'\x00')
    packed_course_name = course_name.encode('utf-8')[:50].ljust(50, b'\x00')
    try:
        record = struct.pack(
            COURSE_RECORD_FORMAT,
            packed_course_id,
            packed_course_name,
            credit,
            academic_year,
            semester,
            is_active
        )
        return record
    except struct.error as e:
        print(f"เกิดข้อผิดพลาดในการแพ็คข้อมูล: {e}")
        return None

def read_course_record(record_data):
    """อ่านบันทึกข้อมูลรายวิชาจากรูปแบบไบนารี"""
    try:
        unpacked_data = struct.unpack(COURSE_RECORD_FORMAT, record_data)
        course_id = unpacked_data[0].strip(b'\x00').decode('utf-8')
        course_name = unpacked_data[1].strip(b'\x00').decode('utf-8')
        return {
            'COURSE ID': course_id,
            'COURSE NAME': course_name,
            'CREDIT': unpacked_data[2],
            'ACADEMIC YEAR': unpacked_data[3],
            'SEMESTER': unpacked_data[4],
            'STATUS': 'Active' if unpacked_data[5] == 1 else 'Inactive'
        }
    except struct.error as e:
        print(f"เกิดข้อผิดพลาดในการอันแพ็คข้อมูล: {e}")
        return None

def write_record_to_file(record, file_path=COURSE_FILE_PATH):
    """เขียนบันทึกข้อมูลลงในไฟล์ไบนารี"""
    try:
        with open(file_path, 'ab') as f:
            f.write(record)
    except IOError as e:
        print(f"เกิดข้อผิดพลาดในการเขียนไฟล์: {e}")

def read_all_records_from_file(file_path=COURSE_FILE_PATH):
    """อ่านบันทึกข้อมูลทั้งหมดจากไฟล์ไบนารี"""
    records = []
    try:
        if not os.path.exists(file_path):
            return records
        with open(file_path, 'rb') as f:
            while True:
                record_data = f.read(COURSE_RECORD_SIZE)
                if not record_data:
                    break
                record = read_course_record(record_data)
                if record:
                    records.append(record)
    except IOError as e:
        print(f"เกิดข้อผิดพลาดในการอ่านไฟล์: {e}")
    return records

def print_course_report(records, title="รายงานรายวิชา"):
    """แสดงรายงานรายวิชาในรูปแบบตาราง"""
    report = ""
    report += "==========================================================================\n"
    report += f"                          {title}\n"
    report += "==========================================================================\n"

    headers = ["COURSE ID", "COURSE NAME", "CREDIT", "ACADEMIC YEAR", "SEMESTER", "STATUS"]
    col_widths = [20, 20, 20, 15, 8, 15]

    header_line = " | ".join(f"{h:<{col_widths[i]}}" for i, h in enumerate(headers))
    report += header_line + "\n"
    report += "-" * len(header_line) + "\n"

    for rec in records:
        row_data = [str(rec[h]) for h in headers]
        # ตัดข้อความหากยาวเกิน
        for i in range(len(row_data)):
            if len(row_data[i]) > col_widths[i]:
                row_data[i] = row_data[i][:col_widths[i]-3] + "..."
        row_line = " | ".join(f"{row_data[i]:<{col_widths[i]}}" for i in range(len(headers)))
        report += row_line + "\n"

    report += "--------------------------------------------------------------------------\n"
    print(report)

def add_course():
    """เพิ่มข้อมูลรายวิชาใหม่"""
    course_id = input("ป้อนรหัสวิชา (ไม่เกิน 10 ตัวอักษร): ")
    course_name = input("ป้อนชื่อวิชา (ไม่เกิน 50 ตัวอักษร): ")
    try:
        credit = int(input("ป้อนหน่วยกิต: "))
        academic_year = int(input("ป้อนปีการศึกษา (เช่น 2568): "))
        semester = int(input("ป้อนภาคเรียน (1, 2, 3): "))
        is_active = int(input("ป้อนสถานะ (1 = Active, 0 = Inactive): "))
    except ValueError:
        print("ข้อมูลที่ป้อนไม่ถูกต้อง กรุณาป้อนเป็นตัวเลข")
        return

    record = create_course_record(course_id, course_name, credit, academic_year, semester, is_active)
    if record:
        write_record_to_file(record)
        print("เพิ่มข้อมูลรายวิชาสำเร็จ!")

def view_all_courses():
    """แสดงข้อมูลรายวิชาทั้งหมด"""
    courses = read_all_records_from_file()
    if not courses:
        print("ไม่พบข้อมูลรายวิชาในระบบ")
        return
    print_course_report(courses, title="รายงานรายวิชา")

def view_single_course():
    """แสดงข้อมูลรายวิชาเดียวตามรหัสวิชา"""
    course_id = input("ป้อนรหัสวิชาที่ต้องการดู: ")
    courses = read_all_records_from_file()
    found = False
    
    for course in courses:
        if course and course['COURSE ID'] == course_id:
            found = True
            print("\n==========================================")
            print("      ข้อมูลรายวิชาที่ค้นหา")
            print("==========================================")
            print(f"รหัสวิชา: {course['COURSE ID']}")
            print(f"ชื่อวิชา: {course['COURSE NAME']}")
            print(f"หน่วยกิต: {course['CREDIT']}")
            print(f"ปีการศึกษา: {course['ACADEMIC YEAR']}")
            print(f"ภาคเรียน: {course['SEMESTER']}")
            print(f"สถานะ: {course['STATUS']}")
            print("==========================================")
            break
    
    if not found:
        print("ไม่พบรหัสวิชาที่ต้องการดู")

def view_filtered_courses():
    """แสดงข้อมูลรายวิชาที่กรองตามเงื่อนไข"""
    print("\n--- ตัวเลือกการกรอง ---")
    print("1. กรองตามปีการศึกษา")
    print("2. กรองตามภาคเรียน")
    print("3. กรองตามสถานะ (Active)")
    print("4. กรองตามปีการศึกษาและภาคเรียน")
    print("5. กลับไปเมนูหลัก")
    filter_choice = input("กรุณาเลือกการกรอง (1-5): ")
    
    courses = read_all_records_from_file()
    if not courses:
        print("ไม่พบข้อมูลรายวิชาในระบบ")
        return
    
    filtered_courses = []
    
    if filter_choice == '1':
        try:
            year = int(input("ป้อนปีการศึกษาที่ต้องการกรอง: "))
            filtered_courses = [c for c in courses if c and c['ACADEMIC YEAR'] == year]
        except ValueError:
            print("ปีการศึกษาไม่ถูกต้อง")
            return
    
    elif filter_choice == '2':
        try:
            sem = int(input("ป้อนภาคเรียนที่ต้องการกรอง (1, 2, 3): "))
            filtered_courses = [c for c in courses if c and c['SEMESTER'] == sem]
        except ValueError:
            print("ภาคเรียนไม่ถูกต้อง")
            return
    
    elif filter_choice == '3':
        filtered_courses = [c for c in courses if c and c['STATUS'] == 'Active']
    
    elif filter_choice == '4':
        try:
            year = int(input("ป้อนปีการศึกษาที่ต้องการกรอง: "))
            sem = int(input("ป้อนภาคเรียนที่ต้องการกรอง (1, 2, 3): "))
            filtered_courses = [c for c in courses if c and c['ACADEMIC YEAR'] == year and c['SEMESTER'] == sem]
        except ValueError:
            print("ข้อมูลกรองไม่ถูกต้อง")
            return
    
    elif filter_choice == '5':
        return
    
    else:
        print("ตัวเลือกไม่ถูกต้อง")
        return
    
    if not filtered_courses:
        print("ไม่พบข้อมูลที่ตรงตามเงื่อนไขการกรอง")
        return
    
    print_course_report(filtered_courses, title=f"รายงานรายวิชาที่กรอง ({len(filtered_courses)} รายการ)")

def update_course():
    """แก้ไขข้อมูลรายวิชา"""
    course_id_to_update = input("ป้อนรหัสวิชาที่ต้องการแก้ไข: ")
    courses = read_all_records_from_file()
    found = False
    new_records = []

    for course in courses:
        if course and course['COURSE ID'] == course_id_to_update:
            found = True
            print("==========================================")
            print("      พบข้อมูลวิชาที่ต้องการแก้ไข")
            print("==========================================")
            print(f"รหัสวิชา: {course['COURSE ID']}")
            print(f"ชื่อวิชา: {course['COURSE NAME']}")
            print(f"หน่วยกิต: {course['CREDIT']}")
            print(f"ปีการศึกษา: {course['ACADEMIC YEAR']}")
            print(f"ภาคเรียน: {course['SEMESTER']}")
            print(f"สถานะ: {course['STATUS']}")
            print("==========================================")
                        
            new_name = input("ป้อนชื่อวิชาใหม่ (Enter เพื่อใช้ค่าเดิม): ")
            if new_name:
                course['COURSE NAME'] = new_name
            
            new_credit = input("ป้อนหน่วยกิตใหม่ (Enter เพื่อใช้ค่าเดิม): ")
            if new_credit:
                try:
                    course['CREDIT'] = int(new_credit)
                except ValueError:
                    print("หน่วยกิตไม่ถูกต้อง ใช้ค่าเดิม")

            new_academic_year = input("ป้อนปีการศึกษาใหม่ (Enter เพื่อใช้ค่าเดิม): ")
            if new_academic_year:
                try:
                    course['ACADEMIC YEAR'] = int(new_academic_year)
                except ValueError:
                    print("ปีการศึกษาไม่ถูกต้อง ใช้ค่าเดิม")

            new_semester = input("ป้อนภาคเรียนใหม่ (Enter เพื่อใช้ค่าเดิม): ")
            if new_semester:
                try:
                    course['SEMESTER'] = int(new_semester)
                except ValueError:
                    print("ภาคเรียนไม่ถูกต้อง ใช้ค่าเดิม")

            new_active = input("ป้อนสถานะใหม่ (1 = Active, 0 = Inactive) (Enter เพื่อใช้ค่าเดิม): ")
            if new_active:
                try:
                    new_active_int = int(new_active)
                    if new_active_int in [0, 1]:
                        course['STATUS'] = 'Active' if new_active_int == 1 else 'Inactive'
                    else:
                        print("สถานะไม่ถูกต้อง ใช้ค่าเดิม")
                except ValueError:
                    print("สถานะไม่ถูกต้อง ใช้ค่าเดิม")

        updated_record = create_course_record(
            course['COURSE ID'],
            course['COURSE NAME'],
            course['CREDIT'],
            course['ACADEMIC YEAR'],
            course['SEMESTER'],
            1 if course['STATUS'] == 'Active' else 0
        )
        if updated_record:
            new_records.append(updated_record)
    
    if found:
        try:
            with open(COURSE_FILE_PATH, 'wb') as f:
                for record in new_records:
                    f.write(record)
            print("แก้ไขข้อมูลสำเร็จ!")
        except IOError as e:
            print(f"เกิดข้อผิดพลาดในการแก้ไขไฟล์: {e}")
    else:
        print("ไม่พบรหัสวิชาที่ต้องการแก้ไข")

def delete_course():
    """ลบข้อมูลรายวิชาแบบถาวร"""
    course_id_to_delete = input("ป้อนรหัสวิชาที่ต้องการลบถาวร: ")
    courses = read_all_records_from_file()
    found = False
    remaining_records = []
    
    for course in courses:
        if course and course['COURSE ID'] == course_id_to_delete:
            found = True
            print("ลบข้อมูลรายวิชาสำเร็จ!")
        else:
            remaining_records.append(course)

    if found:
        try:
            with open(COURSE_FILE_PATH, 'wb') as f:
                for course in remaining_records:
                    record = create_course_record(
                        course['COURSE ID'],
                        course['COURSE NAME'],
                        course['CREDIT'],
                        course['ACADEMIC YEAR'],
                        course['SEMESTER'],
                        1 if course['STATUS'] == 'Active' else 0
                    )
                    if record:
                        f.write(record)
        except IOError as e:
            print(f"เกิดข้อผิดพลาดในการลบไฟล์: {e}")
    else:
        print("ไม่พบรหัสวิชาที่ต้องการลบ")

def course_menu():
    """แสดงเมนูหลักและรับตัวเลือกจากผู้ใช้"""
    while True:
        print("\n===== ระบบจัดการรายวิชา =====")
        print("1. เพิ่มข้อมูลรายวิชา")
        print("2. ดูข้อมูลรายวิชาทั้งหมด")
        print("3. ดูข้อมูลรายวิชารายบุคคล")
        print("4. ดูข้อมูลรายวิชาแบบกรอง")
        print("5. แก้ไขข้อมูลรายวิชา")
        print("6. ลบข้อมูลรายวิชา")
        print("0. กลับสู่เมนูหลัก")
        choice = input("กรุณาเลือกเมนู (1-0): ")
            
        if choice == '1':
            add_course()
        elif choice == '2':
            view_all_courses()
        elif choice == '3':
            view_single_course()
        elif choice == '4':
            view_filtered_courses()
        elif choice == '5':
            update_course()
        elif choice == '6':
            delete_course()
        elif choice == '0':
            print("ย้อนกลับสู่เมนูหลัก...")
            break
        else:
            print("ตัวเลือกไม่ถูกต้อง กรุณาลองอีกครั้ง")

if __name__ == "__main__":
    course_menu()