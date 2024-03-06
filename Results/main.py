from results import Results

message = """1. See all rankings.
2. Check student score.
Select an option: """

choice = input(message)
results = Results()
if choice == "1":
    results.rank()
elif choice == "2":
    roll_no = input("Enter Student Roll No: ")
    results.std_result(roll_no)
else:
    print("Invalid option!!!")
