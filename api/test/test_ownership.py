def test_owner_can_read(client, booked):
    r = client.get(
        f"/appointments/{booked['appt'].id}",
        headers={"X-User-Id": str(booked["alice"].id)},
    )
    assert r.status_code == 200


def test_non_owner_cannot_read(client, booked):
    r = client.get(
        f"/appointments/{booked['appt'].id}",
        headers={"X-User-Id": str(booked["ben"].id)},
    )
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "NOT_APPOINTMENT_OWNER"

def test_non_owner_cannot_reschedule(client, booked):
    r = client.patch(
        f"/appointments/{booked['appt'].id}",
        headers={"X-User-Id": str(booked["ben"].id)},
        json={"notes": "hacked"},
    )
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "NOT_APPOINTMENT_OWNER"

def test_write_then_read_as_non_owner(client, booked):
    appt_id = booked["appt"].id
    # Ben's write is rejected
    r = client.patch(
        f"/appointments/{appt_id}",
        headers={"X-User-Id": str(booked["ben"].id)},
        json={"notes": "hacked"},
    )
    assert r.status_code == 403
    # Alice reads it back — the rejected write left no trace
    r = client.get(
        f"/appointments/{appt_id}",
        headers={"X-User-Id": str(booked["alice"].id)},
    )
    assert r.status_code == 200
    assert r.json()["notes"] != "hacked"

def test_non_owner_cannot_book_for_others_pet(client, booked):
    r = client.post(
        "/appointments",
        headers={"X-User-Id": str(booked["ben"].id)},
        json={
            "pet_id": booked["appt"].pet_id,  # Alice's pet
            "clinic_id": booked["appt"].clinic_id,
            "start_time": "2027-01-01T10:00:00Z",
        },
    )
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "NOT_PET_OWNER"