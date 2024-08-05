from collections import UserDict
from datetime import datetime, timedelta
import pickle


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        super().__init__(value)
        if not value.isalpha():
            raise ValueError("Name must contain only letters")


class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must contain 10 digits")


class Birthday(Field):
    def __init__(self, value):
        super().__init__(value)
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def find_phone(self, phone):
        for ph in self.phones:
            if ph.value == phone:
                return ph

    def remove_phone(self, phone):
        phone_remove = self.find_phone(phone)
        if phone_remove:
            self.phones.remove(phone_remove)
        else:
            raise ValueError("Phone number is not found")

    def edit_phone(self, old_phone_number, new_phone_number):
        phone_edit = self.find_phone(old_phone_number)
        if phone_edit:
            self.remove_phone(old_phone_number)
            self.add_phone(new_phone_number)
        else:
            raise ValueError("Phone number is not found")

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = "; ".join(p.value for p in self.phones)
        birthday = self.birthday.value.strftime("%d.%m.%Y") if self.birthday else "Not available"
        return f"Contact name: {self.name.value}, phones: {phones}, birthday: {birthday}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find_record(self, name):
        return self.data.get(name, None)

    def delete_record(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise KeyError("Contact not found")

    def get_upcoming_birthdays(self):
        today = datetime.now().date()
        upcoming_birthdays = []
        for record in self.data.values():
            if record.birthday:
                bday_this_year = record.birthday.value.replace(year=today.year)
                if 0 <= (bday_this_year - today).days <= 7:
                    if bday_this_year.weekday() >= 5:
                        bday_this_year += timedelta(days=(7 - bday_this_year.weekday()))
                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "birthday": bday_this_year.strftime("%d.%m.%Y")
                    })
        return upcoming_birthdays

    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as ve:
            return str(ve)
        except KeyError:
            return "Contact is not found"
        except IndexError:
            return "Enter user name and phone/birthday"

    return inner


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find_record(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args
    record = book.find_record(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Contact updated."
    else:
        return "Contact is not found"


@input_error
def phone_contact(args, book: AddressBook):
    name = args[0]
    record = book.find_record(name)
    if record:
        return f"Contact {name}: {'; '.join(p.value for p in record.phones)}"
    else:
        return "Contact is not found"


@input_error
def show_all_contacts(book: AddressBook):
    if book.data:
        return str(book)
    else:
        return "Phonebook is empty"


@input_error
def add_birthday(args, book: AddressBook):
    name, birthday, *_ = args
    record = book.find_record(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added."
    else:
        return "Contact is not found"


@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find_record(name)
    if record:
        return f"Contact {name}: Birthday is {record.birthday.value.strftime('%d.%m.%Y') if record.birthday else
        'not set'}"
    else:
        return "Contact is not found"


@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if upcoming:
        return "\n".join([f"{record['name']}: {record['birthday']}" for record in upcoming])
    else:
        return "No upcoming birthdays in the next 7 days."


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(phone_contact(args, book))

        elif command == "all":
            print(show_all_contacts(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command")


if __name__ == "__main__":
    main()
