import struct
import os
from module.student import *
from module.register import *







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