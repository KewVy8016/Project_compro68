import struct
import os
from module.student import *
from module.register import *

def course_menu():
    """เมนูย่อยสำหรับจัดการข้อมูลรายวิชา (CRUD)"""
    while True:
        print("\n===== ระบบจัดการข้อมูลรายวิชา =====")
        print("1. เพิ่มรายวิชา")
        print("2. ดูรายวิชาทั้งหมด")
        print("3. แก้ไขรายวิชา")
        print("4. ลบรายวิชา")
        print("0. กลับสู่เมนูหลัก")
        
        choice = input("กรุณาเลือกเมนู: ")
        
        if choice == '1':
            def_CRUD_course.add_course()
            print(">>> เรียกฟังก์ชัน 'เพิ่มรายวิชา' <<<")
        elif choice == '2':
            def_CRUD_course.view_courses()
            print(">>> เรียกฟังก์ชัน 'ดูรายวิชาทั้งหมด' <<<")
        elif choice == '3':
            def_CRUD_course.update_course()
            print(">>> เรียกฟังก์ชัน 'แก้ไขรายวิชา' <<<")
        elif choice == '4':
            def_CRUD_course.delete_course()
            print(">>> เรียกฟังก์ชัน 'ลบรายวิชา' <<<")
        elif choice == '0':
            print("ย้อนกลับสู่เมนูหลัก...")
            break
        else:
            print("ตัวเลือกไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง")






def main_menu():
    """เมนูหลักของโปรแกรม"""
    while True:
        print("\n===== ระบ1บจัดการข้อมูลลงทะเบียนเรียน =====")
        print("1. จัดการข้อมูลนักเรียน")
        print("2. จัดการข้อมูลรายวิชา")
        print("3. จัดการข้อมูลการลงทะเบียน")
        print("4. สร้างไฟล์รายงาน")
        print("0. ออกจากโปรแกรม")

        choice = input("กรุณาเลือกเมนูหลัก: ")

        if choice == '1':
            student_menu()
        elif choice == '2':
            course_menu()
        elif choice == '3':
            registration_menu()
        elif choice == '4':
            # generate_report()
            print(">>> เรียกฟังก์ชัน 'สร้างไฟล์รายงาน' <<<")
        elif choice == '0':
            print("ออกจากโปรแกรม...")
            break
        else:
            print("ตัวเลือกไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง")

if __name__ == "__main__":
    main_menu()