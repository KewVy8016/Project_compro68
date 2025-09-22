import struct
import os
from datetime import datetime

# กำหนดพาธของไฟล์ฐานข้อมูล
current_dir = os.path.dirname(os.path.abspath(__file__))
main_dir = os.path.dirname(current_dir)
REGISTRATION_FILE_PATH = os.path.join(main_dir, 'registration.bin')
STUDENT_FILE_PATH = os.path.join(main_dir, 'student.bin')

# รูปแบบของข้อมูลนักเรียน
STUDENT_RECORD_FORMAT = '<16s50s50s20sBB'
STUDENT_RECORD_SIZE = struct.calcsize(STUDENT_RECORD_FORMAT)

# รูปแบบของข้อมูลการลงทะเบียนเรียน
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
        registration_date = datetime.fromtimestamp(unpacked_data[3])
        status = 'Registered' if unpacked_data[4] == 1 else 'Dropped'
        return {
            'ID': register_id,
            'STUDENT ID': student_id,
            'COURSE ID': course_id,
            'REGISTRATION DATE': registration_date,
            'STATUS': status
        }
    except (struct.error, ValueError) as e:
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
                record = read_registration_record(record_data)
                if record:
                    records.append(record)
    except IOError as e:
        print(f"เกิดข้อผิดพลาดในการอ่านไฟล์: {e}")
    return records

def get_next_register_id():
    """หา ID การลงทะเบียนถัดไป"""
    records = read_all_records_from_file()
    if not records:
        return 1
    valid_records = [r for r in records if r is not None]
    if not valid_records:
        return 1
    return max(r['ID'] for r in valid_records) + 1

def read_student_by_id(student_id):
    """อ่านข้อมูลนักเรียนจาก student.bin โดยใช้รหัสนักเรียน"""
    try:
        if not os.path.exists(STUDENT_FILE_PATH):
            print("ไม่พบไฟล์ student.bin")
            return None
            
        with open(STUDENT_FILE_PATH, 'rb') as f:
            while True:
                record_data = f.read(STUDENT_RECORD_SIZE)
                if not record_data:
                    break
                
                try:
                    unpacked_data = struct.unpack(STUDENT_RECORD_FORMAT, record_data)
                    current_student_id = unpacked_data[0].strip(b'\x00').decode('utf-8')
                    
                    if current_student_id == student_id:
                        status_map = {1: 'Active', 0: 'Inactive'}
                        status_text = status_map.get(unpacked_data[5], 'Unknown')
                        
                        return {
                            'student_id': current_student_id,
                            'first_name': unpacked_data[1].strip(b'\x00').decode('utf-8'),
                            'last_name': unpacked_data[2].strip(b'\x00').decode('utf-8'),
                            'major': unpacked_data[3].strip(b'\x00').decode('utf-8'),
                            'year_level': unpacked_data[4],
                            'status': status_text,
                            'status_code': unpacked_data[5]
                        }
                        
                except (struct.error, UnicodeDecodeError) as e:
                    print(f"ข้อผิดพลาดในการอ่าน record: {e}")
                    continue
                    
        return None
        
    except IOError as e:
        print(f"เกิดข้อผิดพลาดในการอ่านไฟล์นักเรียน: {e}")
        return None

def get_student_info_for_registration():
    """ดึงข้อมูลนักเรียนและยืนยันก่อนลงทะเบียน"""
    student_id = input("ป้อนรหัสนักเรียน: ").strip()
    
    student = read_student_by_id(student_id)
    
    if not student:
        print(f"ไม่พบนักเรียนที่มีรหัส {student_id} ในระบบ")
        return None
    
    if student['status_code'] == 0:
        print(f"นักเรียนรหัส {student_id} มีสถานะ Inactive ไม่สามารถลงทะเบียนได้")
        return None
    
    print("\n=== พบข้อมูลนักเรียน ===")
    print(f"รหัสนักเรียน: {student['student_id']}")
    print(f"ชื่อ: {student['first_name']} {student['last_name']}")
    print(f"สาขา: {student['major']}")
    print(f"ชั้นปี: {student['year_level']}")
    print(f"สถานะ: {student['status']}")
    print("=======================")
    
    confirm = input("ใช่คนนี้ใช่หรือไม่? (y/n): ").lower()
    if confirm == 'y' or confirm == 'yes':
        return student
    else:
        print("ยกเลิกการเลือกนักเรียน")
        return None

def print_registration_report(records, title="รายงานการลงทะเบียน"):
    """แสดงรายงานการลงทะเบียนในรูปแบบตาราง"""
    report = ""
    report += "==========================================================================\n"
    report += f"                          {title}\n"
    report += "==========================================================================\n"

    headers = ["ID", "STUDENT ID", "COURSE ID", "REGISTRATION DATE", "STATUS"]
    col_widths = [8, 20, 20, 25, 15]

    header_line = " | ".join(f"{h:<{col_widths[i]}}" for i, h in enumerate(headers))
    report += header_line + "\n"
    report += "-" * len(header_line) + "\n"

    for reg in records:
        try:
            date_str = reg['REGISTRATION DATE'].strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            date_str = "Invalid Date"
        
        row_data = [
            str(reg['ID']),
            reg['STUDENT ID'],
            reg['COURSE ID'],
            date_str,
            reg['STATUS']
        ]
        # ตัดข้อความหากยาวเกิน
        for i in range(len(row_data)):
            if len(row_data[i]) > col_widths[i]:
                row_data[i] = row_data[i][:col_widths[i]-3] + "..."
        row_line = " | ".join(f"{row_data[i]:<{col_widths[i]}}" for i in range(len(headers)))
        report += row_line + "\n"

    report += "--------------------------------------------------------------------------\n"
    print(report)

def add_registration():
    """เพิ่มข้อมูลการลงทะเบียนใหม่"""
    student = get_student_info_for_registration()
    if not student:
        return
    
    course_id = input("ป้อนรหัสวิชา: ").strip()
    if not course_id:
        print("รหัสวิชาว่าง กรุณาลองใหม่")
        return
    
    try:
        status = int(input("ป้อนสถานะ (1 = Registered, 0 = Dropped): "))
        if status not in (0, 1):
            raise ValueError
    except ValueError:
        print("❌ สถานะไม่ถูกต้อง กรุณาป้อนเป็นตัวเลข 0 หรือ 1")
        return
        
    register_id = get_next_register_id()
    registration_date = datetime.now().timestamp()
    
    record = create_registration_record(
        register_id,
        student['student_id'],
        course_id,
        registration_date,
        status
    )
    if record:
        write_record_to_file(record)
        print("✅ เพิ่มข้อมูลการลงทะเบียนสำเร็จ!")

def view_registrations():
    """แสดงข้อมูลการลงทะเบียนทั้งหมด"""
    registrations = read_all_records_from_file()
    if not registrations:
        print("ไม่พบข้อมูลการลงทะเบียนในระบบ")
        return
    print_registration_report(registrations, title="รายงานการลงทะเบียน")

def view_single_registration():
    """แสดงข้อมูลการลงทะเบียนรายการเดียวตามรหัส ID"""
    try:
        reg_id = int(input("ป้อนรหัส ID การลงทะเบียนที่ต้องการดู: "))
    except ValueError:
        print("รหัส ID ไม่ถูกต้อง กรุณาป้อนเป็นตัวเลข")
        return
    
    registrations = read_all_records_from_file()
    filtered_registrations = [r for r in registrations if r and r['ID'] == reg_id]
    
    if not filtered_registrations:
        print("ไม่พบรหัส ID การลงทะเบียนที่ต้องการดู")
        return
    
    print_registration_report(filtered_registrations, title="รายงานการลงทะเบียนรายการเดียว")

def view_filtered_registrations():
    """แสดงข้อมูลการลงทะเบียนที่กรองตามเงื่อนไข"""
    print("\n--- ตัวเลือกการกรอง ---")
    print("1. กรองตามรหัสนักเรียน")
    print("2. กรองตามรหัสวิชา")
    print("3. กรองตามสถานะ (Registered)")
    print("4. กลับไปเมนูหลัก")
    filter_choice = input("กรุณาเลือกการกรอง (1-4): ")
    
    registrations = read_all_records_from_file()
    if not registrations:
        print("ไม่พบข้อมูลการลงทะเบียนในระบบ")
        return
    
    filtered_registrations = []
    
    if filter_choice == '1':
        student_id = input("ป้อนรหัสนักเรียนที่ต้องการกรอง: ").strip()
        filtered_registrations = [r for r in registrations if r and r['STUDENT ID'] == student_id]
    
    elif filter_choice == '2':
        course_id = input("ป้อนรหัสวิชาที่ต้องการกรอง: ").strip()
        filtered_registrations = [r for r in registrations if r and r['COURSE ID'] == course_id]
    
    elif filter_choice == '3':
        filtered_registrations = [r for r in registrations if r and r['STATUS'] == 'Registered']
    
    elif filter_choice == '4':
        return
    
    else:
        print("ตัวเลือกไม่ถูกต้อง")
        return
    
    if not filtered_registrations:
        print("ไม่พบข้อมูลที่ตรงตามเงื่อนไขการกรอง")
        return
    
    print_registration_report(filtered_registrations, title=f"รายงานการลงทะเบียนที่กรอง ({len(filtered_registrations)} รายการ)")

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
        if reg and reg['ID'] == reg_id_to_update:
            found = True
            print("==========================================")
            print("    พบข้อมูลการลงทะเบียนที่ต้องการแก้ไข")
            print("==========================================")
            print(f"ID การลงทะเบียน: {reg['ID']}")
            print(f"รหัสนักเรียน: {reg['STUDENT ID']}")
            print(f"รหัสวิชา: {reg['COURSE ID']}")
            print(f"วันลงทะเบียน: {reg['REGISTRATION DATE'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"สถานะ: {reg['STATUS']}")
            print("==========================================")

            new_status = input("ป้อนสถานะใหม่ (1=Registered, 0=Dropped) (Enter เพื่อใช้ค่าเดิม): ")
            if new_status:
                try:
                    new_status = int(new_status)
                    if new_status not in [0, 1]:
                        raise ValueError
                    reg['STATUS'] = 'Registered' if new_status == 1 else 'Dropped'
                except ValueError:
                    print("สถานะไม่ถูกต้อง ใช้ค่าเดิม")
        
        if reg:
            updated_record = create_registration_record(
                reg['ID'],
                reg['STUDENT ID'],
                reg['COURSE ID'],
                reg['REGISTRATION DATE'].timestamp(),
                1 if reg['STATUS'] == 'Registered' else 0
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
        if reg and reg['ID'] == reg_id_to_delete:
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
                    reg['ID'],
                    reg['STUDENT ID'],
                    reg['COURSE ID'],
                    reg['REGISTRATION DATE'].timestamp(),
                    1 if reg['STATUS'] == 'Registered' else 0
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
        print("3. ดูข้อมูลการลงทะเบียนรายการเดียว")
        print("4. ดูข้อมูลการลงทะเบียนแบบกรอง")
        print("5. แก้ไขข้อมูลการลงทะเบียน")
        print("6. ลบข้อมูลการลงทะเบียน")
        print("0. กลับสู่เมนูหลัก")
        
        choice = input("กรุณาเลือกเมนู: ")
        
        if choice == '1':
            add_registration()
        elif choice == '2':
            view_registrations()
        elif choice == '3':
            view_single_registration()
        elif choice == '4':
            view_filtered_registrations()
        elif choice == '5':
            update_registration()
        elif choice == '6':
            delete_registration()
        elif choice == '0':
            print("ย้อนกลับสู่เมนูหลัก...")
            break
        else:
            print("ตัวเลือกไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง")

if __name__ == "__main__":
    registration_menu()