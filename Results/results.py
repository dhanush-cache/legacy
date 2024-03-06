from pathlib import Path
import PyPDF2
from tabulate import tabulate
import re
from tabulate import tabulate


class Results:
    def __init__(self, pdf_file=Path("results.pdf")):
        self.__results = {}
        self.__pdf_file = pdf_file
        self.__get_text()
        self.__patterns()
        self.__format_text()

    def __get_text(self):
        __txt_file = Path(".results.txt")
        if __txt_file.exists():
            self.__text = __txt_file.read_text()
        else:
            with open(self.__pdf_file, 'rb') as file:
                self.__text = ""
                pdf_reader = PyPDF2.PdfReader(file)
                for page_no in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_no]
                    self.__text += page.extract_text()
                __txt_file.write_text(self.__text)

    def __patterns(self):
        self.__find_roll_no = r'[A-Z]{1,3}-[0-9]{4}'
        self.__find_std_end = r'SGPI.*$'
        self.__find_name = r'[A-Z][a-z]*'
        self.__rem_line = r'.*$'
        self.__rem_sub_name = r'[ A-Za-z\-]*'
        self.__rem_sub_id = r'^\(.*\)'
        self.__find_marks = r'[0-9]{1,2}'

    def __extract_info(self, pattern):
        match = re.search(pattern, self.__std_data, re.MULTILINE)
        if match:
            info = self.__std_data[match.span()[0]:match.span()[1]]
            self.__std_data = self.__std_data[match.span()[1]:].strip()
            return info

    def __sub_change(self):
        self.__extract_info(self.__rem_line)
        self.__sub_name = self.__extract_info(self.__rem_sub_name)
        self.__extract_info(self.__rem_sub_id)
        self.__extract_info(self.__find_marks)

    def __format_text(self):
        while True:
            start = re.search(self.__find_roll_no, self.__text, re.MULTILINE)
            end = re.search(self.__find_std_end, self.__text, re.MULTILINE)

            if not start:
                break

            start_index = start.span()[0]
            end_index = end.span()[1] if end != None else -1

            self.__std_data = self.__text[start_index:end_index].strip()
            self.__text = self.__text[end_index:].strip()

            roll_no = self.__extract_info(self.__find_roll_no)
            lname = self.__extract_info(self.__find_name)
            name = self.__extract_info(self.__find_name)
            fname = self.__extract_info(self.__find_name)
            mname = self.__extract_info(self.__find_name)
            self.__sub_change()

            internals = []
            theory = []
            practicals = []
            while "Practical" not in self.__sub_name:
                internals.append(self.__extract_info(self.__find_marks))
                theory.append(self.__extract_info(self.__find_marks))
                self.__sub_change()

            while "Practical" in self.__sub_name:
                practicals.append(self.__extract_info(self.__find_marks))
                self.__sub_change()

            total = 0
            for mark in internals + theory + practicals:
                total += int(mark)

            for i in range(len(internals)):
                if int(internals[i]) < 10:
                    internals[i] = f"\x1b[1;31m{internals[i]}\x1b[0m"
                else:
                    internals[i] = f"\x1b[1;32m{internals[i]}\x1b[0m"

            for i in range(len(theory)):
                if int(theory[i]) < 30:
                    theory[i] = f"\x1b[1;31m{theory[i]}\x1b[0m"
                else:
                    theory[i] = f"\x1b[1;32m{theory[i]}\x1b[0m"

            for i in range(len(practicals)):
                if int(practicals[i]) < 20:
                    practicals[i] = f"\x1b[1;31m{practicals[i]}\x1b[0m"
                else:
                    practicals[i] = f"\x1b[1;32m{practicals[i]}\x1b[0m"

            self.__results[int(roll_no[-4:])] = {"roll no": roll_no}
            self.__results[int(roll_no[-4:])]["name"] = f"{name} {lname}"
            self.__results[int(roll_no[-4:])]["subjects"] = {
                "DSA": {"theory": theory[0], "internals": internals[0], "practicals": practicals[0]},
                "Python": {"theory": theory[1], "internals": internals[1], "practicals": practicals[1]},
                "Linux": {"theory": theory[2], "internals": internals[2], "practicals": practicals[2]},
                "OST": {"theory": theory[3], "internals": internals[3], "practicals": practicals[3]},
                "DM": {"theory": theory[4], "internals": internals[4], "practicals": practicals[4]},
                "DS": {"theory": theory[5], "internals": internals[5], "practicals": practicals[5]},
                "SS": {"theory": theory[6], "internals": internals[6], "practicals": None},
            }
            self.__results[int(roll_no[-4:])]["total"] = total

    def std_result(self, roll_no):
        roll_no = int(roll_no[-4:])
        print(f"Name: {self.__results[roll_no]['name']}")
        rows = [[subject,
                 self.__results[roll_no]["subjects"][subject]["internals"],
                 self.__results[roll_no]["subjects"][subject]["theory"],
                 self.__results[roll_no]["subjects"][subject]["practicals"]]
                for subject in self.__results[roll_no]["subjects"]]
        table = tabulate(
            rows, headers=["Subject", "Internal", "Theory", "Practical"], tablefmt="grid")
        print(table)
        print(f"Total: {self.__results[roll_no]['total']}")

    def rank(self):
        self.__sorted_results = sorted(
            self.__results.items(), key=lambda std: std[1]["total"], reverse=True)
        rows = [[str(index).zfill(3), student[1]["roll no"], student[1]["name"], student[1]["total"]]
                for index, student in enumerate(self.__sorted_results, start=1)]
        table = tabulate(
            rows, headers=["Rank", "Roll no", "Name", "Total Marks"], tablefmt="grid")
        print(table)
