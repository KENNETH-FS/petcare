If clinics.owner_id exists, then a pet owner booking an appointment needs to read clinics they don't own. So your ownership rule can't be a blanket "filter everything by current_user.id". It'll be:

Clinics: anyone can read, only the owner can write
Pets / appointments: owner-scoped for both read and write