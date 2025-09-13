import struct
import os

# ชื่อไฟล์สำหรับจัดเก็บข้อมูลนักเรียน
STUDENT_FILE_NAME = 'student.bin'

# กำหนดพาธของไฟล์ให้บันทึกในโฟลเดอร์หลัก (main)
# จาก Project_compro68/main/module ไปที่ Project_compro68/main/student.bin
current_dir = os.path.dirname(os.path.abspath(__file__))
main_dir = os.path.dirname(current_dir)
STUDENT_FILE_PATH = os.path.join(main_dir, STUDENT_FILE_NAME)

# รูปแบบของข้อมูลที่จะจัดเก็บในแต่ละ record ตามตารางที่กำหนด
# <16s: student_id (string, 16 bytes)
# 50s: first_name (string, 50 bytes)
# 50s: last_name (string, 50 bytes)
# 20s: major (string, 20 bytes)
# B: year_level (unsigned char, 1 byte)
# B: status (unsigned char, 1 byte)
STUDENT_RECORD_FORMAT = '<16s50s50s20sB B'
STUDENT_RECORD_SIZE = struct.calcsize(STUDENT_RECORD_FORMAT)

def create_student_record(student_id, first_name, last_name, major, year_level, status):
    """สร้างบันทึกข้อมูลนักเรียนในรูปแบบไบนารี"""
    packed_student_id = student_id.encode('utf-8')[:16].ljust(16, b'\x00')
    packed_first_name = first_name.encode('utf-8')[:50].ljust(50, b'\x00')
    packed_last_name = last_name.encode('utf-8')[:50].ljust(50, b'\x00')
    packed_major = major.encode('utf-8')[:20].ljust(20, b'\x00')
    try:
        record = struct.pack(
            STUDENT_RECORD_FORMAT,
            packed_student_id,
            packed_first_name,
            packed_last_name,
            packed_major,
            year_level,
            status
        )
        return record
    except struct.error as e:
        print(f"เกิดข้อผิดพลาดในการแพ็คข้อมูล: {e}")
        return None

def read_student_record(record_data):
    """อ่านบันทึกข้อมูลนักเรียนจากรูปแบบไบนารี"""
    try:
        unpacked_data = struct.unpack(STUDENT_RECORD_FORMAT, record_data)
        student_id = unpacked_data[0].strip(b'\x00').decode('utf-8')
        first_name = unpacked_data[1].strip(b'\x00').decode('utf-8')
        last_name = unpacked_data[2].strip(b'\x00').decode('utf-8')
        major = unpacked_data[3].strip(b'\x00').decode('utf-8')
        return {
            'student_id': student_id,
            'first_name': first_name,
            'last_name': last_name,
            'major': major,
            'year_level': unpacked_data[4],
            'status': unpacked_data[5]
        }
    except struct.error as e:
        print(f"เกิดข้อผิดพลาดในการอันแพ็คข้อมูล: {e}")
        return None

def write_record_to_file(record, file_path=STUDENT_FILE_PATH):
    """เขียนบันทึกข้อมูลลงในไฟล์ไบนารี"""
    try:
        with open(file_path, 'ab') as f:
            f.write(record)
    except IOError as e:
        print(f"เกิดข้อผิดพลาดในการเขียนไฟล์: {e}")

def read_all_records_from_file(file_path=STUDENT_FILE_PATH):
    """อ่านบันทึกข้อมูลทั้งหมดจากไฟล์ไบนารี"""
    records = []
    try:
        if not os.path.exists(file_path):
            return records
        with open(file_path, 'rb') as f:
            while True:
                record_data = f.read(STUDENT_RECORD_SIZE)
                if not record_data:
                    break
                records.append(read_student_record(record_data))
    except IOError as e:
        print(f"เกิดข้อผิดพลาดในการอ่านไฟล์: {e}")
    return records

# --- ฟังก์ชัน CRUD หลักที่ใช้ในเมนู ---

def add_student():
    """เพิ่มข้อมูลนักเรียนใหม่"""
    student_id = input("ป้อนรหัสนักเรียน (ไม่เกิน 16 ตัวอักษร): ")
    first_name = input("ป้อนชื่อจริง (ไม่เกิน 50 ตัวอักษร): ")
    last_name = input("ป้อนนามสกุล (ไม่เกิน 50 ตัวอักษร): ")
    major = input("ป้อนสาขาวิชา (ไม่เกิน 20 ตัวอักษร): ")
    try:
        year_level = int(input("ป้อนชั้นปี (1, 2, 3, 4, ...): "))
        status = int(input("ป้อนสถานะ (1 = Active, 0 = Inactive): "))
    except ValueError:
        print("ข้อมูลที่ป้อนไม่ถูกต้อง กรุณาป้อนเป็นตัวเลข")
        return
    
    record = create_student_record(student_id, first_name, last_name, major, year_level, status)
    if record:
        write_record_to_file(record)
        print("เพิ่มข้อมูลนักเรียนสำเร็จ!")

def view_students():
    """แสดงข้อมูลนักเรียนทั้งหมด"""
    students = read_all_records_from_file()
    if not students:
        print("ไม่พบข้อมูลนักเรียนในระบบ")
        return
    print("\n--- รายการนักเรียนทั้งหมด ---")
    print(f"{'รหัส':<16} | {'ชื่อจริง':<20} | {'นามสกุล':<20} | {'สาขา':<10} | {'ชั้นปี':<5} | {'สถานะ':<10}")
    print("-" * 90)
    for student in students:
        if student:
            status_text = "Active" if student['status'] == 1 else "Inactive"
            print(f"{student['student_id']:<16} | {student['first_name']:<20} | {student['last_name']:<20} | {student['major']:<10} | {student['year_level']:<5} | {status_text:<10}")
    print("-------------------------")

def update_student():
    """แก้ไขข้อมูลนักเรียน"""
    student_id_to_update = input("ป้อนรหัสนักเรียนที่ต้องการแก้ไข: ")
    students = read_all_records_from_file()
    found = False
    new_records = []

    for student in students:
        if student and student['student_id'] == student_id_to_update:
            found = True
            print("==========================================")
            print("         พบข้อมูลนักเรียนที่ต้องการแก้ไข")
            print("==========================================")
            print(f"รหัสนักเรียน: {student['student_id']}")
            print(f"ชื่อจริง: {student['first_name']}")
            print(f"นามสกุล: {student['last_name']}")
            print(f"สาขาวิชา: {student['major']}")
            print(f"ชั้นปี: {student['year_level']}")
            print(f"สถานะ: {'Active' if student['status'] == 1 else 'Inactive'}")
            print("==========================================")

            new_first_name = input(f"ป้อนชื่อจริงใหม่ (Enter เพื่อใช้ค่าเดิม): ")
            if new_first_name:
                student['first_name'] = new_first_name

            new_last_name = input(f"ป้อนนามสกุลใหม่ (Enter เพื่อใช้ค่าเดิม): ")
            if new_last_name:
                student['last_name'] = new_last_name
            
            new_major = input(f"ป้อนสาขาวิชาใหม่ (Enter เพื่อใช้ค่าเดิม): ")
            if new_major:
                student['major'] = new_major

            new_year_level = input(f"ป้อนชั้นปีใหม่ (Enter เพื่อใช้ค่าเดิม): ")
            if new_year_level:
                try:
                    student['year_level'] = int(new_year_level)
                except ValueError:
                    print("ชั้นปีไม่ถูกต้อง ใช้ค่าเดิม")

            new_status = input(f"ป้อนสถานะใหม่ (1=กำลังศึกษา, 0=ไม่ได้ศึกษาเเล้ว) (Enter เพื่อใช้ค่าเดิม): ")
            if new_status:
                try:
                    student['status'] = int(new_status)
                except ValueError:
                    print("สถานะไม่ถูกต้อง ใช้ค่าเดิม")

        if student:
            updated_record = create_student_record(
                student['student_id'],
                student['first_name'],
                student['last_name'],
                student['major'],
                student['year_level'],
                student['status']
            )
            if updated_record:
                new_records.append(updated_record)
    
    if found:
        try:
            os.remove(STUDENT_FILE_PATH)
            for record in new_records:
                write_record_to_file(record)
            print("แก้ไขข้อมูลสำเร็จ!")
        except IOError as e:
            print(f"เกิดข้อผิดพลาดในการแก้ไขไฟล์: {e}")
    else:
        print("ไม่พบรหัสนักเรียนที่ต้องการแก้ไข")

def delete_student():
    """ลบข้อมูลนักเรียนแบบถาวร"""
    student_id_to_delete = input("ป้อนรหัสนักเรียนที่ต้องการลบ: ")
    students = read_all_records_from_file()
    found = False

    remaining_records = []

    for student in students:
        if student and student['student_id'] == student_id_to_delete:
            found = True
            print("ลบข้อมูลนักเรียนสำเร็จ!")
        elif student:
            remaining_records.append(student)

    if found:
        try:
            os.remove(STUDENT_FILE_PATH)
            for student in remaining_records:
                record = create_student_record(
                    student['student_id'],
                    student['first_name'],
                    student['last_name'],
                    student['major'],
                    student['year_level'],
                    student['status']
                )
                if record:
                    write_record_to_file(record)
        except IOError as e:
            print(f"เกิดข้อผิดพลาดในการลบไฟล์: {e}")
    else:
        print("ไม่พบรหัสนักเรียนที่ต้องการลบ")

def student_menu():
    """เมนูย่อยสำหรับจัดการข้อมูลนักเรียน (CRUD)"""
    while True:
        print("\n===== ระบบจัดการข้อมูลนักเรียน =====")
        print("1. เพิ่มข้อมูลนักเรียน")
        print("2. ดูข้อมูลนักเรียนทั้งหมด")
        print("3. แก้ไขข้อมูลนักเรียน")
        print("4. ลบข้อมูลนักเรียน")
        print("0. กลับสู่เมนูหลัก")
        
        choice = input("กรุณาเลือกเมนู: ")
        
        if choice == '1':
            add_student()
        elif choice == '2':
            view_students()
        elif choice == '3':
            update_student()
        elif choice == '4':
            delete_student()
        elif choice == '0':
            print("ย้อนกลับสู่เมนูหลัก...")
            break
        else:
            print("ตัวเลือกไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง")


