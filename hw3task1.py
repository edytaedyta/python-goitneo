from collections import UserDict, defaultdict
from datetime import datetime, timedelta
import pickle

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        if value:  
            self.value = value
        else:
            raise ValueError("Name field is required")

class Phone(Field):
    def __init__(self, value):
        if self.validate_phone(value):
            self.value = value
        else:
            raise ValueError("Invalid phone number: must be 10 digits")
    
    def validate_phone(self, phone):
        return len(str(phone)) == 10
    
class Birthday(Field):
    def __init__(self, value):
        if len(value) != 10 or not datetime.strptime(value, "%d.%m.%Y"):
            raise ValueError("Invalidd birthday format. DD.MM.YYYY required")
        super().__init__(value)

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None
    
    def remove_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                self.phones.remove(phone)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(str(p) for p in self.phones)} Birthdayy: {self.birthday.value}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record
    
    def find(self, name):
        return self.data.get(name)

    def remove_phone(self, name):
        if name in self.data:
            del self.data[name]
            print(f"Contact {name} deleted.")
        else:
            print("Contact not found.")

    def save_to_file(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(self.data, file)

    def get_birthdays_per_week(self):
        birthdays_per_week = defaultdict(list)
        today = datetime.today().date()
        monday_of_next_week = today + timedelta(days=(7 - today.weekday()))
        for name, record in self.data.items():
            if record.birthday:
                birthday = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                birthday_this_year = birthday.replace(year=today.year)
                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)
                delta_days = (birthday_this_year - today).days
                birthday_weekday = birthday_this_year.weekday()
                if birthday_weekday >= 5:
                    birthday_weekday = 0  
                if delta_days < 7 : 
                    birthday_weekday_name = (monday_of_next_week + timedelta(days=birthday_weekday)).strftime("%A")
                    birthdays_per_week[birthday_weekday_name].append(name)
                    
        if any(birthdays_per_week.values()):
            print("Birthdays in the next week:")
            for day, names in birthdays_per_week.items():
                if names:
                    print(f"{day}: {', '.join(names)}")
        else:
            print("No birthdays in the next week.")
                
            
def load_address_book_from_file(filename):
    try:
        with open(filename, 'rb') as file:
            data = pickle.load(file)
        address_book = AddressBook()
        address_book.data = data
        return address_book
    except (FileNotFoundError, EOFError):
        return AddressBook()

def parse_input(user_input):
    try:
        cmd, *args = user_input.split()
        cmd = cmd.strip().lower()
        return cmd, args
    except ValueError:
        return None, None
    



def main():
    Globalfilename = 'Myaddressbook.dat'
    book = load_address_book_from_file(Globalfilename)
    print("Welcome to the assistant bot!")
    
    ''' 
        Start assistant commands:
        comand lists: add, remove_phone, change_phone, phone, all, add_birthday, show_birthday, birthdays, hello, exit, close
    ''' 
    while True:
        user_input = input("Enter command: ").strip()
        command, args = parse_input(user_input)
        
        if command == "add":
            try:
                name, phone = args
                record = Record(name)
                record.add_phone(phone)
                book.add_record(record)
                print(f"Contact {name} added with phone number {phone}")

            except ValueError as e:
                print(e)
                print("Invalid command format. Use 'add [name] [phone]'")

        
        elif command == "remove_phone":
            try:
                name, phone = args
                record = book.find(name)
                if record:
                    phone_found = record.find_phone(phone)
                    if phone_found:
                        record.remove_phone(phone)
                        print(f"Phone number {phone} removed for contact {name}.")
                    else:
                        print(f"Phone number {phone} not found for contact {name}.")
                else:
                    print(f"Contact {name} not found.")

            except ValueError as e:
                print(e)
                print("Invalid command format. Use 'remove-phone [name] [phone]'")

        elif command == "change_phone":
            try:
                name, new_phone = args
                record = book.find(name)
                if record:
                    record.edit_phone(record.phones[0].value, new_phone)
                    print(f"Phone number changed for contact {name}")
                else:
                    print(f"Contact not found")
            except ValueError as e:
                print(e)
                print("Invalid command format. Use 'change [name] [new phone]'")

        elif command == "phone":
            try:
                name = args[0]
                record = book.find(name)
                if record:
                    print(f"Phone number for {name}: {record.phones[0]}")
                else:
                    print(f"Contact {name} not found.")
            except IndexError as e:
                print(e)
                print("Invalid command format. Use 'phone [name]'")

        elif command == "all":
            if book.data:
                print("All contacts:")
                for record in book.data.values():
                    print(record)
            else:
                print("No contacts in the address book.")

        elif command == "add_birthday":
            try:
                name, birthday = args
                record = book.find(name)
                if record:
                    record.add_birthday(birthday)
                    print(f"Birthday added for contact {name}")
                else:
                    print(f"Contact {name} not found")
                    
            except ValueError as e:
                print(e)
                print("Invalid command format. Use 'add-birthday [name] [birth date]'")

        elif command == "show_birthday":
            try:
                name = args[0]
                record = book.find(name)
                if record and record.birthday:
                    print(f"Birthday for {name}: {record.birthday}")
                elif record and not record.birthday:
                    print(f"No birthday set for {name}")
                else: 
                    print(f"Contact {name} not found.")
            except IndexError as e:
                print(e)
                print("Invalid command format. Use 'show-birthday [name]'")

        elif command == "birthdays":
            book.get_birthdays_per_week()

        elif command == "hello":
            print("How can I help you?")
        
        elif command in ["close", "exit"]:
            print("Goodbye!")
            book.save_to_file(Globalfilename)
            print("Saving address book and closing the app.")
            break

        else:
            print("Invalid command. Please try again")

if __name__ == "__main__":
    main()