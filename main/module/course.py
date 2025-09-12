import def_CRUD_course
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
                def_CRUD_course.add_course()
            elif choice == '2':
                def_CRUD_course.view_courses()
            elif choice == '3':
                def_CRUD_course.update_course()
            elif choice == '4':
                def_CRUD_course.delete_course()
            elif choice == '5':
                print("ย้อนกลับสู่เมนูหลัก...")
                break
            else:
                print("ตัวเลือกไม่ถูกต้อง กรุณาลองอีกครั้ง")
if __name__ == "__main__":
    main_menu()
