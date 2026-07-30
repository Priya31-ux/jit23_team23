from speech import speak

while True:
    print("\n===== SightSense =====")
    print("1. Describe Surroundings")
    print("2. Read Text")
    print("3. Object Detection")
    print("4. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        print("Launching Scene Description...")
        exec(open("live_gemini.py").read())

    elif choice == "2":
        print("Launching OCR...")
        exec(open("test_ocr.py").read())

    elif choice == "3":
        print("Launching YOLO Detection...")
        exec(open("yolo_detect.py").read())

    elif choice == "4":
        speak("Goodbye.")
        break

    else:
        print("Invalid choice.")