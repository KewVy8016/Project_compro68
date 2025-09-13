import struct
import os

COURSE_FILE_NAME = 'CourseSubject.bin'
COURSE_RECORD_FORMAT = '<10s50sB H B B'
COURSE_RECORD_SIZE = struct.calcsize(COURSE_RECORD_FORMAT)

current_dir = os.path.dirname(os.path.abspath(__file__))
main_dir = os.path.dirname(current_dir)
COURSE_FILE_PATH = os.path.join(main_dir, COURSE_FILE_NAME)

def create_course_record(course_id, course_name, credit, academic_year, semester, is_active):
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
    except struct.error as e:
        print(f"เกิดข้อผิดพลาดในการอันแพ็คข้อมูล: {e}")
        return None

def write_record_to_file(record, file_path=COURSE_FILE_PATH):
    with open(file_path, 'ab') as f:
        f.write(record)

def read_all_records_from_file(file_path=COURSE_FILE_PATH):
    records = []
    if not os.path.exists(file_path):
        return records
    with open(file_path, 'rb') as f:
        while True:
            record_data = f.read(COURSE_RECORD_SIZE)
            if not record_data:
                break
            records.append(read_course_record(record_data))
    return records
   
# --- ฟังก์ชัน CRUD หลักที่ใช้ในเมนู ---

def add_course():
    """เพิ่มข้อมูลรายวิชาใหม่"""
    course_id = input("ป้อนรหัสวิชา (ไม่เกิน 10 ตัวอักษร): ")
    course_name = input("ป้อนชื่อวิชา (ไม่เกิน 50 ตัวอักษร): ")
    credit = int(input("ป้อนหน่วยกิต: "))
    academic_year = int(input("ป้อนปีการศึกษา (เช่น 2568): "))
    semester = int(input("ป้อนภาคเรียน (1, 2, 3): "))
    is_active = int(input("สถานะการของวิชา(1 = เปิดสอน 0 = ยกเลิก):"))

    record = create_course_record(course_id, course_name, credit, academic_year, semester, is_active)
    if record:
        write_record_to_file(record)
        print("เพิ่มข้อมูลรายวิชาสำเร็จ!")

def view_courses():
    """แสดงข้อมูลรายวิชาทั้งหมด"""
    courses = read_all_records_from_file()
    if not courses:
        print("ไม่พบข้อมูลรายวิชาในระบบ")
        return
    print("\n--- รายการวิชาทั้งหมด ---")
    for course in courses:
        print(f"รหัส: {course['course_id']:<10} | ชื่อ: {course['course_name']:<50} | หน่วยกิต: {course['credit']:<2} | ปีการศึกษา: {course['academic_year']} | ภาคเรียน: {course['semester']} | สถานะ: {'เปิดสอน' if course['is_active'] == 1 else 'ยกเลิก'}")
    print("-------------------------")

def update_course():
    """แก้ไขข้อมูลรายวิชา"""
    course_id_to_update = input("ป้อนรหัสวิชาที่ต้องการแก้ไข: ")
    courses = read_all_records_from_file()
    found = False
    new_records = []

    for course in courses:
        if course['course_id'] == course_id_to_update:
            found = True
            print("==========================================")
            print("      พบข้อมูลวิชาที่ต้องการแก้ไข")
            print("==========================================")
            print(f"รหัสวิชา: {course['course_id']}")
            print(f"ชื่อวิชา: {course['course_name']}")
            print(f"หน่วยกิต: {course['credit']}")
            print(f"ปีการศึกษา: {course['academic_year']}")
            print(f"ภาคเรียน: {course['semester']}")
            print(f"สถานะ: {'เปิดสอน' if course['is_active'] == 1 else 'ยกเลิก'}")
            print("==========================================")
                        
            new_name = input("ป้อนชื่อวิชาใหม่ (Enter เพื่อใช้ค่าเดิม): ")
            if new_name:
                course['course_name'] = new_name
            
            new_credit = input("ป้อนหน่วยกิตใหม่ (Enter เพื่อใช้ค่าเดิม): ")
            if new_credit:
                try:
                    course['credit'] = int(new_credit)
                except ValueError:
                    print("หน่วยกิตไม่ถูกต้อง กรุณาป้อนเป็นตัวเลข ใช้ค่าเดิม")

            new_academic_year = input("ป้อนปีการศึกษาใหม่ (Enter เพื่อใช้ค่าเดิม): ")
            if new_academic_year:
                try:
                    course['academic_year'] = int(new_academic_year)
                except ValueError:
                    print("ปีการศึกษาไม่ถูกต้อง กรุณาป้อนเป็นตัวเลข ใช้ค่าเดิม")

            new_semester = input("ป้อนภาคเรียนใหม่ (Enter เพื่อใช้ค่าเดิม): ")
            if new_semester:
                try:
                    course['semester'] = int(new_semester)
                except ValueError:
                    print("ภาคเรียนไม่ถูกต้อง กรุณาป้อนเป็นตัวเลข ใช้ค่าเดิม")

            new_active = input("สถานะการของวิชา(1 = เปิดสอน 0 = ยกเลิก) (Enter เพื่อใช้ค่าเดิม): ")
            if new_active:
                try:
                    new_active_int = int(new_active)
                    if new_active_int in [0, 1]:
                        course['is_active'] = new_active_int
                    else:
                        print("สถานะไม่ถูกต้อง กรุณาป้อน 1 หรือ 0 เท่านั้น ใช้ค่าเดิม")
                except ValueError:
                    print("สถานะไม่ถูกต้อง กรุณาป้อนเป็นตัวเลข ใช้ค่าเดิม")

            updated_record = create_course_record(
                course['course_id'], 
                course['course_name'], 
                course['credit'], 
                course['academic_year'], 
                course['semester'], 
                course['is_active']
            )
            new_records.append(updated_record)
        else:
            old_record = create_course_record(
                course['course_id'], 
                course['course_name'], 
                course['credit'], 
                course['academic_year'], 
                course['semester'], 
                course['is_active']
            )
            new_records.append(old_record)
            
    if found:
        with open(COURSE_FILE_PATH, 'wb') as f:
            for record in new_records:
                f.write(record)
        print("แก้ไขข้อมูลสำเร็จ!")
    else:
        print("ไม่พบรหัสวิชาที่ต้องการแก้ไข")

def delete_course():
    """ลบข้อมูลรายวิชาแบบถาวร"""
    course_id_to_delete = input("ป้อนรหัสวิชาที่ต้องการลบถาวร: ")
    courses = read_all_records_from_file()
    found = False
    
    remaining_records = []
    
    for course in courses:
        if course['course_id'] == course_id_to_delete:
            found = True
            print("ลบข้อมูลรายวิชาสำเร็จ!")
        else:
            remaining_records.append(course)

    if found:
        with open(COURSE_FILE_PATH, 'wb') as f:
            for course in remaining_records:
                record = create_course_record(
                    course['course_id'], 
                    course['course_name'], 
                    course['credit'], 
                    course['academic_year'], 
                    course['semester'], 
                    course['is_active']
                )
                f.write(record)
    else:
        print("ไม่พบรหัสวิชาที่ต้องการลบ")

def main_menu():
    """แสดงเมนูหลักและรับตัวเลือกจากผู้ใช้"""
    while True:
            print("\n--- เมนูจัดการรายวิชา ---")
            print("1. เพิ่มข้อมูลรายวิชา")
            print("2. ดูข้อมูลรายวิชาทั้งหมด")
            print("3. แก้ไขข้อมูลรายวิชา")
            print("4. ลบรายวิชา")
            print("5. ย้อนกลับไปหน้าแรก")
            choice = input("กรุณาเลือกเมนู (1-5): ")
                
            if choice == '1':
                add_course()
            elif choice == '2':
                view_courses()
            elif choice == '3':
                update_course()
            elif choice == '4':
                delete_course()
            elif choice == '5':
                print("ย้อนกลับสู่เมนูหลัก...")
                break
            else:
                print("ตัวเลือกไม่ถูกต้อง กรุณาลองอีกครั้ง")
if __name__ == "__main__":
    main_menu()
