import struct
import os
import time

REGISTER_FILE_NAME = 'RegisterCourse.bin'
REGISTER_RECORD_FORMAT = '<i 16s 16s d b'
REGISTER_RECORD_SIZE = struct.calcsize(REGISTER_RECORD_FORMAT)

current_dir = os.path.dirname(os.path.abspath(__file__))
main_dir = os.path.dirname(current_dir)
REGISTER_FILE_PATH = os.path.join(main_dir, REGISTER_FILE_NAME)

def create_register_record(register_id, student_id, course_id, registration_date, status):
    """สร้าง record ข้อมูลการลงทะเบียนเป็นไบต์"""
    packed_student_id = student_id.encode('utf-8')[:16].ljust(16, b'\x00')
    packed_course_id = course_id.encode('utf-8')[:16].ljust(16, b'\x00')
    
    try:
        record = struct.pack(
            REGISTER_RECORD_FORMAT,
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

def read_register_record(record_data):
    """อ่าน record ข้อมูลการลงทะเบียนจากไบต์"""
    try:
        unpacked_data = struct.unpack(REGISTER_RECORD_FORMAT, record_data)
        student_id = unpacked_data[1].strip(b'\x00').decode('utf-8')
        course_id = unpacked_data[2].strip(b'\x00').decode('utf-8')
        return {
            'register_id': unpacked_data[0],
            'student_id': student_id,
            'course_id': course_id,
            'registration_date': unpacked_data[3], # เก็บเป็น Timestamp
            'status': unpacked_data[4]
        }
    except struct.error as e:
        print(f"เกิดข้อผิดพลาดในการอันแพ็คข้อมูล: {e}")
        return None

def write_record_to_file(record, file_path=REGISTER_FILE_PATH):
    """เขียน record ลงในไฟล์ไบนารี"""
    with open(file_path, 'ab') as f:
        f.write(record)

def read_all_records_from_file(file_path=REGISTER_FILE_PATH):
    """อ่านข้อมูลทั้งหมดจากไฟล์ไบนารี"""
    records = []
    if not os.path.exists(file_path):
        return records
    with open(file_path, 'rb') as f:
        while True:
            record_data = f.read(REGISTER_RECORD_SIZE)
            if not record_data:
                break
            records.append(read_register_record(record_data))
    return records

def add_register():
    """เพิ่มข้อมูลการลงทะเบียนใหม่พร้อมการตรวจสอบข้อมูล"""
    try:
        register_id = int(input("ป้อนรหัสการลงทะเบียน: "))
        student_id = input("ป้อนรหัสนักเรียน: ")
        course_id = input("ป้อนรหัสวิชา: ")
        status = int(input("ป้อนสถานะ (1=ลงทะเบียน, 0=ยกเลิก): "))
        
        if status not in [0, 1]:
            print("สถานะไม่ถูกต้อง กรุณาป้อน 1 หรือ 0 เท่านั้น")
            return

        registration_date = time.time()
        
        record = create_register_record(register_id, student_id, course_id, registration_date, status)
        if record:
            write_record_to_file(record)
            print("เพิ่มข้อมูลการลงทะเบียนสำเร็จ!")
    except ValueError:
        print("ป้อนข้อมูลไม่ถูกต้อง กรุณาตรวจสอบและลองอีกครั้ง")

def view_all_registers():
    """แสดงข้อมูลการลงทะเบียนทั้งหมด"""
    registers = read_all_records_from_file()
    if not registers:
        print("ไม่พบข้อมูลการลงทะเบียนในระบบ")
        return
    
    print("\n--- รายการลงทะเบียนทั้งหมด ---")
    for reg in registers:
        if reg: # เพิ่มการตรวจสอบเพื่อให้แน่ใจว่า record ไม่เป็น None
            print(f"ID: {reg['register_id']} | Student ID: {reg['student_id']} | Course ID: {reg['course_id']} | Date: {time.ctime(reg['registration_date'])} | Status: {'ลงทะเบียนแล้ว' if reg['status'] == 1 else 'ยกเลิก'}")
    print("---------------------------------")

def update_register():
    """แก้ไขข้อมูลการลงทะเบียน"""
    try:
        register_id_to_update = int(input("ป้อนรหัสการลงทะเบียนที่ต้องการแก้ไข: "))
        registers = read_all_records_from_file()
        found = False
        new_records = []

        for reg in registers:
            if reg and reg['register_id'] == register_id_to_update:
                found = True
                print("==========================================")
                print("      พบข้อมูลการลงทะเบียนที่ต้องการแก้ไข")
                print("==========================================")
                print(f"รหัสลงทะเบียน: {reg['register_id']}")
                print(f"รหัสนักเรียน: {reg['student_id']}")
                print(f"รหัสวิชา: {reg['course_id']}")
                print(f"สถานะ: {'ลงทะเบียนแล้ว' if reg['status'] == 1 else 'ยกเลิก'}")
                print("==========================================")
                
                new_status = input("ป้อนสถานะใหม่ (1=ลงทะเบียน, 0=ยกเลิก) (Enter เพื่อใช้ค่าเดิม): ")
                if new_status:
                    try:
                        new_status_int = int(new_status)
                        if new_status_int in [0, 1]:
                            reg['status'] = new_status_int
                        else:
                            print("สถานะไม่ถูกต้อง กรุณาป้อน 1 หรือ 0 เท่านั้น ใช้ค่าเดิม")
                    except ValueError:
                        print("สถานะไม่ถูกต้อง กรุณาป้อนเป็นตัวเลข ใช้ค่าเดิม")
                
                updated_record = create_register_record(
                    reg['register_id'],
                    reg['student_id'],
                    reg['course_id'],
                    reg['registration_date'],
                    reg['status']
                )
                if updated_record:
                    new_records.append(updated_record)
            elif reg:
                old_record = create_register_record(
                    reg['register_id'],
                    reg['student_id'],
                    reg['course_id'],
                    reg['registration_date'],
                    reg['status']
                )
                if old_record:
                    new_records.append(old_record)

        if found:
            with open(REGISTER_FILE_PATH, 'wb') as f:
                for record in new_records:
                    f.write(record)
            print("แก้ไขข้อมูลการลงทะเบียนสำเร็จ!")
        else:
            print("ไม่พบรหัสการลงทะเบียนที่ต้องการแก้ไข")
    except ValueError:
        print("ป้อนข้อมูลรหัสการลงทะเบียนไม่ถูกต้อง กรุณาป้อนเป็นตัวเลข")

def delete_register():
    """ลบข้อมูลการลงทะเบียนแบบถาวร"""
    try:
        register_id_to_delete = int(input("ป้อนรหัสการลงทะเบียนที่ต้องการลบ: "))
        registers = read_all_records_from_file()
        found = False
        
        remaining_records = []
        
        for reg in registers:
            if reg and reg['register_id'] == register_id_to_delete:
                found = True
            elif reg:
                remaining_records.append(reg)
        
        if found:
            with open(REGISTER_FILE_PATH, 'wb') as f:
                for reg in remaining_records:
                    record = create_register_record(
                        reg['register_id'],
                        reg['student_id'],
                        reg['course_id'],
                        reg['registration_date'],
                        reg['status']
                    )
                    if record:
                        f.write(record)
            print("ลบข้อมูลการลงทะเบียนสำเร็จ!")
        else:
            print("ไม่พบรหัสการลงทะเบียนที่ต้องการลบ")
    except ValueError:
        print("ป้อนข้อมูลรหัสการลงทะเบียนไม่ถูกต้อง กรุณาป้อนเป็นตัวเลข")

def main_menu():
    """แสดงเมนูหลักและรับตัวเลือกจากผู้ใช้"""
    while True:
        print("\n--- เมนูจัดการข้อมูลการลงทะเบียน ---")
        print("1. เพิ่มข้อมูลการลงทะเบียน")
        print("2. ดูข้อมูลการลงทะเบียนทั้งหมด")
        print("3. แก้ไขข้อมูลการลงทะเบียน")
        print("4. ลบข้อมูลการลงทะเบียน")
        print("5. ย้อนกลับไปหน้าแรก")
        choice = input("กรุณาเลือกเมนู (1-5): ")
            
        if choice == '1':
            add_register()
        elif choice == '2':
            view_all_registers()
        elif choice == '3':
            update_register()
        elif choice == '4':
            delete_register()
        elif choice == '5':
            print("ย้อนกลับสู่เมนูหลัก...")
            break
        else:
            print("ตัวเลือกไม่ถูกต้อง กรุณาลองอีกครั้ง")

if __name__ == "__main__":
    main_menu()