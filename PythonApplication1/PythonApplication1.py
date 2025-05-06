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
    def calculate(self, base: float, bonus, plan: float, actual: float) -> float:
        pass

class IBonusScheme(ABC):
    @abstractmethod
    def calculate_bonus(self, base: float, plan: float, actual: float) -> float:
        pass

class IDataLoader(ABC):
    @abstractmethod
    def load(self, filepath: str):
        pass

class IDataSaver(ABC):
    @abstractmethod
    def save(self, filepath: str, data):
        pass

# ===== СХЕМИ ПРЕМІЮВАННЯ =====
class FixedBonus(IBonusScheme):
    def calculate_bonus(self, base, plan, actual):
        return base  # тут base означає передану "премію" (фіксовану суму)

class PercentOfBaseBonus(IBonusScheme):
    def calculate_bonus(self, base, plan, actual):
        return base * 0.1  # 10% від ставки

class PlanPerformanceBonus(IBonusScheme):
    def calculate_bonus(self, base, plan, actual):
        if plan == 0:
            return 0
        return (actual / plan) * 0.2 * base  # 20% від ставки пропорційно до виконання плану

# ===== СХЕМИ ОПЛАТИ =====
class FixedSalaryWithBonus(IPaymentScheme):
    def calculate(self, base, bonus: IBonusScheme, plan, actual):
        return base + bonus.calculate_bonus(base, plan, actual)

class PercentProductionWithBonus(IPaymentScheme):  #У схемі % від виробітку працівники отримують залежно від кількості виконаних одиниць.
    def calculate(self, base, bonus: IBonusScheme, plan, actual):
        return actual * base + bonus.calculate_bonus(base, plan, actual)

class PercentPlanWithBonus(IPaymentScheme): #У схемі % виконання плану працівники отримують залежно від виконаного плану. 
    def calculate(self, base, bonus: IBonusScheme, plan, actual):
        if plan == 0:
            return bonus.calculate_bonus(base, plan, actual)
        return (actual / plan) * base + bonus.calculate_bonus(base, plan, actual)

# ===== ПРАЦІВНИК =====
class Employee(IEmployee):
    def __init__(self, name, position, department, payment_scheme: IPaymentScheme, bonus_scheme: IBonusScheme, base_salary):
        self.name = name
        self.position = position
        self.department = department
        self.payment_scheme = payment_scheme
        self.bonus_scheme = bonus_scheme
        self.base_salary = base_salary
        self.production = {}  # місяць -> виконання

    def calculate_salary(self, month: str) -> float:
        actual = self.production.get(month, 0)
        plan = self.department.plan.get(month, 0)
        return self.payment_scheme.calculate(self.base_salary, self.bonus_scheme, plan, actual)

class Manager(Employee):
    pass

# ===== ПІДРОЗДІЛ =====
class Department:
    def __init__(self, name, manager=None):
        self.name = name
        self.manager = manager
        self.employees = []
        self.plan = {}

    def add_employee(self, employee):
        self.employees.append(employee)

    def distribute_plan(self, month: str):
        if not self.employees:
            return
        per_employee = self.plan.get(month, 0) / len(self.employees)
        for emp in self.employees:
            emp.production[month] = per_employee

# ===== ЗЧИТУВАННЯ/ЗБЕРЕЖЕННЯ =====
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
        print("6. Зберегти в JSON")  # C:\Users\Miha\source\repos\Питон\Лаба 5 (ООП)\PythonApplication1\дані.json
        print("7. Зберегти в CSV") # C:\Users\Miha\source\repos\Питон\Лаба 5 (ООП)\PythonApplication1\дані.csv
        print("8. Переглянути працівників")
        print("9. Переглянути підрозділи")
        print("10. Завантажити з JSON")
        print("11. Завантажити з CSV")
        print("12. Вийти")
        choice = input("Ваш вибір: ")

        if choice == '1':
            name = input("Назва підрозділу: ")
            departments[name] = Department(name)
            print(f"Підрозділ {name} створено.")

        elif choice == '2':
            name = input("Ім'я працівника: ")
            position = input("Посада: ")
            dept_name = input("Підрозділ: ")
            base_salary = float(input("Базова ставка: "))

            print("Схема премії:")
            print("1. Фіксована сума")
            print("2. 10% від ставки")
            print("3. Від виконання плану (20% від ставки)")
            bonus_choice = input("Ваш вибір: ")

            if bonus_choice == '1':
                bonus_value = float(input("Фіксована сума премії: "))
                bonus_scheme = FixedBonus()
            elif bonus_choice == '2':
                bonus_scheme = PercentOfBaseBonus()
                bonus_value = base_salary
            elif bonus_choice == '3':
                bonus_scheme = PlanPerformanceBonus()
                bonus_value = base_salary
            else:
                print("Невірний вибір премії!")
                continue

            print("Тип оплати:")
            print("1. Ставка + премія")
            print("2. % від виробітку + премія")
            print("3. % виконання плану + премія")
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
                employee = Employee(name, position, department, scheme, bonus_scheme, base_salary)
                department.add_employee(employee)
                employees.append(employee)
                print(f"Працівника {name} додано.")
            else:
                print("Підрозділ не знайдено!")

        elif choice == '3':
            dept_name = input("Назва підрозділу: ")
            month = input("Місяць (YYYY-MM): ")
            plan = float(input("План: "))
            if dept_name in departments:
                departments[dept_name].plan[month] = plan
                print("План збережено.")
            else:
                print("Підрозділ не знайдено.")

        elif choice == '4':
            dept_name = input("Назва підрозділу: ")
            month = input("Місяць (YYYY-MM): ")
            if dept_name in departments:
                departments[dept_name].distribute_plan(month)
                print("План розподілено.")
            else:
                print("Підрозділ не знайдено.")

        elif choice == '5':
            month = input("Місяць (YYYY-MM): ")
            for emp in employees:
                salary = emp.calculate_salary(month)
                print(f"{emp.name} ({emp.position}) — Зарплата за {month}: {salary:.2f}")

        elif choice == '6':
            filepath = input("Шлях до JSON-файлу: ")
            data = [{
                'name': emp.name,
                'position': emp.position,
                'department': emp.department.name,
                'base_salary': emp.base_salary,
                'production': emp.production
            } for emp in employees]
            JsonSaver().save(filepath, data)
            print("Дані збережено.")

        elif choice == '7':
            filepath = input("Шлях до CSV-файлу: ")
            data = [{
                'name': emp.name,
                'position': emp.position,
                'department': emp.department.name,
                'base_salary': emp.base_salary
            } for emp in employees]
            CsvSaver().save(filepath, data)
            print("Дані збережено.")

        elif choice == '8':
            for emp in employees:
                print(f"{emp.name} - {emp.position} ({emp.department.name})")

        elif choice == '9':
            for name, dept in departments.items():
                print(f"{name} - працівників: {len(dept.employees)}")

        elif choice == '10':
            filepath = input("Шлях до JSON: ")
            data = JsonLoader().load(filepath)
            for emp_data in data:
                dept_name = emp_data['department']
                if dept_name not in departments:
                    departments[dept_name] = Department(dept_name)
                scheme = FixedSalaryWithBonus()
                bonus_scheme = FixedBonus()
                emp = Employee(emp_data['name'], emp_data['position'], departments[dept_name],
                               scheme, bonus_scheme, emp_data['base_salary'])
                emp.production = emp_data.get('production', {})
                departments[dept_name].add_employee(emp)
                employees.append(emp)
            print("Дані завантажено.")

        elif choice == '11':
            filepath = input("Шлях до CSV: ")
            data = CsvLoader().load(filepath)
            for emp_data in data:
                dept_name = emp_data['department']
                if dept_name not in departments:
                    departments[dept_name] = Department(dept_name)
                scheme = FixedSalaryWithBonus()
                bonus_scheme = FixedBonus()
                emp = Employee(emp_data['name'], emp_data['position'], departments[dept_name],
                               scheme, bonus_scheme, float(emp_data['base_salary']))
                departments[dept_name].add_employee(emp)
                employees.append(emp)
            print("Дані завантажено.")

        elif choice == '12':
            break
        else:
            print("Невірний вибір!")

if __name__ == "__main__":
    main()
