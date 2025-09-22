import struct
import os
import random
from datetime import datetime, timedelta

REGISTRATION_FILE_NAME = 'registration.bin'
REGISTRATION_RECORD_FORMAT = '<I16s16sdB'
REGISTRATION_RECORD_SIZE = struct.calcsize(REGISTRATION_RECORD_FORMAT)
COURSE_FILE_NAME = 'CourseSubject.bin'
COURSE_RECORD_FORMAT = '<10s50sB H B B'
COURSE_RECORD_SIZE = struct.calcsize(COURSE_RECORD_FORMAT)

current_dir = os.path.dirname(os.path.abspath(__file__))
main_dir = os.path.dirname(current_dir)
REGISTRATION_FILE_PATH = os.path.join(main_dir, REGISTRATION_FILE_NAME)
COURSE_FILE_PATH = os.path.join(main_dir, COURSE_FILE_NAME)

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

def write_record_to_file(record, file_path=REGISTRATION_FILE_PATH):
    """เขียนบันทึกข้อมูลลงในไฟล์ไบนารี"""
    try:
        with open(file_path, 'ab') as f:
            f.write(record)
    except IOError as e:
        print(f"เกิดข้อผิดพลาดในการเขียนไฟล์: {e}")

def read_course_ids():
    """อ่านรหัสวิชาทั้งหมดจากไฟล์ CourseSubject.bin"""
    course_ids = []
    try:
        if not os.path.exists(COURSE_FILE_PATH):
            print("ไม่พบไฟล์ CourseSubject.bin")
            return course_ids
        with open(COURSE_FILE_PATH, 'rb') as f:
            while True:
                record_data = f.read(COURSE_RECORD_SIZE)
                if not record_data:
                    break
                try:
                    unpacked_data = struct.unpack(COURSE_RECORD_FORMAT, record_data)
                    course_id = unpacked_data[0].strip(b'\x00').decode('utf-8')
                    course_ids.append(course_id)
                except (struct.error, UnicodeDecodeError) as e:
                    print(f"ข้อผิดพลาดในการอ่าน course record: {e}")
                    continue
    except IOError as e:
        print(f"เกิดข้อผิดพลาดในการอ่านไฟล์ CourseSubject.bin: {e}")
    return course_ids

def generate_sample_data():
    """สร้างข้อมูลตัวอย่างการลงทะเบียน 60 รายการ (5 วิชา, วิชาละ 10-20 คน)"""
    student_ids = [
        'STU796973', 'STU705257', 'STU442194', 'STU569818', 'STU942291', 'STU778182',
        'STU837721', 'STU510451', 'STU911742', 'STU109544', 'STU471005', 'STU355431',
        'STU779447', 'STU669065', 'STU804899', 'STU945148', 'STU788477', 'STU636498',
        'STU989829', 'STU761706', 'STU535097', 'STU204097', 'STU625594', 'STU482699',
        'STU197090', 'STU767621', 'STU771368', 'STU468016', 'STU546039', 'STU339972',
        'STU971475', 'STU337436', 'STU840301', 'STU153914', 'STU625746', 'STU204521',
        'STU472020', 'STU780745', 'STU265238', 'STU155168', 'STU892150', 'STU402507',
        'STU820212', 'STU162343', 'STU411021', 'STU116871', 'STU586679', 'STU242278',
        'STU157653', 'STU345896', 'STU637546', 'STU154528', 'STU162787', 'STU663268',
        'STU898946', 'STU453644', 'STU818977', 'STU794109', 'STU895593', 'STU709304'
    ]
    course_ids = read_course_ids()
    if len(course_ids) < 5:
        print(f"พบรหัสวิชาเพียง {len(course_ids)} รายการ ต้องการอย่างน้อย 5 วิชา ไม่สามารถสร้างข้อมูลได้")
        return

    statuses = [0, 1]  # 0=Dropped, 1=Registered

    # ลบไฟล์เก่าถ้ามี
    if os.path.exists(REGISTRATION_FILE_PATH):
        os.remove(REGISTRATION_FILE_PATH)

    # เลือก 5 วิชาแบบสุ่ม
    selected_courses = random.sample(course_ids, 5)
    registrations = []
    register_id = 1

    # สร้างการลงทะเบียนสำหรับแต่ละวิชา
    for course_id in selected_courses:
        # สุ่มจำนวนนักเรียนต่อวิชา (10-20 คน)
        num_students = random.randint(10, 20)
        # สุ่มนักเรียนโดยไม่ให้ซ้ำในวิชานี้
        selected_students = random.sample(student_ids, min(num_students, len(student_ids)))
        
        for student_id in selected_students:
            # สุ่มวันที่ในช่วง 1 ปีที่ผ่านมา (2567-2568)
            start_date = datetime(2024, 9, 22).timestamp()
            end_date = datetime(2025, 9, 22).timestamp()
            registration_date = start_date + (end_date - start_date) * random.random()
            status = random.choice(statuses)

            record = create_registration_record(
                register_id,
                student_id,
                course_id,
                registration_date,
                status
            )
            if record:
                registrations.append((register_id, student_id, course_id))
                write_record_to_file(record)
                register_id += 1

    # หากจำนวนรายการน้อยกว่า 60, เติมรายการเพิ่มโดยสุ่มจากวิชาที่เลือก
    while len(registrations) < 60:
        course_id = random.choice(selected_courses)
        # สุ่มนักเรียนโดยหลีกเลี่ยงการลงทะเบียนซ้ำ
        available_students = [sid for sid in student_ids if not any(r[1] == sid and r[2] == course_id for r in registrations)]
        if not available_students:
            break  # หากไม่มีนักเรียนที่ยังไม่ได้ลงวิชานี้
        student_id = random.choice(available_students)
        
        start_date = datetime(2024, 9, 22).timestamp()
        end_date = datetime(2025, 9, 22).timestamp()
        registration_date = start_date + (end_date - start_date) * random.random()
        status = random.choice(statuses)

        record = create_registration_record(
            register_id,
            student_id,
            course_id,
            registration_date,
            status
        )
        if record:
            registrations.append((register_id, student_id, course_id))
            write_record_to_file(record)
            print(f"เพิ่มข้อมูลการลงทะเบียนที่ {register_id}: ID={register_id}, Student={student_id}, Course={course_id}")
            register_id += 1

    # แสดงผลการลงทะเบียนทั้งหมด
    for i, (rid, sid, cid) in enumerate(registrations, 1):
        print(f"เพิ่มข้อมูลการลงทะเบียนที่ {i}: ID={rid}, Student={sid}, Course={cid}")

if __name__ == "__main__":
    print("กำลังสร้างข้อมูลตัวอย่างการลงทะเบียน 60 รายการ (5 วิชา, วิชาละ 10-20 คน)...")
    generate_sample_data()
    print("สร้างข้อมูลตัวอย่างสำเร็จ!")