import struct
import os
import datetime

# กำหนดพาธของไฟล์ฐานข้อมูล
current_dir = os.path.dirname(os.path.abspath(__file__))
main_dir = os.path.dirname(current_dir)
REGISTRATION_FILE_PATH = os.path.join(main_dir, 'registration.bin')

# รูปแบบของข้อมูลการลงทะเบียนเรียน
# <I: register_id (unsigned int, 4 bytes)
# 16s: student_id (string, 16 bytes)
# 16s: course_id (string, 16 bytes)
# d: registration_date (double, 8 bytes for timestamp)
# B: status (unsigned char, 1 byte)
REGISTRATION_RECORD_FORMAT = '<I16s16sdB'
REGISTRATION_RECORD_SIZE = struct.calcsize(REGISTRATION_RECORD_FORMAT)

def create_registration_record(register_id, student_id, course_id, registration_date, status):
    """สร้างบันทึกข้อมูลการลงทะเบียนในรูปแบบไบนารี"""
    packed_student_id = student_id.encode('utf-8')[:16].ljust(16, b'\x00')
    packed_course_id = course_id.encode('utf-8')[:16].ljust(16, b'\x00')
    try:
        record = struct.pack(
            REGISTRATION_RECORD_FORMAT,
            register_id,
            packed_student_id,
            packed_course_id,
            registration_date,
            status
        )
        return record
    except struct.error as e:
        print(f"เกิดข้อผิดพลาดในการแพ็คข้อมูล: {e}")
        return None

def read_registration_record(record_data):
    """อ่านบันทึกข้อมูลการลงทะเบียนจากรูปแบบไบนารี"""
    try:
        unpacked_data = struct.unpack(REGISTRATION_RECORD_FORMAT, record_data)
        register_id = unpacked_data[0]
        student_id = unpacked_data[1].strip(b'\x00').decode('utf-8')
        course_id = unpacked_data[2].strip(b'\x00').decode('utf-8')
        registration_date = datetime.datetime.fromtimestamp(unpacked_data[3])
        status = unpacked_data[4]
        return {
            'register_id': register_id,
            'student_id': student_id,
            'course_id': course_id,
            'registration_date': registration_date,
            'status': status
        }
    except struct.error as e:
        print(f"เกิดข้อผิดพลาดในการอันแพ็คข้อมูล: {e}")
        return None

def write_record_to_file(record, file_path=REGISTRATION_FILE_PATH):
    """เขียนบันทึกข้อมูลลงในไฟล์ไบนารี"""
    try:
        with open(file_path, 'ab') as f:
            f.write(record)
    except IOError as e:
        print(f"เกิดข้อผิดพลาดในการเขียนไฟล์: {e}")

def read_all_records_from_file(file_path=REGISTRATION_FILE_PATH):
    """อ่านบันทึกข้อมูลทั้งหมดจากไฟล์ไบนารี"""
    records = []
    try:
        if not os.path.exists(file_path):
            return records
        with open(file_path, 'rb') as f:
            while True:
                record_data = f.read(REGISTRATION_RECORD_SIZE)
                if not record_data:
                    break
                records.append(read_registration_record(record_data))
    except IOError as e:
        print(f"เกิดข้อผิดพลาดในการอ่านไฟล์: {e}")
    return records

def get_next_register_id():
    """หา ID การลงทะเบียนถัดไป"""
    records = read_all_records_from_file()
    if not records:
        return 1
    return max(r['register_id'] for r in records) + 1

def add_registration():
    """เพิ่มข้อมูลการลงทะเบียนใหม่"""
    register_id = get_next_register_id()
    student_id = input("ป้อนรหัสนักเรียน: ")
    course_id = input("ป้อนรหัสวิชา: ")
    
    try:
        status = int(input("ป้อนสถานะ (1 = ลงทะเบียนแล้ว, 0 = ยกเลิก): "))
        if status not in [0, 1]:
            raise ValueError
    except ValueError:
        print("สถานะไม่ถูกต้อง กรุณาป้อนเป็นตัวเลข 0 หรือ 1")
        return
        
    registration_date = datetime.datetime.now().timestamp()
    
    record = create_registration_record(register_id, student_id, course_id, registration_date, status)
    if record:
        write_record_to_file(record)
        print("เพิ่มข้อมูลการลงทะเบียนสำเร็จ!")

def view_registrations():
    """แสดงข้อมูลการลงทะเบียนทั้งหมด"""
    registrations = read_all_records_from_file()
    if not registrations:
        print("ไม่พบข้อมูลการลงทะเบียนในระบบ")
        return
    print("\n--- รายการการลงทะเบียนทั้งหมด ---")
    status_map = {1: 'Registered', 0: 'Dropped'}
    print(f"{'ID':<5} | {'รหัสนักเรียน':<16} | {'รหัสวิชา':<16} | {'วันลงทะเบียน':<20} | {'สถานะ':<10}")
    print("-" * 75)
    for reg in registrations:
        if reg:
            status_text = status_map.get(reg['status'], 'N/A')
            date_str = reg['registration_date'].strftime('%Y-%m-%d %H:%M')
            print(f"{reg['register_id']:<5} | {reg['student_id']:<16} | {reg['course_id']:<16} | {date_str:<20} | {status_text:<10}")
    print("-------------------------")


def update_registration():
    """แก้ไขข้อมูลการลงทะเบียน"""
    try:
        reg_id_to_update = int(input("ป้อนรหัส ID การลงทะเบียนที่ต้องการแก้ไข: "))
    except ValueError:
        print("รหัส ID ไม่ถูกต้อง กรุณาป้อนเป็นตัวเลข")
        return

    registrations = read_all_records_from_file()
    found = False
    new_records = []

    for reg in registrations:
        if reg and reg['register_id'] == reg_id_to_update:
            found = True
            print("==========================================")
            print("    พบข้อมูลการลงทะเบียนที่ต้องการแก้ไข")
            print("==========================================")
            print(f"ID การลงทะเบียน: {reg['register_id']}")
            print(f"รหัสนักเรียน: {reg['student_id']}")
            print(f"รหัสวิชา: {reg['course_id']}")
            print(f"สถานะปัจจุบัน: {'Registered' if reg['status'] == 1 else 'Dropped'}")
            print("==========================================")

            new_status = input("ป้อนสถานะใหม่ (1=Registered, 0=Dropped) (Enter เพื่อใช้ค่าเดิม): ")
            if new_status:
                try:
                    new_status = int(new_status)
                    if new_status not in [0, 1]:
                        raise ValueError
                    reg['status'] = new_status
                except ValueError:
                    print("สถานะไม่ถูกต้อง ใช้ค่าเดิม")
        
        if reg:
            updated_record = create_registration_record(
                reg['register_id'],
                reg['student_id'],
                reg['course_id'],
                reg['registration_date'].timestamp(),
                reg['status']
            )
            if updated_record:
                new_records.append(updated_record)
    
    if found:
        try:
            if os.path.exists(REGISTRATION_FILE_PATH):
                os.remove(REGISTRATION_FILE_PATH)
            for record in new_records:
                write_record_to_file(record)
            print("แก้ไขข้อมูลสำเร็จ!")
        except IOError as e:
            print(f"เกิดข้อผิดพลาดในการแก้ไขไฟล์: {e}")
    else:
        print("ไม่พบรหัส ID การลงทะเบียนที่ต้องการแก้ไข")

def delete_registration():
    """ลบข้อมูลการลงทะเบียนแบบถาวร"""
    try:
        reg_id_to_delete = int(input("ป้อนรหัส ID การลงทะเบียนที่ต้องการลบถาวร: "))
    except ValueError:
        print("รหัส ID ไม่ถูกต้อง กรุณาป้อนเป็นตัวเลข")
        return

    registrations = read_all_records_from_file()
    found = False
    remaining_records = []

    for reg in registrations:
        if reg and reg['register_id'] == reg_id_to_delete:
            found = True
            print("ลบข้อมูลการลงทะเบียนสำเร็จ!")
        elif reg:
            remaining_records.append(reg)

    if found:
        try:
            if os.path.exists(REGISTRATION_FILE_PATH):
                os.remove(REGISTRATION_FILE_PATH)
            for reg in remaining_records:
                record = create_registration_record(
                    reg['register_id'],
                    reg['student_id'],
                    reg['course_id'],
                    reg['registration_date'].timestamp(),
                    reg['status']
                )
                if record:
                    write_record_to_file(record)
        except IOError as e:
            print(f"เกิดข้อผิดพลาดในการลบไฟล์: {e}")
    else:
        print("ไม่พบรหัส ID การลงทะเบียนที่ต้องการลบ")

def registration_menu():
    """เมนูย่อยสำหรับจัดการข้อมูลการลงทะเบียน (CRUD)"""
    while True:
        print("\n===== ระบบจัดการข้อมูลการลงทะเบียน =====")
        print("1. เพิ่มข้อมูลการลงทะเบียน")
        print("2. ดูข้อมูลการลงทะเบียนทั้งหมด")
        print("3. แก้ไขข้อมูลการลงทะเบียน")
        print("4. ลบข้อมูลการลงทะเบียน")
        print("0. กลับสู่เมนูหลัก")
        
        choice = input("กรุณาเลือกเมนู: ")
        
        if choice == '1':
            add_registration()
        elif choice == '2':
            view_registrations()
        elif choice == '3':
            update_registration()
        elif choice == '4':
            delete_registration()
        elif choice == '0':
            print("ย้อนกลับสู่เมนูหลัก...")
            break
        else:
            print("ตัวเลือกไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง")
