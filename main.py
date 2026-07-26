from datetime import date

from pawpal_system import Frequency, Owner, Pet, Scheduler, Task


def format_12h(hhmm: str) -> str:
    """Render a "HH:MM" 24-hour string as "HH:MM AM/PM" for display."""
    hour, minute = (int(part) for part in hhmm.split(":"))
    period = "AM" if hour < 12 else "PM"
    hour12 = hour % 12 or 12
    return f"{hour12:02d}:{minute:02d} {period}"


def print_tasks(tasks) -> None:
    for task in tasks:
        status = "done" if task.completed else "pending"
        print(f"  {task.dueDate} {format_12h(task.time)} - {task.description} ({status})")


def main() -> None:
    owner = Owner("Sam")

    rex = Pet("Rex", "dog", 3)
    fido = Pet("Fido", "dog", 4)
    whiskers = Pet("Whiskers", "cat", 5)

    owner.addPet(rex)
    owner.addPet(fido)
    owner.addPet(whiskers)

    scheduler = Scheduler(owner)

    today = date(2026, 1, 15)

    # Added out of time-order on purpose, to exercise filter_by_pet / filter_by_status
    # independent of any sorting.
    evening_walk = Task("Evening walk", "18:30", Frequency.DAILY, dueDate=today)
    morning_walk = Task("Morning walk", "07:00", Frequency.DAILY, dueDate=today)
    lunch_feeding = Task("Lunchtime feeding", "12:00", Frequency.DAILY, dueDate=today)
    scheduler.scheduleTask(rex, evening_walk)
    scheduler.scheduleTask(rex, morning_walk)
    scheduler.scheduleTask(rex, lunch_feeding)

    # Vet checkup is due on the last day of January, to also show the
    # month-end rollover (Jan 31 -> Feb 28) once it's completed below.
    vet_checkup = Task("Vet checkup", "16:00", Frequency.MONTHLY, dueDate=date(2026, 1, 31))
    breakfast = Task("Breakfast", "08:00", Frequency.DAILY, dueDate=today)
    litter_cleaning = Task("Litter box cleaning", "13:30", Frequency.DAILY, dueDate=today)
    scheduler.scheduleTask(whiskers, vet_checkup)
    scheduler.scheduleTask(whiskers, breakfast)
    scheduler.scheduleTask(whiskers, litter_cleaning)

    # Intentionally overlapping with Rex's evening walk, to demonstrate conflict detection:
    # same-pet (Rex: walk + meds) and cross-pet (Rex vs. Whiskers) at 6:30 PM today.
    give_meds = Task("Give meds", "18:30", Frequency.DAILY, dueDate=today)
    grooming = Task("Grooming", "18:30", Frequency.WEEKLY, dueDate=today)
    scheduler.scheduleTask(rex, give_meds)
    scheduler.scheduleTask(whiskers, grooming)

    # Fido shares Rex's exact "Evening walk" at the same time - the owner is walking
    # both dogs together, so this pair is exempt from cross-pet conflict detection,
    # even though Fido's walk still conflicts with Whiskers' differently-named Grooming.
    fido_walk = Task("Evening walk", "18:30", Frequency.DAILY, dueDate=today)
    scheduler.scheduleTask(fido, fido_walk)

    print("Today's Schedule (before completing anything)")
    for pet in owner.petList:
        print(f"\n{pet.name} ({pet.species}):")
        print_tasks(scheduler.getTasksByPet(pet))

    print("\nCompleting Morning walk, Breakfast, Litter box cleaning, and Vet checkup...")
    scheduler.complete_task(rex, morning_walk)
    scheduler.complete_task(whiskers, breakfast)
    scheduler.complete_task(whiskers, litter_cleaning)
    scheduler.complete_task(whiskers, vet_checkup)

    print("\nToday's Schedule (after completing - note the auto-scheduled next occurrences)")
    for pet in owner.petList:
        print(f"\n{pet.name} ({pet.species}):")
        print_tasks(scheduler.getTasksByPet(pet))

    print("\nfilter_by_pet(rex):")
    print_tasks(scheduler.filter_by_pet(rex))

    print("\nfilter_by_pet(whiskers):")
    print_tasks(scheduler.filter_by_pet(whiskers))

    print("\nfilter_by_status(completed=True):")
    print_tasks(scheduler.filter_by_status(True))

    print("\nfilter_by_status(completed=False):")
    print_tasks(scheduler.filter_by_status(False))

    print("\nfind_same_pet_conflicts():")
    for pet, task1, task2 in scheduler.find_same_pet_conflicts():
        print(f"  {pet.name}: '{task1.description}' vs '{task2.description}' "
              f"at {format_12h(task1.time)} on {task1.dueDate}")

    print("\nfind_cross_pet_conflicts():")
    for pet1, task1, pet2, task2 in scheduler.find_cross_pet_conflicts():
        print(f"  {pet1.name}'s '{task1.description}' vs {pet2.name}'s '{task2.description}' "
              f"at {format_12h(task1.time)} on {task1.dueDate}")

    print("\nget_conflict_warnings():")
    for warning in scheduler.get_conflict_warnings():
        print(f"  [!] {warning}")


if __name__ == "__main__":
    main()
