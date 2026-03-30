from pawpal_system import Pet, Task


def test_mark_complete_changes_status():
    task = Task(name="Walk", category="walk", duration=30, priority="high", frequency=2)
    assert task.is_completed == 0
    assert not task.is_fully_done()

    task.mark_complete()
    assert task.is_completed == 1
    assert not task.is_fully_done()

    task.mark_complete()
    assert task.is_completed == 2
    assert task.is_fully_done()

    # Should not increment past frequency
    task.mark_complete()
    assert task.is_completed == 2


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Bella", species="dog", breed="Labrador", age=4, color="black")
    assert len(pet.tasks) == 0

    pet.add_task(Task(name="Walk", category="walk", duration=30, priority="high"))
    assert len(pet.tasks) == 1

    pet.add_task(Task(name="Feeding", category="feeding", duration=10, priority="medium"))
    assert len(pet.tasks) == 2
