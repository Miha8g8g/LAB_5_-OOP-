from abc import ABC, abstractmethod
import json
import csv

# ===== ІНТЕРФЕЙСИ =====
class IEmployee(ABC):
    @abstractmethod
    def calculate_salary(self, month: str) -> float:
        pass

class IPaymentScheme(ABC):
    @abstractmethod
    def calculate(self, base: float, bonus: float, plan: float, actual: float) -> float:
        pass

class IDataLoader(ABC):
    @abstractmethod
    def load(self, filepath: str):
        pass

class IDataSaver(ABC):
    @abstractmethod
    def save(self, filepath: str, data):
        pass

# ===== КЛАСИ СХЕМ НАРАХУВАННЯ =====
class FixedSalaryWithBonus(IPaymentScheme):
    def calculate(self, base, bonus, plan, actual):
        return base + bonus

class PercentProductionWithBonus(IPaymentScheme):
    def calculate(self, base, bonus, plan, actual):
        return actual * base + bonus

class PercentPlanWithBonus(IPaymentScheme):
    def calculate(self, base, bonus, plan, actual):
        if plan == 0:
            return bonus
        return (actual / plan) * base + bonus

# ===== ПРАЦІВНИКИ =====
class Employee(IEmployee):
    def __init__(self, name, position, department, payment_scheme: IPaymentScheme, base_salary, bonus):
        self.name = name
        self.position = position
        self.department = department
        self.payment_scheme = payment_scheme
        self.base_salary = base_salary
        self.bonus = bonus
        self.production = {}  # month -> production

    def calculate_salary(self, month: str) -> float:
        actual = self.production.get(month, 0)
        plan = self.department.plan.get(month, 0)
        return self.payment_scheme.calculate(self.base_salary, self.bonus, plan, actual)

class Manager(Employee):
    pass

# ===== ПІДРОЗДІЛИ =====
class Department:
    def __init__(self, name, manager=None):
        self.name = name
        self.manager = manager
        self.employees = []
        self.plan = {}  # month -> plan value

    def add_employee(self, employee):
        self.employees.append(employee)

    def distribute_plan(self, month: str):
        if not self.employees:
            return
        per_employee = self.plan.get(month, 0) / len(self.employees)
        for emp in self.employees:
            emp.production[month] = per_employee

# ===== ЗЧИТУВАННЯ/ЗБЕРЕЖЕННЯ ДАНИХ =====
class JsonLoader(IDataLoader):
    def load(self, filepath: str, encoding="utf-8"):
        with open(filepath, 'r', encoding=encoding) as f:
            return json.load(f)

class CsvLoader(IDataLoader):
    def load(self, filepath: str):
        with open(filepath, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            return list(reader)

class JsonSaver(IDataSaver):
    def save(self, filepath: str, data):
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)

class CsvSaver(IDataSaver):
    def save(self, filepath: str, data):
        if data:
            keys = data[0].keys()
            with open(filepath, 'w', newline='') as output_file:
                dict_writer = csv.DictWriter(output_file, keys)
                dict_writer.writeheader()
                dict_writer.writerows(data)

# ===== ГОЛОВНА ПРОГРАМА =====
def main():
    departments = {}
    employees = []

    while True:
        print("\n===== Меню =====")
        print("1. Створити підрозділ")
        print("2. Додати працівника")
        print("3. Задати план підрозділу")
        print("4. Розподілити план")
        print("5. Порахувати зарплати")
        print("6. Зберегти дані (JSON)")
        print("7. Зберегти дані (CSV)")
        print("8. Переглянути працівників")
        print("9. Переглянути підрозділи")
        print("10. Завантажити дані (JSON)")
        print("11. Завантажити дані (CSV)")
        print("12. Вийти")
        choice = input("Ваш вибір: ")

        if choice == '1':
            name = input("Назва підрозділу: ")
            departments[name] = Department(name)
            print(f"Підрозділ {name} створено.")

        elif choice == '2':
            name = input("Ім'я працівника: ")
            position = input("Посада: ")
            dept_name = input("Назва підрозділу: ")
            base_salary = float(input("Базова ставка: "))
            bonus = float(input("Премія: "))

            print("Тип оплати:")
            print("1. Ставка + Премія")
            print("2. % від виробітку + Премія")
            print("3. % виконання плану + Премія")
            scheme_choice = input("Ваш вибір: ")

            if scheme_choice == '1':
                scheme = FixedSalaryWithBonus()
            elif scheme_choice == '2':
                scheme = PercentProductionWithBonus()
            elif scheme_choice == '3':
                scheme = PercentPlanWithBonus()
            else:
                print("Невірний вибір схеми!")
                continue

            department = departments.get(dept_name)
            if department:
                employee = Employee(name, position, department, scheme, base_salary, bonus)
                department.add_employee(employee)
                employees.append(employee)
                print(f"Працівника {name} додано до підрозділу {dept_name}.")
            else:
                print("Підрозділ не знайдено!")

        elif choice == '3':
            dept_name = input("Назва підрозділу: ")
            month = input("Місяць (формат YYYY-MM): ")
            plan = float(input("План виробітку: "))
            department = departments.get(dept_name)
            if department:
                department.plan[month] = plan
                print(f"План для {dept_name} на {month} встановлено.")
            else:
                print("Підрозділ не знайдено!")

        elif choice == '4':
            dept_name = input("Назва підрозділу: ")
            month = input("Місяць (формат YYYY-MM): ")
            department = departments.get(dept_name)
            if department:
                department.distribute_plan(month)
                print(f"План для {dept_name} розподілено на працівників.")
            else:
                print("Підрозділ не знайдено!")

        elif choice == '5':
            month = input("Місяць (формат YYYY-MM): ")
            for emp in employees:
                salary = emp.calculate_salary(month)
                print(f"{emp.name} ({emp.position}) - Зарплата за {month}: {salary:.2f}")

        elif choice == '6':
            filepath = input("Введіть шлях до JSON-файлу: ")
            data = [{
                'name': emp.name,
                'position': emp.position,
                'department': emp.department.name,
                'base_salary': emp.base_salary,
                'bonus': emp.bonus,
                'production': emp.production
            } for emp in employees]
            JsonSaver().save(filepath, data)
            print(f"Дані збережено у {filepath}")

        elif choice == '7':
            filepath = input("Введіть шлях до CSV-файлу: ")
            data = [{
                'name': emp.name,
                'position': emp.position,
                'department': emp.department.name,
                'base_salary': emp.base_salary,
                'bonus': emp.bonus
            } for emp in employees]
            CsvSaver().save(filepath, data)
            print(f"Дані збережено у {filepath}")

        elif choice == '8':
            print("\nСписок працівників:")
            for emp in employees:
                print(f"{emp.name} - {emp.position} ({emp.department.name})")

        elif choice == '9':
            print("\nСписок підрозділів:")
            for dept_name, dept in departments.items():
                print(f"{dept_name} - Кількість працівників: {len(dept.employees)}")

        elif choice == '10':
            filepath = input("Введіть шлях до JSON-файлу: ")
            data = JsonLoader().load(filepath)
            for emp_data in data:
                dept_name = emp_data['department']
                if dept_name not in departments:
                    departments[dept_name] = Department(dept_name)
                scheme = FixedSalaryWithBonus()  # За замовчуванням, можна додати типи
                emp = Employee(
                    emp_data['name'],
                    emp_data['position'],
                    departments[dept_name],
                    scheme,
                    emp_data['base_salary'],
                    emp_data['bonus']
                )
                emp.production = emp_data.get('production', {})
                employees.append(emp)
                departments[dept_name].add_employee(emp)
            print(f"Дані завантажено з {filepath}")

        elif choice == '11':
            filepath = input("Введіть шлях до CSV-файлу: ")
            data = CsvLoader().load(filepath)
            for emp_data in data:
                dept_name = emp_data['department']
                if dept_name not in departments:
                    departments[dept_name] = Department(dept_name)
                scheme = FixedSalaryWithBonus()  # За замовчуванням
                emp = Employee(
                    emp_data['name'],
                    emp_data['position'],
                    departments[dept_name],
                    scheme,
                    float(emp_data['base_salary']),
                    float(emp_data['bonus'])
                )
                employees.append(emp)
                departments[dept_name].add_employee(emp)
            print(f"Дані завантажено з {filepath}")

        elif choice == '12':
            print("Вихід з програми.")
            break

        else:
            print("Невірний вибір! Спробуйте ще раз.")

if __name__ == "__main__":
    main()
