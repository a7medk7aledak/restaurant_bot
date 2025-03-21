from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import datetime
import sqlite3
import sys
import os

# إضافة مسار المشروع للوصول إلى ملف database.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import check_availability, make_reservation

class ActionCheckAvailability(Action):
    def name(self) -> Text:
        return "action_check_availability"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        guests_number = tracker.get_slot("guests_number")
        reservation_date = tracker.get_slot("reservation_date")
        reservation_time = tracker.get_slot("reservation_time")
        
        # تحويل قيم النصوص إلى قيم مناسبة
        try:
            guests_number = int(guests_number)
        except (ValueError, TypeError):
            # تخمين عدد الضيوف إذا كان النص غير واضح
            if guests_number in ["شخصين", "اثنين", "شخصان"]:
                guests_number = 2
            elif guests_number in ["ثلاثة", "ثلاث"]:
                guests_number = 3
            elif guests_number in ["أربعة", "أربع"]:
                guests_number = 4
            elif guests_number in ["خمسة", "خمس"]:
                guests_number = 5
            else:
                guests_number = 2  # قيمة افتراضية

        # تحويل التاريخ إلى تنسيق مناسب
        if reservation_date == "اليوم":
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        elif reservation_date == "غدا":
            tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
            date = tomorrow.strftime("%Y-%m-%d")
        else:
            date = reservation_date
        
        # تحويل الوقت إلى تنسيق مناسب
        if "مساء" in str(reservation_time) or "ليلا" in str(reservation_time):
            try:
                hour = int(reservation_time.split()[0])
                time = f"{hour}:00 PM"
            except:
                time = "8:00 PM"  # قيمة افتراضية
        elif "صباحا" in str(reservation_time) or "صباح" in str(reservation_time):
            try:
                hour = int(reservation_time.split()[0])
                time = f"{hour}:00 AM"
            except:
                time = "8:00 AM"  # قيمة افتراضية
        else:
            time = reservation_time
            
        # التحقق من قاعدة البيانات
        available_table = check_availability(guests_number, date, time)
        
        # إعداد قيمة لإظهار التوفر
        has_availability = bool(available_table)
        
        return [
            SlotSet("available_table", float(available_table) if available_table else 0.0),
            SlotSet("has_availability", has_availability),
            SlotSet("reservation_date", date),
            SlotSet("reservation_time", time),
            SlotSet("guests_number", guests_number)
        ]
class ActionCreateReservation(Action):
    def name(self) -> Text:
        return "action_create_reservation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        table_id = int(tracker.get_slot("available_table")) if tracker.get_slot("available_table") else None
        customer_name = tracker.get_slot("customer_name")
        guests_number = tracker.get_slot("guests_number")
        date = tracker.get_slot("reservation_date")
        time = tracker.get_slot("reservation_time")
        
        print(f"[DEBUG] Slots Received: table_id={table_id}, name={customer_name}, guests={guests_number}, date={date}, time={time}")

        if not table_id:
            dispatcher.utter_message(text="عذراً، لا توجد طاولات متاحة بهذه المواصفات.")
            return [SlotSet("reservation_id", 0.0)]
            
        # إنشاء الحجز في قاعدة البيانات
        reservation_id = make_reservation(table_id, customer_name, guests_number, date, time)
        
        if reservation_id:
            print(f"[LOG] تم حجز الطاولة بنجاح! رقم الحجز: {reservation_id}")
        else:
            print("[ERROR] لم يتم إنشاء الحجز بشكل صحيح!")

        dispatcher.utter_message(text=f"تم تأكيد حجزك بنجاح! رقم الحجز الخاص بك هو {reservation_id}. نتطلع لاستقبالك.")

        return [SlotSet("reservation_id", float(reservation_id))]
